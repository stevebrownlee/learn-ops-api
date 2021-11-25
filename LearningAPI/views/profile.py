"""View module for handling requests about park areas"""
from django.contrib.auth.models import User
from django.db.models.fields import BooleanField
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from LearningAPI.models import NssUser

class Profile(ViewSet):
    """Person can see profile information"""

    def list(self, request):
        """Handle GET requests to profile resource

        Returns:
            Response -- JSON representation of user info and events
        """
        person = NssUser.objects.get(user=request.auth.user)

        profile = {}
        profile["person"] = {}
        profile["person"]["first_name"] = request.auth.user.first_name
        profile["person"]["last_name"] = request.auth.user.last_name
        profile["staff"] = request.auth.user.is_staff

        return Response(profile)
