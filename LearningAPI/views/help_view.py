""" This module contains the view for the HelpRequest model. """
import json
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from valkey import Valkey
from LearningAPI.models.help import HelpRequest
from LearningAPI.models.people import NssUser


# Module-level Valkey client
valkey_client = Valkey(
    host=settings.VALKEY_CONFIG['HOST'],
    port=settings.VALKEY_CONFIG['PORT'],
    db=settings.VALKEY_CONFIG['DB'],
)

class HelpRequestViewSet(viewsets.ViewSet):

    def create(self, request):
        try:
            question = request.data.get('question')
            if not question:
                return Response(
                    {'error': 'Question is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create help request record
            help_request = HelpRequest.objects.create(
                student=NssUser.objects.get(user=request.user),
                question=question,
                status='pending'
            )

            # Publish to Valkey channel using module-level client
            valkey_client.publish('student_question', json.dumps({
                'request_id': help_request.id,
                'question': question,
                'user_id': request.user.id
            }))

            return Response({
                'request_id': help_request.id,
                'status': 'processing'
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as ex:
            return Response(
                {'error': str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HelpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ('id', 'question', 'status', 'created_at')
