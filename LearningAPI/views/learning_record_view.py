from django.http.response import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models.skill import LearningRecord, LearningRecordEntry, LearningWeight
from LearningAPI.models.people import NssUser


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
        model = LearningRecordEntry
        fields = ('id', 'score', 'note', 'recorded_on', 'instructor', 'label')


class LearningRecordSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    student = NssUserSerializer()

    class Meta:
        model = LearningRecord
        fields = ( 'id', 'student', 'weight', 'achieved', 'created_on', )


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

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            learningrecord = LearningRecord.objects.get(pk=pk)

            serializer = LearningRecordSerializer(
                learningrecord, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            records = LearningRecord.objects.all().order_by('-created_on')

            serializer = LearningRecordSerializer(
                records, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        record = LearningRecord()
        record.student = NssUser.objects.get(pk=request.data["student"])
        record.weight = LearningWeight.objects.get(pk=request.data["weight"])
        record.achieved = request.data["achieved"]

        try:
            record.save()
            entry = LearningRecordEntry()
            entry.record = record
            entry.instructor = NssUser.objects.get(user=request.auth.user)
            entry.note = request.data["note"]
            entry.save()

            serializer = LearningRecordSerializer(
                record, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            record = LearningRecord.objects.get(pk=pk)

            if request.auth.user.is_staff:
                record.achieved = request.data["achieved"]
                record.save()

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        except LearningRecord.DoesNotExist as ex:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=['delete', 'post'], detail=False)
    def entries(self, request, entry_id=None):
        """ Manage learning record entries """

        if request.method == "POST":
            # Handle POST operations
            try:
                record = LearningRecord.objects.get(pk=request.data["record"])
            except LearningRecord.DoesNotExist:
                return Response({"reason": "Learning record not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                weight = LearningWeight.objects.get(pk=request.data["weight"])
            except LearningWeight.DoesNotExist:
                return Response({"reason": "Learning weight not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                entry = LearningRecordEntry()
                entry.record = record
                entry.weight = weight
                entry.instructor = NssUser.objects.get(
                    user=request.auth.user)
                entry.note = request.data["note"]
                entry.save()

                serializer = LearningRecordSerializer(
                    record, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "DELETE":

            try:
                entry = LearningRecordEntry.objects.get(pk=entry_id)
                record_id = entry.record_id
                entry.delete()

                record_entries = LearningRecordEntry.objects.filter(
                    record_id=record_id)
                any_left = len(record_entries)
                if not any_left:
                    record = LearningRecord.objects.get(pk=record_id)
                    record.delete()

            except LearningRecordEntry.DoesNotExist:
                return Response(None, status=status.HTTP_404_NOT_FOUND)

            return Response(None, status=status.HTTP_204_NO_CONTENT)
