""" This module contains the view for the HelpRequest model. """
import torch
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from transformers import AutoModelForCausalLM, AutoTokenizer
from LearningAPI.models.help import HelpRequest


# LearningAPI/views/help_request.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from valkey import Valkey
import json
from django.conf import settings

# Module-level Valkey client
valkey_client = Valkey(
    host=settings.VALKEY_CONFIG['HOST'],
    port=settings.VALKEY_CONFIG['PORT'],
    db=settings.VALKEY_CONFIG['DB'],
)

class HelpRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

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
                student=request.user,
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


class HelpRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize model and tokenizer
        self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
        self.model.to(self.device)  # Move model to GPU if available
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

        self.SYSTEM_PROMPT = """You are a programming concept explainer.
        You must ONLY provide natural language explanations.
        Never generate or include code examples.
        Never use code formatting, backticks, or code blocks.
        Explain concepts using analogies and plain language instead.
        The explanations must be generated to be understandable by a beginner.
        The explanations must assume the user has no prior knowledge of the concept."""

    def sanitize_response(self, response: str) -> str:
        import re
        # Implementation from previous response
        # (Include the sanitization code we discussed earlier)
        return response

    def create(self, request):
        try:
            question = request.data.get('question')
            if not question:
                return Response(
                    {'error': 'Question is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare the prompt
            full_prompt = f"{self.SYSTEM_PROMPT}\n\nQuestion: {question}"

            # Generate response
            inputs = self.tokenizer(full_prompt, return_tensors="pt", truncation=True)
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=500,
                temperature=0.7,
                num_return_sequences=1,
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            clean_response = self.sanitize_response(response)

            # Save the request and response (optional)
            help_request = HelpRequest.objects.create(
                student=request.user,
                question=question,
                response=clean_response
            )

            return Response({
                'response': clean_response,
                'id': help_request.id
            }, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response(
                {'error': str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HelpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ('id', 'question', 'response', 'created_at')
