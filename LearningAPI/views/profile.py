"""View module for handling requests about park areas"""
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount
from LearningAPI.models.people import Cohort, NssUserCohort, NssUser, nssuser
from LearningAPI.models.people.student_personality import StudentPersonality
from LearningAPI.views.student_view import SingleStudent, StudentNoteSerializer




class Profile(ViewSet):
    """Person can see profile information"""

    def list(self, request):
        """Handle GET requests to profile resource

        Returns:
            Response -- JSON representation of user info
        """
        personality = {}
        cohort = self.request.query_params.get('cohort', None)

        #
        #  Discovered how to access social account info at following URL
        #     https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/models.py
        #
        try:
            person = SocialAccount.objects.get(user=request.auth.user)
        except SocialAccount.DoesNotExist as ex:
            raise ex

        try:
            nss_user = NssUser.objects.get(user=request.auth.user)

        except NssUser.DoesNotExist:
            # User has authorized with Github, but NSSUser hasn't been made yet
            nss_user = NssUser.objects.create(
                github_handle=person.extra_data["login"],
                user=request.auth.user
            )
            nss_user.save()

            if cohort is not None:
                coh = Cohort.objects.get(name=cohort)
                usercohort = NssUserCohort()
                usercohort.cohort = coh
                usercohort.nss_user = nss_user
                usercohort.save()

        try:
            StudentPersonality.objects.get(student=nss_user)
        except StudentPersonality.DoesNotExist:
            personality = StudentPersonality()
            personality.briggs_myers_type = ""
            personality.bfi_extraversion = 0
            personality.bfi_agreeableness = 0
            personality.bfi_conscientiousness = 0
            personality.bfi_neuroticism = 0
            personality.bfi_openness = 0
            personality.student = nss_user
            personality.save()

        if request.auth.user.is_staff is False:
            serializer = ProfileSerializer(nss_user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            profile = {}
            profile["person"] = {}
            profile["person"]["first_name"] = request.auth.user.first_name
            profile["person"]["last_name"] = request.auth.user.last_name
            profile["person"]["github"] = {}
            profile["person"]["personality"] = personality
            profile["person"]["github"]["login"] = person.extra_data["login"]
            profile["person"]["github"]["repos"] = person.extra_data["repos_url"]
            profile["staff"] = request.auth.user.is_staff

        return Response(profile)


class PersonalitySerializer(serializers.ModelSerializer):
    """Serializer for a student's personality info"""
    class Meta:
        model = StudentPersonality
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    personality = PersonalitySerializer(many=False)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    repos = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()

    def get_staff(self, obj):
        return obj.user.is_staff

    def get_github(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["login"]

    def get_repos(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["repos_url"]

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'github', 'staff', 'slack_handle',
                  'cohorts', 'feedback', 'repos', 'personality')

