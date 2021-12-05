"""View module for handling requests about park areas"""
from django.contrib.auth.models import User
from django.db.models.fields import BooleanField
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount
from LearningAPI.models import NssUser

class Profile(ViewSet):
    """Person can see profile information"""

    def list(self, request):
        """Handle GET requests to profile resource

        Returns:
            Response -- JSON representation of user info
        """

        #
        #  Discovered how to access social account info at following URL
        #     https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/models.py
        #
        person = SocialAccount.objects.get(user=request.auth.user)

        try:
            NssUser.objects.get(user=request.auth.user)
        except NssUser.DoesNotExist:
            # User has authorized with Github, but NSSUser hasn't been made yet
            nss_user = NssUser.objects.create(
                github_handle=person.extra_data["login"],
                user=request.auth.user
            )
            nss_user.save()


        profile = {}
        profile["person"] = {}
        profile["person"]["first_name"] = request.auth.user.first_name
        profile["person"]["last_name"] = request.auth.user.last_name
        profile["person"]["github"] = {}
        profile["person"]["github"]["login"] = person.extra_data["login"]
        profile["person"]["github"]["repos"] = person.extra_data["repos_url"]

        profile["staff"] = request.auth.user.is_staff

        return Response(profile)
