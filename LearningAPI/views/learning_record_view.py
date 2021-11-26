from rest_framework import serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models import LearningRecord
from LearningAPI.models import LearningRecordWeight
from LearningAPI.models.learning_weight import LearningWeight
from LearningAPI.models.nssuser import NssUser


class NssUserSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    class Meta:
        model = NssUser
        fields = ('id', 'name')


class RecordWeightSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    score = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    instructor = NssUserSerializer()

    def get_score(self, obj):
        return obj.weight.weight

    def get_label(self, obj):
        return obj.weight.label

    class Meta:
        model = LearningRecordWeight
        fields = ('id', 'score', 'note', 'recorded_on', 'instructor', 'label')


class LearningRecordSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    weights = RecordWeightSerializer(many=True)
    student = NssUserSerializer()

    class Meta:
        model = LearningRecord
        fields = ('student', 'description', 'obtained_from',
                  'weights', 'created_on', 'id', )


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class LearningRecordViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning records.
    """
    queryset = LearningRecord.objects.all()
    serializer_class = LearningRecordSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LargeResultsSetPagination

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        record = LearningRecord()
        record.student = NssUser.objects.get(pk=request.data["student"])
        record.description = request.data["description"]
        record.obtained_from = request.data["obtained_from"]

        weight = LearningWeight.objects.get(pk=request.data["weight"])

        try:
            record.save()
            record_weight = LearningRecordWeight()
            record_weight.record = record
            record_weight.weight = weight
            record_weight.instructor = NssUser.objects.get(user=request.auth.user)
            record_weight.note = request.data["note"]
            record_weight.save()

            serializer = LearningRecordSerializer( record, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
