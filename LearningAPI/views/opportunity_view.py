from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.people import Opportunity, NssUser, Cohort


class OpportunityViewSet(ViewSet):
    """Opportunity view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        opportunity = Opportunity()
        opportunity.portion = request.data["portion"]
        opportunity.start_date = request.data["start_date"]
        opportunity.message = request.data["message"]

        cohort = Cohort.objects.get(pk=int(request.data["cohort_id"]))
        opportunity.cohort = cohort

        senior_instructor = NssUser.objects.get(pk=int(request.data["instructor_id"]))
        opportunity.senior_instructor = senior_instructor

        try:
            opportunity.save()
            serializer = OpportunitySerializer(opportunity, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            opportunity = Opportunity.objects.get(pk=pk)

            serializer = OpportunitySerializer(opportunity, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            opportunity = Opportunity.objects.get(pk=pk)
            opportunity.portion = request.data["portion"]
            opportunity.start_date = request.data["start_date"]
            opportunity.message = request.data["message"]

            cohort = Cohort.objects.get(pk=int(request.data["cohort_id"]))
            opportunity.cohort = cohort

            senior_instructor = NssUser.objects.get(pk=int(request.data["instructor_id"]))
            opportunity.senior_instructor = senior_instructor

            opportunity.save()
        except Opportunity.DoesNotExist:
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
            opportunity = Opportunity.objects.get(pk=pk)
            opportunity.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Opportunity.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            opportunitys = Opportunity.objects.all().order_by('pk')

            serializer = OpportunitySerializer(
                opportunitys, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

class CohortSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Cohort
        fields = ('name',)


class OpportunitySerializer(serializers.ModelSerializer):
    """JSON serializer"""
    cohort = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()

    def get_cohort(self, obj):
        return obj.cohort.name

    def get_instructor(self, obj):
        return f'{obj.senior_instructor.user.first_name} {obj.senior_instructor.user.last_name}'


    class Meta:
        model = Opportunity
        fields = ('id', 'portion', 'message', 'cohort', 'portion', 'start_date', 'instructor',)
