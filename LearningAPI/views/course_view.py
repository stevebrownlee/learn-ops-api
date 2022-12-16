from django.db.models import Count
from django.utils.decorators import method_decorator
from django.http import HttpResponseServerError

from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from LearningAPI.decorators import is_instructor
from LearningAPI.models.coursework import Course, Book, Project, CohortCourse


class CourseViewSet(ViewSet):
    """Course view set"""

    # permission_classes = (IsAdminUser,)

    @method_decorator(is_instructor())
    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        course = Course()
        course.name = request.data["name"]

        try:
            course.save()
            serializer = CourseSerializer(course, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            course = Course.objects.annotate(
                chapters=Count('books__chapters')
            ).get(pk=pk)

            serializer = CourseSerializer(course, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @method_decorator(is_instructor())
    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            course = Course.objects.get(pk=pk)
            course.name = request.data["name"]

            course.save()
        except Course.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @method_decorator(is_instructor())
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            course = Course.objects.get(pk=pk)
            course.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Course.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        cohort = request.query_params.get("cohortId", None)
        active = request.query_params.get("active", None)

        try:
            courses = Course.objects.all()

            if cohort is not None and active is not None:
                active_cohort_course = CohortCourse.objects.get(cohort__id=cohort, active=bool(active))
                courses = courses.filter(pk=active_cohort_course.course.id)

            serializer = CourseSerializer(courses, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

class ProjectSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Project
        fields = ('id', 'name',)


class BookSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    projects = ProjectSerializer(many=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'projects', 'cardinality')
        depth = 1


class CourseSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    books = serializers.SerializerMethodField()

    def get_books(self, obj):
        books = Book.objects.filter(course=obj).order_by("cardinality")
        return BookSerializer(books, many=True).data

    class Meta:
        model = Course
        fields = ('id', 'name', 'books',)
