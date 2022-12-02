from django.db.models import Count, Q, Case, When
from django.db.models.fields import BooleanField
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from ..models.people import Cohort, NssUser, NssUserCohort


class CohortPermission(permissions.BasePermission):
    """Cohort permissions"""

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'destroy', 'assign']:
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
        cohort = Cohort()
        cohort.name = request.data["name"]
        cohort.slack_channel = request.data["slackChannel"]
        cohort.start_date = request.data["startDate"]
        cohort.end_date = request.data["endDate"]
        cohort.break_start_date = request.data["breakStartDate"]
        cohort.break_end_date = request.data["breakEndDate"]

        try:
            cohort.save()
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

            if search_terms != None:
                for letter in list(search_terms):
                    cohorts = cohorts.filter(name__icontains=letter)

                serializer = MiniCohortSerializer(
                    cohorts, many=True, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            cohorts = cohorts.annotate(
                students=Count('members', filter=Q(members__nss_user__user__is_staff=False)),
                is_instructor=Count('members', filter=Q(members__nss_user__user=request.auth.user)),
            ).all().order_by('-pk')



            if limit is not None:
                cohorts = cohorts.all()[0:int(limit)]

            serializer = CohortSerializer(
                cohorts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=['post', 'delete'], detail=True)
    def assign(self, request, pk):
        """Assign student or instructor to an existing cohort"""

        if request.method == "POST":
            cohort = None
            member = None

            try:
                user_type = request.query_params.get("userType", None)

                if user_type is not None and user_type == "instructor":
                    user_id = request.auth.user.id
                else:
                    user_id = int(request.data["person_id"])

                cohort = Cohort.objects.get(pk=pk)
                member = NssUser.objects.get(pk=user_id)
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
                user_id = request.auth.user.id
            else:
                user_id = int(request.data["student_id"])

            try:
                cohort = Cohort.objects.get(pk=pk)
                member = NssUser.objects.get(pk=user_id)
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


class CohortSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Cohort
        fields = ('id', 'name', 'slack_channel', 'start_date', 'end_date', 'coaches',
                  'break_start_date', 'break_end_date', 'students', 'is_instructor', )
