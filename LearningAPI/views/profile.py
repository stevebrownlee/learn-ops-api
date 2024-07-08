"""View module for handling requests about park areas"""
import logging
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount

from LearningAPI.utils import GithubRequest
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

                # Add student's github account as a member of the cohort Github organization
                gh_request = GithubRequest()
                student_org_name = cohort_assignment.info.student_organization_url.split("/")[-1]
                request_url = f'https://api.github.com/orgs/{student_org_name}/memberships/{person.extra_data["login"]}'
                data = {"role": "member"}
                response = gh_request.put(request_url, data)
                if response.status_code != 200:
                    logger = logging.getLogger("LearningPlatform")
                    logger.warning("Error adding %s to %s organization", person.extra_data['login'], student_org_name)

                # Assign student to first project in cohort's course
                cohort_first_course = cohort_assignment.courses.get(index=0)
                course_first_book = cohort_first_course.course.books.get(index=0)
                book_first_project = course_first_book.projects.get(index=0)
                student_project = StudentProject()
                student_project.student = nss_user
                student_project.project = book_first_project
                student_project.save()



        if not request.auth.user.is_staff or mimic:
            student_cohort = nss_user.assigned_cohorts.first()
            if not student_cohort.is_github_org_member:
                # Send a request to the Github API to check the membership status of the user for the cohort Github organization
                gh_request = GithubRequest()
                student_org_name = student_cohort.cohort.info.student_organization_url.split("/")[-1]
                request_url = f'https://api.github.com/orgs/{student_org_name}/memberships/{person.extra_data["login"]}'
                response = gh_request.get(request_url).json()
                github_org_membership_status = response.get("state", None)

                if github_org_membership_status == "active":
                    student_cohort.is_github_org_member = True
                    student_cohort.save()
            else:
                github_org_membership_status = "active"


            serializer = ProfileSerializer(nss_user, context={'request': request, 'github_status': github_org_membership_status})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create custom JSON response for instructors
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


class ProfileSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    name = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    repos = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    capstones = serializers.SerializerMethodField()
    github_org_status = serializers.SerializerMethodField()

    def get_github_org_status(self, obj):
        return self.context['github_status']

    def get_staff(self, obj):
        return obj.user.is_staff

    def get_project(self, obj):
        project = StudentProject.objects.filter(student=obj).last()
        if project is not None:
            return {
                "id": project.project.id,
                "name": project.project.name,
                "book_name": project.project.book.name,
                "book_id": project.project.book.id,
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
                  'current_cohort', 'repos', 'assessment_overview', 'capstones',
                  'github_org_status')
