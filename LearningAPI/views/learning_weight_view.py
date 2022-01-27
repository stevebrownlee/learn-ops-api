from django.http.response import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from LearningAPI.models import LearningWeight
from django.db.models import Q
from django.forms.models import model_to_dict


from LearningAPI.models.learning_record import LearningRecord


class LearningWeightSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = LearningWeight
        fields = '__all__'

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class LearningWeightViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning weights.
    """
    queryset = LearningWeight.objects.all().order_by("tier")
    serializer_class = LearningWeightSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LargeResultsSetPagination

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        student = self.request.query_params.get('studentId', None)

        try:
            if student is not None:
                weights = LearningWeight.objects\
                    .raw("""
                        select w.id,
                            w.label,
                            w.weight,
                            w.tier,
                            r.achieved,
                            r.student_id
                        from public."LearningAPI_learningweight" w
                        left outer join public."LearningAPI_learningrecord" r
                            on r.weight_id = w.id
                                and
                                r.student_id = %s
                        where r.achieved is NULL
                        order by w.tier
                    """,
                    [student])
            else:
                weights = LearningWeight.objects.all().order_by('tier')

            serializer = LearningWeightSerializer(
                weights, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)
