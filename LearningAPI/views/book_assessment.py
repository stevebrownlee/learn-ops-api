"""Assessment view module"""
from django.http import HttpResponseServerError

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from LearningAPI.models.people import Assessment
from LearningAPI.models.coursework import Book
from LearningAPI.models.skill import AssessmentWeight, LearningWeight


class BookAssessmentView(ViewSet):
    """Book assessment view set"""

    def list(self, request):
        """Listing all assessments"""
        book_id = request.query_params.get("bookId", None)
        assessments = Assessment.objects.all()

        if book_id is not None:
            assessments = Assessment.objects.filter(book__id=book_id)

        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single assessment

        Returns:
            Response -- JSON serialized instance
        """
        try:
            assessment = Assessment.objects.get(pk=pk)
            serializer = AssessmentSerializer(assessment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Assessment.DoesNotExist:
            return Response(
                {"message": "That assessment does not exist."},
                status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk):
        """Handle PUT operations

        Returns:
            Response -- JSON serialized instance
        """
        book_id = request.data.get("bookId", None)
        source_url = request.data.get("sourceURL", None)
        name = request.data.get("name", None)
        objectives = request.data.get("objectives", None)

        if name is not None and \
                source_url is not None and \
                objectives is not None and \
                book_id is not None and\
                request.auth.user.is_staff:

            assmt = Assessment.objects.get(pk=pk)
            assmt.name = request.data["name"]
            assmt.source_url = request.data["sourceURL"]

            try:
                assmt.book = Book.objects.get(pk=book_id)
            except Book.DoesNotExist:
                return Response({'reason': 'Invalid book id sent'}, status=status.HTTP_400_BAD_REQUEST)

            assmt.save()

            # Create or delete relationships

            # Set of weight ids sent by client
            client_set = set(objectives)

            # Set of weight ids currently in database
            existing_set = set(AssessmentWeight.objects.filter(assessment_id=pk).values_list('weight_id', flat=True))

            # Determine which need to be added by difference between client ids and existing ids
            add_set = client_set.difference(existing_set)

            # Determine which need to be deleted by difference between existing ids and client ids
            delete_set = existing_set.difference(client_set)

            # Bulk add all new ones with `bulk_create` and a list comperehension
            AssessmentWeight.objects.bulk_create([
                AssessmentWeight(assessment_id=pk, weight_id=id) for id in add_set
            ])

            # Delete all rows that exist, but were not in client request
            AssessmentWeight.objects.filter(weight_id__in=list(delete_set)).delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"reason": "Please provide all required fields"}, status=status.HTTP_400_BAD_REQUEST)


class AssessmentObjectiveSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = LearningWeight
        fields = ('id', 'label', )


class AssessmentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    objectives = AssessmentObjectiveSerializer(many=True)

    class Meta:
        model = Assessment
        fields = ('id', 'name', 'source_url',
                  'assigned_book', 'course', 'objectives')
