""" This module contains the view for the student note type model """
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from LearningAPI.models.people import StudentNoteType


class StudentNoteTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = StudentNoteType
        fields = '__all__'

class StudentNoteTypeViewSet(ModelViewSet):
    """
    A viewset for viewing and editing student note types
    """
    queryset = StudentNoteType.objects.all()
    serializer_class = StudentNoteTypeSerializer
    permission_classes = [IsAdminUser]
