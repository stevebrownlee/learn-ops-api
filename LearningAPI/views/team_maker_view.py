import random, string

from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from LearningAPI.models.people import StudentTeam, GroupProjectRepository, NSSUserTeam, Cohort
from LearningAPI.models.coursework import Project
from LearningAPI.utils import GithubRequest, SlackAPI


class StudentTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTeam
        fields = ( 'group_name', 'cohort', 'sprint_team', 'students' )


class TeamMakerView(ViewSet):
    """Team Maker"""
    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        slack = SlackAPI()

        cohort_id = request.data.get('cohort', None)
        student_list = request.data.get('students', None)
        group_project_id = request.data.get('groupProject', None)
        team_prefix = request.data.get('weeklyPrefix', None)
        team_index = request.data.get('teamIndex', None)

        # Create the student team in the database
        cohort = Cohort.objects.get(pk=cohort_id)
        team = StudentTeam()
        team.group_name = ""
        team.cohort = cohort
        team.sprint_team = True if group_project_id is not None else False

        # Create the Slack channel and add students to it and store the channel ID in the team
        slack_channel = slack.create_channel(f"{team_prefix}-{team_index}")
        created_channel_id = slack_channel.create(student_list)
        team.slack_channel = created_channel_id
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
            group_project_repo = GroupProjectRepository()
            group_project_repo.team_id = team.id
            group_project_repo.project = project
            group_project_repo.save()

            # Get student Github organization name
            student_org_name = cohort.info.student_organization_url.split("/")[-1]

            # Replace all spaces in the assessment name with hyphens
            random_suffix = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
            repo_name = f'{project.name.replace(" ", "-")}-{random_suffix}'

            # Create the client repository for the group project
            gh_request = GithubRequest()

            gh_request.create_repository(
                source_url=project.client_template_url,
                student_org_url=cohort.info.student_organization_url,
                repo_name=repo_name,
                project_name=project.name
            )

            # Grant write permissions to the students
            for student in team.students.all():
                gh_request.assign_student_permissions(
                    student_org_name=student_org_name,
                    repo_name=repo_name,
                    student=student
                )

            # Send message to student
            created_repo_url = f'https://github.com/{student_org_name}/{repo_name}'
            slack.send_message(
                text=f"🐙 Your client repository has been created. Visit the URL below and clone the project to your machine.\n\n{created_repo_url}",
                channel=team.slack_channel
            )

        serialized_team = StudentTeamSerializer(team, many=False).data

        return Response(serialized_team, status=status.HTTP_201_CREATED)
