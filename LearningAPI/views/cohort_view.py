from django.db.models import Count, Q
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.people import Cohort, NssUser, NssUserCohort, CohortInfo
from LearningAPI.models.coursework import CohortCourse, Course, Project, StudentProject
from LearningAPI.utils import get_logger, bind_request_context, log_action

logger = get_logger("LearningAPI.cohort")

class CohortPermission(permissions.BasePermission):
    """Cohort permissions"""

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'destroy', 'assign', 'migrate', 'active']:
            return request.auth.user.is_staff
        elif view.action in ['retrieve', 'list']:
            return True
        else:
            return False


class CohortViewSet(ViewSet):
    """Cohort view set"""

    permission_classes = (CohortPermission,)

    @log_action("cohort_creation")
    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        client_side = request.data.get('clientSide', None)
        server_side = request.data.get('serverSide', None)
        if client_side is None or server_side is None:
            return Response({"reason": "Please choose both courses for this cohort."}, status=status.HTTP_400_BAD_REQUEST)


        try:
            cohort = Cohort()
            cohort.name = request.data["name"]
            cohort.slack_channel = request.data["slackChannel"]
            cohort.start_date = request.data["startDate"]
            cohort.end_date = request.data["endDate"]
            cohort.break_start_date = '2022-01-01'
            cohort.break_end_date = '2022-01-01'
            cohort.save()
        except IntegrityError as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assign client side course
            cohort_course_client = CohortCourse()
            course_instance = Course.objects.get(pk=client_side)
            cohort_course_client.course = course_instance
            cohort_course_client.cohort = cohort
            cohort_course_client.active = True
            cohort_course_client.index = 0
            cohort_course_client.save()
        except IntegrityError:
            pass

        try:
            # Assign server side course
            cohort_course_server = CohortCourse()
            course_instance = Course.objects.get(pk=server_side)
            cohort_course_server.course = course_instance
            cohort_course_server.cohort = cohort
            cohort_course_server.active = False
            cohort_course_server.index = 1
            cohort_course_server.save()
        except IntegrityError:
            pass

        try:
            # Create matching cohort info
            cohort_info = CohortInfo()
            cohort_info.cohort = cohort
            cohort_info.student_organization_url = request.data.get('orgURL', None)
            cohort_info.save()
        except IntegrityError as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CohortSerializer(cohort, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @log_action("cohort_retrieval")
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

    @log_action("cohort_update")
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

            cohort.save()
        except Cohort.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @log_action("cohort_deletion")
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

    @log_action("cohort_list")
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
            active = self.request.query_params.get('active', None)

            if active == 'true':
                cohorts = cohorts.filter(active=True)

            if search_terms is not None:
                for letter in list(search_terms):
                    cohorts = cohorts.filter(name__icontains=letter)

                serializer = MiniCohortSerializer(cohorts, many=True, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            cohorts = cohorts\
                .annotate(
                    students=Count('members', filter=Q(members__nss_user__user__is_staff=False)),
                    is_instructor=Count('members', filter=Q(members__nss_user__user=request.auth.user))
                )\
                .all()\
                .order_by('pk')

            if limit is not None:
                cohorts = cohorts.order_by("-start_date")[0:int(limit)]

            serializer = CohortSerializer(
                cohorts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @log_action("cohort_active_toggle")
    @action(methods=['put', ], detail=True)
    def active(self, request, pk):
        if request.method == "PUT":
            cohort = Cohort.objects.get(pk=pk)
            cohort.active = request.data.get('active', True)
            cohort.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

    @log_action("cohort_migration")
    @action(methods=['put', ], detail=True)
    def migrate(self, request, pk):
        """Migrate all students in a cohort from client side to server side

        1. Assign all students in cohort to first book of chosen server-side course
        """

        if request.method == "PUT":
            try:
                client_side_course = CohortCourse.objects.get(
                    cohort__id=pk,
                    active=True
                )
            except CohortCourse.DoesNotExist:
                return Response({
                    'reason': 'Could not find an active client side course for this cohort'
                }, status=status.HTTP_404_NOT_FOUND)

            try:
                server_side_course = CohortCourse.objects.get(
                    cohort__id=pk,
                    active=False
                )
            except CohortCourse.DoesNotExist:
                return Response({
                    'reason': 'Could not find an inactive server side course for this cohort'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get first project of server side course
            try:
                first_project = Project.objects.get(
                    book__course=server_side_course.course,
                    book__index=0,
                    index=0
                )
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
                user__is_active=True,
                user__is_staff=False,
                assigned_cohorts__cohort=cohort
            )

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

    @log_action("assign_nssuser_to_cohort")
    @action(methods=['post', 'delete'], detail=True)
    def assign(self, request, pk):
        """Assign student or instructor to an existing cohort"""

        req_logger = bind_request_context(logger, request)

        if request.method == "POST":
            cohort = None
            member = None
            user_type = request.query_params.get("userType", None)


            cohort = Cohort.objects.get(pk=pk)
            req_logger.debug("cohort_found", cohort_name=cohort.name)

            req_logger.info(
                "cohort_assignment_started",
                cohort_id=pk,
                user_type=user_type
            )

            try:
                if user_type is not None and user_type == "instructor":
                    req_logger.info("instructor_assignment_attempt")
                    try:
                        member = NssUser.objects.get(user=request.auth.user)
                        req_logger.debug("instructor_found", instructor_id=member.id)

                        membership = NssUserCohort.objects.get(nss_user=member)
                        req_logger.warning(
                            "instructor_already_assigned",
                            current_cohort_id=membership.cohort.id,
                            current_cohort_name=membership.cohort.name
                        )

                        return Response(
                            {'message': f'Instructor cannot be in more than 1 cohort at a time. Currently assigned to cohort {membership.cohort.name}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except NssUserCohort.DoesNotExist:
                        req_logger.debug("instructor_not_assigned_to_any_cohort")
                        pass

                else:
                    user_id = int(request.data["person_id"])
                    req_logger.info("student_assignment_attempt", student_id=user_id)

                    member = NssUser.objects.get(pk=user_id)
                    req_logger.debug("student_found", student_id=member.id, student_name=member.full_name)

                NssUserCohort.objects.get(cohort=cohort, nss_user=member)
                req_logger.warning(
                    "user_already_assigned_to_cohort",
                    user_id=member.id,
                    cohort_id=cohort.id
                )

                return Response(
                    {'message': 'Person is already assigned to cohort'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except NssUserCohort.DoesNotExist:
                req_logger.info(
                    "creating_cohort_assignment",
                    user_id=member.id,
                    cohort_id=cohort.id
                )
                # Create relationship between user and cohort
                relationship = NssUserCohort()
                relationship.cohort = cohort
                relationship.nss_user = member
                relationship.save()

                req_logger.info(
                    "cohort_assignment_created",
                    user_id=member.id,
                    cohort_id=cohort.id,
                    relationship_id=relationship.id
                )

                if user_type is None:
                    req_logger.info(
                        "assigning_student_to_first_project",
                        student_id=member.id,
                        cohort_id=cohort.id
                    )

                    try:
                        # Assign student to first project in cohort's active course
                        book_first_project = Project.objects.get(
                            index=0,
                            book__course=cohort.courses.get(active=True).course,
                            book__index=0
                        )
                        req_logger.debug(
                            "first_project_found",
                            project_id=book_first_project.id,
                            project_name=book_first_project.name
                        )

                        student_project = StudentProject()
                        student_project.student = member
                        student_project.project = book_first_project
                        student_project.save()
                        req_logger.info(
                            "student_assigned_to_project",
                            student_id=member.id,
                            project_id=book_first_project.id,
                            student_project_id=student_project.id
                        )
                    except Exception as ex:
                        req_logger.error(
                            "failed_to_assign_student_to_project",
                            student_id=member.id,
                            error=str(ex)
                        )

            except Cohort.DoesNotExist as ex:
                req_logger.error(
                    "cohort_not_found",
                    cohort_id=pk,
                    error=str(ex)
                )
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except NssUser.DoesNotExist as ex:
                req_logger.error(
                    "user_not_found",
                    user_type=user_type,
                    user_id=request.data.get("person_id") if user_type is None else "current_user",
                    error=str(ex)
                )
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                req_logger.exception(
                    "unexpected_error_during_assignment",
                    error=str(ex)
                )
                return HttpResponseServerError(ex)

            req_logger.info(
                "cohort_assignment_completed",
                user_id=member.id,
                cohort_id=cohort.id,
                user_type=user_type if user_type else "student"
            )

            return Response({'message': 'User assigned to cohort'}, status=status.HTTP_201_CREATED)


        elif request.method == "DELETE":
            user_type = request.query_params.get("userType", None)

            if user_type is not None and user_type == "instructor":
                member = NssUser.objects.get(user=request.auth.user)
                req_logger.info(
                    "instructor_removal_attempt",
                    instructor_id=member.id,
                    cohort_id=pk
                )
                req_logger.debug("instructor_found", instructor_id=member.id)
            else:
                req_logger.info(
                    "student_removal_attempt",
                    student_id=request.data.get("student_id", None),
                    cohort_id=pk
                )

                if request.data.get("student_id", None) is not None:
                    user_id = int(request.data["student_id"])
                    member = NssUser.objects.get(pk=user_id)
                    req_logger.debug("student_found", student_id=member.id, student_name=member.full_name)
                else:
                    return Response(
                        {'message': 'Please provide a student ID to remove.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            try:
                cohort = Cohort.objects.get(pk=pk)
                rel = NssUserCohort.objects.get(cohort=cohort, nss_user=member)
                rel.delete()
                req_logger.info(
                    "cohort_assignment_deleted",
                    user_id=member.id,
                    cohort_id=cohort.id
                )

                return Response(None, status=status.HTTP_204_NO_CONTENT)

            except Cohort.DoesNotExist as ex:
                req_logger.error(
                    "cohort_not_found",
                    cohort_id=pk,
                    error=str(ex)
                )
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except NssUser.DoesNotExist as ex:
                req_logger.error(
                    "user_not_found",
                    user_type=user_type,
                    user_id=request.data.get("person_id") if user_type is None else "current_user",
                    error=str(ex)
                )
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except NssUserCohort.DoesNotExist as ex:
                req_logger.error(
                    "student_not_found",
                    student_id=request.data.get("student_id", None),
                    cohort_id=pk,
                    error=str(ex)
                )
                return Response(
                    {'message': "Student is not assigned to that cohort."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except Exception as ex:
                req_logger.exception(
                    "unexpected_error_during_removal",
                    error=str(ex)
                )
                return Response(
                    {'message': ex.args[0]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        req_logger.warning(
            "unsupported_http_method",
            method=request.method,
            action="assign"
        )
        return Response(
            {'message': 'Unsupported HTTP method'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

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
        except Exception:
            return ""

    def get_github_classroom_url(self, obj):
        try:
            return obj.info.github_classroom_url
        except Exception:
            return ""

    def get_attendance_sheet_url(self, obj):
        try:
            return obj.info.attendance_sheet_url
        except Exception:
            return ""

    class Meta:
        model = Cohort
        fields = (
            'id', 'name', 'slack_channel', 'start_date', 'end_date',
            'coaches', 'break_start_date', 'break_end_date', 'students',
            'is_instructor', 'courses', 'info', 'student_organization_url',
            'github_classroom_url', 'attendance_sheet_url', 'active'
        )
