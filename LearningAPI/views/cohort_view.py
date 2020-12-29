from django.db.models import Count, Q
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models import Cohort, NssUser
from LearningAPI.models.nssuser_cohort import NssUserCohort


class CohortViewSet(ViewSet):
    """Cohort view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        cohort = Cohort()
        cohort.name = request.data["name"]
        cohort.slack_channel = request.data["slack_channel"]
        cohort.start_date = request.data["start_date"]
        cohort.end_date = request.data["end_date"]
        cohort.break_start_date = request.data["break_start_date"]
        cohort.break_end_date = request.data["break_end_date"]

        try:
            cohort.save()
            serializer = CohortSerializer(cohort, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            cohort = Cohort.objects.annotate(students=Count(
                'members', filter=Q(members__nss_user__user__is_staff=False)),
                instructors=Count(
                'members', filter=Q(members__nss_user__user__is_staff=True))
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
            Response -- 200, 404, or 500 status code
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
            cohorts = Cohort.objects.annotate(students=Count(
                'members', filter=Q(members__nss_user__user__is_staff=False)),
                instructors=Count(
                'members', filter=Q(members__nss_user__user__is_staff=True))
            ).all()

            serializer = CohortSerializer(
                cohorts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=['post', 'delete'], detail=True)
    def assign(self, request, pk):
        """Assign student or instructor to a cohort"""

        if request.method == "POST":
            cohort = None
            member = None

            try:
                cohort = Cohort.objects.get(pk=pk)
                member = NssUser.objects.get(pk=int(request.data["user_id"]))
                NssUserCohort.objects.get(cohort=cohort, nss_user=member)

                return Response(
                    {'message': 'Person is already assigned to cohort'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except NssUserCohort.DoesNotExist as ex:
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


class CohortSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Cohort
        fields = ('name', 'slack_channel', 'start_date', 'end_date',
                  'break_start_date', 'break_end_date', 'students', 'instructors')
