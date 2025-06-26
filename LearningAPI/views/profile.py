"""View module for handling requests about park areas"""
import logging
from django.contrib.auth.models import Group
from rest_framework.decorators import action
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount

from LearningAPI.utils import GithubRequest
from LearningAPI.models.people import Cohort, NssUserCohort, NssUser
from LearningAPI.models.coursework import StudentProject, Project
from LearningAPI.utils import get_logger, bind_request_context, log_action

logger = get_logger("LearningAPI.profile")

class Profile(ViewSet):
    """Person can see profile information"""

    @action(detail=False, methods=['put'])
    def change(self, request):
        """Handle PUT requests to profile resource

        Returns:
            Response -- None
        """
        first = request.data.get("firstName", None)
        last = request.data.get("lastName", None)

        if first is not None and last is not None:
            request.auth.user.first_name = first
            request.auth.user.last_name = last

            request.auth.user.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'You must provide a \'firstName\' and \'lastName\' in the request body'}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """Handle GET requests to profile resource

        Returns:
            Response -- JSON representation of user info
        """
        cohort = self.request.query_params.get('cohort', None)
        role = self.request.query_params.get('role', None)
        mimic = self.request.query_params.get('mimic', None)

        req_logger = bind_request_context(logger, request)
        req_logger.info("Profile list request received", cohort=cohort, role=role, mimic=mimic)

        #
        #  Discovered how to access social account info at following URL
        #     https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/models.py
        #
        try:
            person = SocialAccount.objects.get(user=request.auth.user)
            req_logger.info("Social account found", user=person.user.username, provider=person.provider)
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
            req_logger.info("NssUser created", user=nss_user.user.username)

            # If role is not None, then this user is a staff member and gets the Staff group added to them
            if role is not None:
                # Toggle is_staff to True
                nss_user.user.is_staff = True
                nss_user.user.save()

                # Add user to Staff group
                staff = Group.objects.get(name='Staff')
                staff.user_set.add(nss_user.user)
                req_logger.info("User added to Staff group", user=nss_user.user.username)

            if cohort is not None:
                # First time authenticating with Github, so add user to cohort
                cohort_assignment = Cohort.objects.get(pk=cohort)
                req_logger.info("Cohort found", cohort=cohort_assignment.name)

                usercohort = NssUserCohort()
                usercohort.cohort = cohort_assignment
                usercohort.nss_user = nss_user
                usercohort.save()
                req_logger.info("NssUserCohort created", nss_user=nss_user.user.username, cohort=cohort_assignment.name)

                # Add student's github account as a member of the cohort Github organization
                gh_request = GithubRequest()
                student_org_name = cohort_assignment.info.student_organization_url.split("/")[-1]
                request_url = f'https://api.github.com/orgs/{student_org_name}/memberships/{person.extra_data["login"]}'
                data = {"role": "member"}
                response = gh_request.put(request_url, data)

                if response.status_code != 200:
                    req_logger.error("Failed to add user to cohort Github organization", user=nss_user.user.username, status=response.status_code)
                    return Response(
                        {"error": "Failed to add user to cohort Github organization."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                # Assign student to first project in cohort's course
                try:
                    cohort_first_course = cohort_assignment.courses.get(index=0)
                    course_first_book = cohort_first_course.course.books.get(index=0)
                    book_first_project = course_first_book.projects.get(index=0)
                    req_logger.info("First project found for cohort's course", project=book_first_project.name)

                    student_project = StudentProject()
                    student_project.student = nss_user
                    student_project.project = book_first_project
                    student_project.save()
                    req_logger.info("StudentProject created", student=nss_user.user.username, project=book_first_project.name)

                except Project.DoesNotExist:
                    req_logger.warning("No first project found for cohort's course", cohort=cohort_assignment.name)
                    return Response(
                        {"error": "No first project found for the cohort's course."},
                        status=status.HTTP_404_NOT_FOUND
                    )

        if not request.auth.user.is_staff or mimic:
            # Check to see if the learner has accepted the invitation to join the cohort Github organization
            student_cohort = nss_user.assigned_cohorts.first()
            req_logger.info("Assigned cohort found", cohort=student_cohort.cohort.name if student_cohort else "None")

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
                    req_logger.info("Github organization membership status updated", user=nss_user.user.username, status=github_org_membership_status)
            else:
                github_org_membership_status = "active"


            serializer = ProfileSerializer(
                nss_user,
                context={
                    'request': request,
                    'github_status': github_org_membership_status
                }
            )
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
            profile["instructor"] = nss_user.is_instructor
            req_logger.info("Instructor profile requested", user=request.auth.user.username)

            instructor_active_cohort = NssUserCohort.objects.filter(nss_user__user=request.auth.user).first()
            req_logger.info("Instructor active cohort found", cohort=instructor_active_cohort.cohort.name if instructor_active_cohort else "None")

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
    instructor = serializers.SerializerMethodField()
    capstones = serializers.SerializerMethodField()
    github_org_status = serializers.SerializerMethodField()

    def get_github_org_status(self, obj):
        return self.context['github_status']

    def get_staff(self, obj):
        return obj.user.is_staff

    def get_instructor(self, obj):
        user = NssUser.objects.get(user=obj.user)
        return user.is_instructor

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
                  'github_org_status', 'instructor')
