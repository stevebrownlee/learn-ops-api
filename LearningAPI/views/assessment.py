from django.http import HttpResponseServerError
from django.db.models import Count, Q, Sum
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from LearningAPI.models import NssUser, StudentAssessment, StudentAssessmentStatus, Assessment
from django.forms.models import model_to_dict
from rest_framework.pagination import PageNumberPagination

from LearningAPI.models.assessment import Assessment


class StudentAssessmentPermission(permissions.BasePermission):
    """Custom permissions for Assessment view"""
    def has_permission(self, request, view):
        if view.action in [ 'destroy',]:
            return request.auth.user.is_staff
        elif view.action in ['list', 'retrieve', 'update', 'partial_update', 'create']:
            return True
        else:
            return False


class StudentAssessmentPagination(PageNumberPagination):
    """Custom pagination for Assessment view"""
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 80


class StudentAssessmentView(ViewSet):
    """Student view set"""

    permission_classes = (StudentAssessmentPermission,)
    pagination_class = StudentAssessmentPagination

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        student_assessment = StudentAssessment()
        student_assessment.student = NssUser.objects.get(user=request.auth.user)
        student_assessment.assessment = Assessment.objects.get(pk=request.data["assessmentId"])
        student_assessment.status = StudentAssessmentStatus.objects.get(status="In Progress")

        try:
            student_assessment.save()
            serializer = StudentAssessmentSerializer(student_assessment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """Listing all assessments not allowed."""
        assessments = Assessment.objects.all()
        serializer = AssessmentSerializer(assessments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            assessment = StudentAssessment.objects.get(pk=pk)

            if request.auth.user == assessment.student or request.auth.user.is_staff:
                serializer = StudentAssessmentSerializer(assessment, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "You are not authorized to view this student profile."},
                    status=status.HTTP_401_UNAUTHORIZED)

        except StudentAssessment.DoesNotExist:
            return Response(
                {"message": "That student assessment does not exist."},
                status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            assessment = StudentAssessment.objects.get(pk=pk)
            assessment_status = StudentAssessmentStatus.objects.get(pk=request.data["status"])

            if request.auth.user == assessment.student.user or request.auth.user.is_staff:

                if assessment.status == assessment_status:
                    return Response({ "message": "No change in status"}, status=status.HTTP_400_BAD_REQUEST)


                if request.auth.user == assessment.student.user and assessment_status.status not in ("In Progress", "Ready for Review", ):
                    return Response(None, status=status.HTTP_401_UNAUTHORIZED)

                if request.auth.user.is_staff:
                    assessment.instructor = NssUser.objects.get(user=request.auth.user)

                assessment.status = assessment_status
                assessment.save()

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        except StudentAssessment.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single student

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            assessment = StudentAssessment.objects.get(pk=pk)
            assessment.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except StudentAssessment.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssessmentSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Assessment
        fields = ('id', 'name', )

class StudentAssessmentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    student = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_assessment(self, obj):
        """Return just the name of the assessment"""
        return {
            "id": obj.id,
            "name": obj.assessment.name
        }

    def get_status(self, obj):
        """Return the status of assessment"""
        return obj.status.status

    def get_student(self, obj):
        """Return the student full name"""
        return {
            "id": obj.student.user.id,
            "name": f'{obj.student.user.first_name} {obj.student.user.last_name}'
        }

    class Meta:
        model = StudentAssessment
        fields = ('id', 'student', 'assessment', 'status', 'url', )
