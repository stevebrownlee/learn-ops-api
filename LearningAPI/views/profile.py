"""View module for handling requests about park areas"""
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount
from LearningAPI.models.people import Cohort, NssUserCohort, NssUser
from LearningAPI.models.coursework import StudentProject
from LearningAPI.models.people.student_personality import StudentPersonality


class Profile(ViewSet):
    """Person can see profile information"""

    def list(self, request):
        """Handle GET requests to profile resource

        Returns:
            Response -- JSON representation of user info
        """
        personality = {}
        cohort = self.request.query_params.get('cohort', None)
        mimic = self.request.query_params.get('mimic', None)

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
                # First time authenticating with Github, so add user to cohort
                cohort_assignment = Cohort.objects.get(pk=cohort)
                usercohort = NssUserCohort()
                usercohort.cohort = cohort_assignment
                usercohort.nss_user = nss_user
                usercohort.save()

                # Assign student to first project in cohort's course
                cohort_first_course = cohort_assignment.courses.get(index=0)
                course_first_book = cohort_first_course.course.books.get(index=0)
                book_first_project = course_first_book.projects.get(index=0)
                student_project = StudentProject()
                student_project.student = nss_user
                student_project.project = book_first_project
                student_project.save()

        try:
            personality = StudentPersonality.objects.get(student=nss_user)
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

        if not request.auth.user.is_staff or mimic:
            serializer = ProfileSerializer(nss_user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            profile = {}
            profile["person"] = {}
            profile["person"]["first_name"] = request.auth.user.first_name
            profile["person"]["last_name"] = request.auth.user.last_name
            profile["person"]["github"] = {}
            profile["person"]["github"]["login"] = person.extra_data["login"]
            profile["person"]["github"]["repos"] = person.extra_data["repos_url"]
            profile["staff"] = request.auth.user.is_staff

            instructor_active_cohort = NssUserCohort.objects.filter(nss_user__user=request.auth.user).first()
            if instructor_active_cohort is not None:
                profile["person"]["active_cohort"] = instructor_active_cohort.cohort.id
            else:
                profile["person"]["active_cohort"] = 0


        return Response(profile)


class PersonalitySerializer(serializers.ModelSerializer):
    """Serializer for a student's personality info"""
    briggs_myers_type = serializers.SerializerMethodField()

    def get_briggs_myers_type(self, obj):
        if obj.briggs_myers_type != '':
            return obj.briggs_myers_type

        return ""
    class Meta:
        model = StudentPersonality
        fields = (
            'briggs_myers_type', 'bfi_extraversion',
            'bfi_agreeableness', 'bfi_conscientiousness',
            'bfi_neuroticism', 'bfi_openness',
        )


class ProfileSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    name = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    repos = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    capstones = serializers.SerializerMethodField()

    def get_staff(self, obj):
        return obj.user.is_staff

    def get_project(self, obj):
        project = StudentProject.objects.filter(student=obj).last()
        if project is not None:
            return {
                "id": project.project.id,
                "name": project.project.name,
                "book_name": project.project.book.name,
            }
        else:
            return {
                "id": 0,
                "name": "Unassigned"
            }


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

    def get_capstones(self, obj):
        student = NssUser.objects.get(user=obj.user)
        capstones = []
        for capstone in student.capstones.all():
            capstones.append({
                "course": capstone.course.name,
                "proposal": capstone.proposal_url,
                "statuses": capstone.statuses.order_by("-id").values('status__status', 'date')
            })
        return capstones

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'project', 'email', 'github', 'staff', 'slack_handle',
                  'current_cohort', 'repos', 'assessment_overview', 'capstones',)
