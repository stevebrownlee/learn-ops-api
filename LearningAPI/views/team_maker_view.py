import logging

from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from LearningAPI.models.people import StudentTeam, GroupProjectRepository, NSSUserTeam, Cohort
from LearningAPI.models.coursework import Project

from LearningAPI.utils import GithubRequest, SlackChannel
from LearningAPI.views.notify import slack_notify
import random, string


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
        slack_channel = SlackChannel(f"{team_prefix}-{team_index}")
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

            # Create the Github repository for the group project
            gh_request = GithubRequest()
            client_full_url = project.client_template_url

            # Split the full URL on '/' and get the last two items
            ( org, repo, ) = client_full_url.split('/')[-2:]

            # Construct request body for creating the repository
            student_org_name = cohort.info.student_organization_url.split("/")[-1]

            # Replace all spaces in the assessment name with hyphens
            random_suffix = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
            repo_name = f'{project.name.replace(" ", "-")}-{random_suffix}'

            request_body = {
                "owner": student_org_name,
                "name": repo_name,
                "description": f"This is your client-side repository for the {project.name} sprint(s).",
                "include_all_branches": False,
                "private": False
            }

            # Create the repository
            response = gh_request.post(url=f'https://api.github.com/repos/{org}/{repo}/generate',data=request_body)

            # Assign the student write permissions to the repository
            request_body = { "permission":"write" }

            for student in team.students.all():
                response = gh_request.put(
                    url=f'https://api.github.com/repos/{student_org_name}/{repo_name}/collaborators/{student.github_handle}',
                    data=request_body
                )
                if response.status_code != 204:
                    logger = logging.getLogger("LearningPlatform")
                    logger.exception(f"Error: {student.full_name} was not added as a collaborator to the assessment repository.")

            # Send message to student
            created_repo_url = f'https://github.com/{student_org_name}/{repo_name}'
            slack_notify(
                f"🐙 Your client repository has been created. Visit the URL below and clone the project to your machine.\n\n{created_repo_url}",
                team.slack_channel
            )

        serialized_team = StudentTeamSerializer(team, many=False).data

        return Response(serialized_team, status=status.HTTP_201_CREATED)
