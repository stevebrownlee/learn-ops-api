from LearningAPI.models.favorite_notes import FavoriteNote
from rest_framework.decorators import action
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models import LearningObjective, NssUser, TaxonomyLevel


class LearningObjectiveViewSet(ViewSet):
    """Chapter view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        objective = LearningObjective()
        objective.user = NssUser.objects.get(user=request.auth.user)
        objective.swbat = request.data["swbat"]

        tax_level = TaxonomyLevel.objects.get(pk=int(request.data["taxonomy_id"]))
        objective.bloom_level = tax_level

        try:
            objective.save()
            serializer = LearningObjectiveSerializer(
                objective, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            objective = LearningObjective.objects.get(pk=pk)

            serializer = LearningObjectiveSerializer(
                objective, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            objective = LearningObjective.objects.get(pk=pk)
            objective.swbat = request.data["swbat"]

            bloom_level = TaxonomyLevel.objects.get(pk=int(request.data["taxonomy_id"]))
            objective.bloom_level = bloom_level

            objective.save()
        except LearningObjective.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except TaxonomyLevel.DoesNotExist as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            objective = LearningObjective.objects.get(pk=pk)
            objective.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except LearningObjective.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            notes = LearningObjective.objects.all().order_by('pk')

            serializer = LearningObjectiveSerializer(
                notes, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class LearningObjectiveSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = LearningObjective
        fields = ( 'id', 'swbat', 'bloom_level', )
