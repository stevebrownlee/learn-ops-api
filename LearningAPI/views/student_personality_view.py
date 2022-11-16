"""Student view module"""
import statistics
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from LearningAPI.decorators import is_instructor
from LearningAPI.models.people import NssUser, Cohort, DailyStatus, OneOnOneNote
from LearningAPI.models.people.student_personality import StudentPersonality
from LearningAPI.models.skill import CoreSkillRecord, LearningRecordEntry, LearningRecord
from LearningAPI.views.core_skill_record_view import CoreSkillRecordSerializer


class StudentPersonalityViewSet(ModelViewSet):
    """Student viewset"""

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            student = NssUser.objects.get(user=request.auth.user)

            # Get value of `testresult` query parameter
            testresult = request.query_params.get('testresult', None)

            if testresult is not None:
                # Get the corresponding personality from the DB
                personality = StudentPersonality.objects.get(student=student)

                # Update the correct property based on the query parameter and request body value
                if testresult == 'briggs':
                    personality.briggs_myers_type = request.data['value']

                if testresult == 'bfio':
                    personality.bfi_openness = request.data['value']

                if testresult == 'bfic':
                    personality.bfi_conscientiousness = request.data['value']

                if testresult == 'bfie':
                    personality.bfi_extraversion = request.data['value']

                if testresult == 'bfia':
                    personality.bfi_agreeableness = request.data['value']

                if testresult == 'bfin':
                    personality.bfi_neuroticism = request.data['value']

                # Save the personality
                personality.save()


            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except NssUser.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)
