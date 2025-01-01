import random, string, json, valkey

from django.conf import settings

from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from LearningAPI.models.people import StudentTeam, GroupProjectRepository, NSSUserTeam, Cohort
from LearningAPI.models.coursework import Project
from LearningAPI.utils import GithubRequest, SlackAPI


valkey_client = valkey.Valkey(
    host=settings.VALKEY_CONFIG['HOST'],
    port=settings.VALKEY_CONFIG['PORT'],
    db=settings.VALKEY_CONFIG['DB'],
)

class TeamRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupProjectRepository
        fields = ( 'id', 'project', 'repository' )


class StudentTeamSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    repositories = TeamRepoSerializer(many=True)

    def get_students(self, obj):
        return [{'id': student.id, 'name': student.name} for student in obj.students.all() if not student.user.is_staff]

    class Meta:
        model = StudentTeam
        fields = ( 'group_name', 'cohort', 'sprint_team', 'students', 'repositories' )


class TeamMakerView(ViewSet):
    """Team Maker"""
    def list(self, request):
        cohort_id = request.query_params.get('cohort', None)

        try:
            cohort = Cohort.objects.get(pk=cohort_id)
            teams = StudentTeam.objects.filter(cohort=cohort).order_by('-pk')

            response = StudentTeamSerializer(teams, many=True).data
            return Response(response, status=status.HTTP_200_OK)
        except Cohort.DoesNotExist as ex:
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        cohort_id = request.data.get('cohort', None)
        student_list = request.data.get('students', None)
        group_project_id = request.data.get('groupProject', None)
        team_prefix = request.data.get('weeklyPrefix', None)
        team_index = request.data.get('teamIndex', None)

        issue_target_repos = []

        # Create the student team in the database
        cohort = Cohort.objects.get(pk=cohort_id)
        team = StudentTeam()
        team.group_name = ""
        team.cohort = cohort
        team.sprint_team = group_project_id is not None

        # Create the Slack channel and add students to it and store the channel ID in the team
        # The cohort name will always end in a number. Split on the space and get the last item
        slack = SlackAPI()
        random_team_suffix = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        channel_name = f"{team_prefix}-{cohort.name.split(' ')[-1]}-{random_team_suffix}"
        team.slack_channel = slack.create_channel(channel_name, student_list)
        team.save()

        # Assign the students to the team. Use a for loop with enumerate to get the index of the student
        for student in student_list:
            student_team = NSSUserTeam()
            student_team.student_id = student
            student_team.team = team
            student_team.save()

        # Create group project repository if group project is not None
        if group_project_id is not None:
            project = Project.objects.get(pk=group_project_id)

            # Get student Github organization name
            student_org_name = cohort.info.student_organization_url.split("/")[-1]

            # Replace all spaces in the assessment name with hyphens
            random_suffix = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
            repo_name = f'{project.name.replace(" ", "-")}-client-{random_suffix}'

            # Create the client repository for the group project
            gh_request = GithubRequest()

            response = gh_request.create_repository(
                source_url=project.client_template_url,
                student_org_url=cohort.info.student_organization_url,
                repo_name=repo_name,
                project_name=project.name
            )

            if response.status_code != 201:
                return Response({'message': 'Failed to create repository'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            # Grant write permissions to the students
            for student in team.students.all():
                gh_request.assign_student_permissions(
                    student_org_name=student_org_name,
                    repo_name=repo_name,
                    student=student
                )

            # Save the team's client-side repository URL to the database
            group_project_repo = GroupProjectRepository()
            group_project_repo.team_id = team.id
            group_project_repo.project = project
            group_project_repo.repository = f'https://github.com/{student_org_name}/{repo_name}'
            group_project_repo.save()

            issue_target_repos.append(f'{student_org_name}/{repo_name}')

            # Send message to project team's Slack channel with the repository URL
            created_repo_url = f'https://github.com/{student_org_name}/{repo_name}'
            slack.send_message(
                text=f"🐙 Your client repository has been created. Visit the URL below and clone the project to your machine.\n\n{created_repo_url}",
                channel=team.slack_channel
            )

            # Create the API repository for the group project if it exists
            if project.api_template_url:
                api_repo_name = f'{project.name.replace(" ", "-")}-api-{random_suffix}'

                gh_request.create_repository(
                    source_url=project.api_template_url,
                    student_org_url=cohort.info.student_organization_url,
                    repo_name=api_repo_name,
                    project_name=project.name
                )

                # Grant write permissions to the students
                for student in team.students.all():
                    gh_request.assign_student_permissions(
                        student_org_name=student_org_name,
                        repo_name=api_repo_name,
                        student=student
                    )

                # Save the team's API repository URL to the database
                group_project_repo = GroupProjectRepository()
                group_project_repo.team_id = team.id
                group_project_repo.project = project
                group_project_repo.repository = f'https://github.com/{student_org_name}/{api_repo_name}'
                group_project_repo.save()

                # Send message to project team's Slack channel with the repository URL
                created_repo_url = f'https://github.com/{student_org_name}/{api_repo_name}'
                slack.send_message(
                    text=f"🐙 Your API repository has been created. Visit the URL below and clone the project to your machine.\n\n{created_repo_url}",
                    channel=team.slack_channel
                )

        serialized_team = StudentTeamSerializer(team, many=False).data

        # Publish a message to the channel_migrate_issue_tickets channel on redis to start migrating tickets
        message = json.dumps({
            'notification_channel': cohort.slack_channel,
            'source_repo': "/".join(project.client_template_url.split('/')[-2:]),
            'all_target_repositories': issue_target_repos
        })
        valkey_client.publish('channel_migrate_issue_tickets', message)

        return Response(serialized_team, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def reset(self, request):
        cohort_id = request.query_params.get('cohort', None)

        if cohort_id is None:
            return Response({'message': 'No cohort ID provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cohort = Cohort.objects.get(pk=cohort_id)
            self._delete_slack_channels(cohort)
            self._delete_cohort_teams(cohort)
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Cohort.DoesNotExist as ex:
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _delete_cohort_teams(self, cohort):
        NSSUserTeam.objects.filter(team__cohort=cohort).delete()
        GroupProjectRepository.objects.filter(team__cohort=cohort).delete()
        StudentTeam.objects.filter(cohort=cohort).delete()

    def _delete_slack_channels(self, cohort):
        current_teams = StudentTeam.objects.filter(cohort=cohort)

        for team in current_teams:
            slack = SlackAPI()
            slack.delete_channel(team.slack_channel)

