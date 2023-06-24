from django.db.models import Count, Q
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from ..models.people import Cohort, NssUser, NssUserCohort, CohortInfo
from ..models.coursework import CohortCourse, Course, Project, StudentProject


class CohortPermission(permissions.BasePermission):
    """Cohort permissions"""

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'destroy', 'assign', 'migrate']:
            return request.auth.user.is_staff
        elif view.action in ['retrieve', 'list']:
            return True
        else:
            return False


class CohortViewSet(ViewSet):
    """Cohort view set"""

    permission_classes = (CohortPermission,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        client_side = request.data.get('clientSide', None)
        server_side = request.data.get('serverSide', None)
        if client_side is None or server_side is None:
            return Response({"reason": "Please choose both courses for this cohort."}, status=status.HTTP_400_BAD_REQUEST)

        cohort = Cohort()
        cohort.name = request.data["name"]
        cohort.slack_channel = request.data["slackChannel"]
        cohort.start_date = request.data["startDate"]
        cohort.end_date = request.data["endDate"]
        cohort.break_start_date = '2022-01-01'
        cohort.break_end_date = '2022-01-01'

        try:
            cohort.save()

            # Assign client side course
            cohort_course_client = CohortCourse()
            course_instance = Course.objects.get(pk=client_side)
            cohort_course_client.course = course_instance
            cohort_course_client.cohort = cohort
            cohort_course_client.active = True
            cohort_course_client.index = 0
            cohort_course_client.save()

            # Assign server side course
            cohort_course_server = CohortCourse()
            course_instance = Course.objects.get(pk=server_side)
            cohort_course_server.course = course_instance
            cohort_course_server.cohort = cohort
            cohort_course_server.active = False
            cohort_course_server.index = 1
            cohort_course_server.save()

            serializer = CohortSerializer(cohort, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError as ex:
            if "cohort_name_key" in ex.args[0]:
                return Response({"reason": "Duplicate cohort name."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"reason": "Duplicate cohort Slack channel."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            cohort = Cohort.objects.annotate(
                students=Count(
                    'members',
                    filter=Q(members__nss_user__user__is_staff=False)
                )
            ).get(pk=pk)

            serializer = CohortSerializer(cohort, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            cohort = Cohort.objects.get(pk=pk)
            cohort.name = request.data["name"]
            cohort.slack_channel = request.data["slack_channel"]
            cohort.start_date = request.data["start_date"]
            cohort.end_date = request.data["end_date"]
            cohort.break_start_date = request.data["break_start_date"]
            cohort.break_end_date = request.data["break_end_date"]

            cohort.save()
        except Cohort.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 204, 404, or 500 status code
        """
        try:
            cohort = Cohort.objects.get(pk=pk)
            cohort.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Cohort.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            cohorts = Cohort.objects.all()

            # Fuzzy search on `q` param present
            search_terms = self.request.query_params.get('q', None)
            limit = self.request.query_params.get('limit', None)

            if search_terms is not None:
                for letter in list(search_terms):
                    cohorts = cohorts.filter(name__icontains=letter)

                serializer = MiniCohortSerializer(cohorts, many=True, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            cohorts = cohorts.annotate(
                students=Count('members', filter=Q(
                    members__nss_user__user__is_staff=False)),
                is_instructor=Count('members', filter=Q(
                    members__nss_user__user=request.auth.user)),
            ).all().order_by('-pk')

            if limit is not None:
                cohorts = cohorts.order_by("-start_date")[0:int(limit)]

            serializer = CohortSerializer(
                cohorts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=['put', ], detail=True)
    def migrate(self, request, pk):
        """Migrate all students in a cohort from client side to server side

        1. Assign all students in cohort to first book of chosen server-side course
        """

        if request.method == "PUT":
            try:
                client_side_course = CohortCourse.objects.get(
                cohort__id=pk, active=True)
            except CohortCourse.DoesNotExist:
                return Response({
                    'reason': 'Could not find an active client side course for this cohort'
                }, status=status.HTTP_404_NOT_FOUND)

            try:
                server_side_course = CohortCourse.objects.get(
                    cohort__id=pk, active=False)
            except CohortCourse.DoesNotExist:
                return Response({
                    'reason': 'Could not find an inactive server side course for this cohort'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get first project of server side course
            try:
                first_project = Project.objects.get(
                    book__course=server_side_course.course, book__index=0, index=0)
            except Project.DoesNotExist:
                return Response({
                    'reason': 'Could not find a singular project in the first book of server side'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get all students in cohort
            try:
                cohort = Cohort.objects.get(pk=pk)
            except Cohort.DoesNotExist:
                return Response({
                    'reason': 'Cohort does not exist'
                }, status=status.HTTP_404_NOT_FOUND)

            cohort_students = NssUser.objects.filter(
                user__is_active=True, user__is_staff=False, assigned_cohorts__cohort=cohort)

            # Create record in student project
            for student in cohort_students:
                student_project = StudentProject()
                student_project.student = student
                student_project.project = first_project

                try:
                    student_project.save()
                except IntegrityError:
                    existing = StudentProject.objects.get(student=student, project=first_project)
                    existing.delete()
                    student_project.save()


            # Deactivate client side course
            client_side_course.active = False
            client_side_course.save()

            # Active server side course
            server_side_course.active = True
            server_side_course.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def assign(self, request, pk):
        """Assign student or instructor to an existing cohort"""

        if request.method == "POST":
            cohort = None
            member = None
            user_type = request.query_params.get("userType", None)

            try:

                if user_type is not None and user_type == "instructor":
                    try:
                        member = NssUser.objects.get(user=request.auth.user)
                        membership = NssUserCohort.objects.get(nss_user=member)

                        return Response(
                            {'message': f'Instructor cannot be in more than 1 cohort at a time. Currently assigned to cohort {membership.cohort.name}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except NssUserCohort.DoesNotExist:
                        pass

                else:
                    user_id = int(request.data["person_id"])
                    member = NssUser.objects.get(pk=user_id)

                cohort = Cohort.objects.get(pk=pk)
                NssUserCohort.objects.get(cohort=cohort, nss_user=member)

                return Response(
                    {'message': 'Person is already assigned to cohort'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except NssUserCohort.DoesNotExist:
                relationship = NssUserCohort()
                relationship.cohort = cohort
                relationship.nss_user = member
                relationship.save()

            except Cohort.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response({'message': 'User assigned to cohort'}, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            user_type = request.query_params.get("userType", None)

            if user_type is not None and user_type == "instructor":
                member = NssUser.objects.get(user=request.auth.user)
            else:
                user_id = int(request.data["student_id"])
                member = NssUser.objects.get(pk=user_id)

            try:
                cohort = Cohort.objects.get(pk=pk)
                rel = NssUserCohort.objects.get(cohort=cohort, nss_user=member)
                rel.delete()

                return Response(None, status=status.HTTP_204_NO_CONTENT)

            except Cohort.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except NssUserCohort.DoesNotExist as ex:
                return Response({'message': "Student is not assigned to that cohort."}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class MiniCohortSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Cohort
        fields = ('id', 'name')


class CohortCourseSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = CohortCourse
        fields = ('id', 'course', 'active', 'index', )
        depth = 1

class CohortSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    courses = CohortCourseSerializer(many=True)
    attendance_sheet_url = serializers.SerializerMethodField()
    student_organization_url = serializers.SerializerMethodField()
    github_classroom_url = serializers.SerializerMethodField()

    def get_student_organization_url(self, obj):
        try:
            return obj.info.student_organization_url
        except Exception as ex:
            return ""

    def get_github_classroom_url(self, obj):
        try:
            return obj.info.github_classroom_url
        except Exception as ex:
            return ""

    def get_attendance_sheet_url(self, obj):
        try:
            return obj.info.attendance_sheet_url
        except Exception as ex:
            return ""

    class Meta:
        model = Cohort
        fields = (
            'id', 'name', 'slack_channel', 'start_date', 'end_date',
            'coaches', 'break_start_date', 'break_end_date', 'students',
            'is_instructor', 'courses', 'info', 'student_organization_url',
            'github_classroom_url', 'attendance_sheet_url'
        )
