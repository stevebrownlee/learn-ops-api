from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.coursework import Book, Project, Course


class ProjectViewSet(ViewSet):
    """Project view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        project = Project()
        project.name = request.data["name"]
        project.index = request.data["index"]
        project.active = True
        project.is_group_project = request.data["is_group_project"]
        project.api_template_url = request.data["api_template_url"]
        project.client_template_url = request.data["client_template_url"]
        project.book = Book.objects.get(pk=request.data["book"])
        project.implementation_url = request.data["implementation_url"]

        try:
            project.save()
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            project = Project.objects.get(pk=pk)

            serializer = ProjectSerializer(project, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            project = Project.objects.get(pk=pk)
            project.name = request.data["name"]
            project.active = request.data["active"]
            project.index = request.data["index"]
            project.is_group_project = request.data["is_group_project"]
            project.api_template_url = request.data.get("api_template_url", "")
            project.client_template_url = request.data.get("client_template_url", "")
            project.implementation_url = request.data.get("implementation_url", "")

            project.save()
        except Project.DoesNotExist:
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
            project = Project.objects.get(pk=pk)
            project.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Project.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        book_id = request.query_params.get("bookId", None)
        course_id = request.query_params.get("courseId", None)

        try:
            projects = Project.objects.all().order_by('book__index', 'index')

            if course_id is not None:
                projects = projects.filter(book__course__id=course_id)

            if book_id is not None:
                projects = projects.filter(book__id=book_id)

            serializer = ProjectSerializer(projects, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class BookSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Book
        fields = ('id', 'name',)

class CourseSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Course
        fields = ('id', 'name',)


class ProjectSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    book = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    def get_book(self, obj):
        request = self.context.get('request')
        if request is not None:
            expansions = request.query_params.getlist("expand", None)
            if 'book' in expansions:
                book = BookSerializer(obj.book, many=False)
                return book.data
        return obj.book.id

    def get_course(self, obj):
        request = self.context.get('request')
        if request is not None:
            expansions = request.query_params.getlist("expand", None)
            if 'course' in expansions:
                course = CourseSerializer(obj.book.course, many=False)
                return course.data
        return obj.book.course.id

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'book', 'course',
            'index', 'active', 'is_group_project',
            'api_template_url', 'client_template_url',
        )
