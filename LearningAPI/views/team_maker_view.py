import os
import requests

from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from LearningAPI.models.people import StudentTeam, GroupProjectRepository, NSSUserTeam, NssUser


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

        # Create the student team in the database
        team = StudentTeam()
        team.group_name = ""
        team.cohort_id = cohort_id
        team.sprint_team = True if group_project_id is not None else False
        team.save()


        # Assign the students to the team
        for student in student_list:
            student_team = NSSUserTeam()
            student_team.student_id = student
            student_team.team = team
            student_team.save()

        # Create group project repository if group project is not None
        if group_project_id is not None:
            group_project_repo = GroupProjectRepository()
            group_project_repo.team_id = team.id
            group_project_repo.project_id = group_project_id
            group_project_repo.save()

        serialized_team = StudentTeamSerializer(team, many=False).data
        return Response(serialized_team, status=status.HTTP_201_CREATED)


