"""Student view module"""
import os
import statistics
import logging

import requests
from django.db.models import Count, Q
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from LearningAPI.decorators import is_instructor
from LearningAPI.models.people import (Cohort, DailyStatus, NssUser,
                                       OneOnOneNote, StudentPersonality)
from LearningAPI.models.skill import (CoreSkillRecord, LearningRecord,
                                      LearningRecordEntry)
from LearningAPI.views.core_skill_record_view import CoreSkillRecordSerializer


class StudentPagination(PageNumberPagination):
    """Pagination for student resource"""
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 80


class StudentViewSet(ModelViewSet):
    """Student viewset"""

    pagination_class = StudentPagination

    def create(self, request):
        """Handle POST operations"""
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        logger = logging.getLogger("LearningPlatform")

        try:
            try:
                student = NssUser.objects.get(pk=pk)

            except ValueError:
                student = NssUser.objects.get(slack_handle=pk)

            try:
                personality = StudentPersonality.objects.get(student=student)
            except StudentPersonality.DoesNotExist:
                personality = StudentPersonality()
                personality.briggs_myers_type = ""
                personality.bfi_extraversion = 0
                personality.bfi_agreeableness = 0
                personality.bfi_conscientiousness = 0
                personality.bfi_neuroticism = 0
                personality.bfi_openness = 0
                personality.student = student
                personality.save()
            except Exception as ex:
                logger.exception(getattr(ex, 'message', repr(ex)))

            if request.auth.user == student.user or request.auth.user.is_staff:
                serializer = StudentSerializer(
                    student, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "You are not authorized to view this student profile."},
                    status=status.HTTP_401_UNAUTHORIZED)

        except NssUser.DoesNotExist:
            return Response(
                {"message": "That student does not exist."},
                status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            logger.exception(getattr(ex, 'message', repr(ex)))
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            student = NssUser.objects.get(pk=pk)

            if request.auth.user == student.user or request.auth.user.is_staff:
                if "slack_handle" in request.data:
                    student.slack_handle = request.data["slack_handle"]
                if "gitub_handle" in request.data:
                    student.gitub_handle = request.data["gitub_handle"]

                student.save()

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        except NssUser.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

    @method_decorator(is_instructor())
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single student

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            student = NssUser.objects.get(pk=pk)
            student.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except NssUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all students

        Returns:
            Response -- JSON serialized array
        """
        student_status = self.request.query_params.get('status', None)

        if student_status == "unassigned":
            students = NssUser.objects.\
                annotate(cohort_count=Count('assigned_cohorts')).\
                filter(user__is_staff=False,
                       user__is_active=True, cohort_count=0)
        else:
            students = NssUser.objects.filter(
                user__is_active=True, user__is_staff=False)

        serializer = SingleStudent(
            students, many=True, context={'request': request})

        search_terms = self.request.query_params.get('q', None)
        if search_terms is not None:
            for letter in list(search_terms):
                students = students.filter(
                    Q(user__first_name__icontains=letter)
                    | Q(user__last_name__icontains=letter)
                )

            serializer = SingleStudent(
                students, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        cohort = self.request.query_params.get('cohort', None)
        feedback = self.request.query_params.get('feedback', None)

        if cohort is not None:
            cohort_filter = Cohort.objects.get(pk=cohort)
            students = students.filter(assigned_cohorts__cohort=cohort_filter)

            if feedback is not None and feedback == 'true':
                serializer = MicroStudents(
                    students, many=True, context={'request': request})
            else:
                serializer = MicroStudents(
                    students, many=True, context={'request': request})

        page = self.paginate_queryset(serializer.data)
        paginated_response = self.get_paginated_response(page)
        return paginated_response

    @method_decorator(is_instructor())
    @action(methods=['post'], detail=True)
    def status(self, request, pk):
        """Add daily status from stand-up"""

        if request.method == "POST":
            try:
                daily_status = DailyStatus()
                daily_status.coach = NssUser.objects.get(
                    user=request.auth.user)
                daily_status.student = NssUser.objects.get(pk=pk)
                daily_status.status = request.data["status"]

                daily_status.save()

                response = {
                    "id": daily_status.id,
                    "status": daily_status.status
                }

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response(response, status=status.HTTP_201_CREATED)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @method_decorator(is_instructor())
    @action(methods=['post'], detail=True)
    def feedback(self, request, pk):
        """Add feedback from 1:1 session"""

        if request.method == "POST":
            try:
                student = NssUser.objects.get(pk=pk)
                note = OneOnOneNote()
                note.coach = NssUser.objects.get(user=request.auth.user)
                note.student = student
                note.notes = request.data["notes"]
                note.save()

                # Send message to student
                try:
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    channel_payload = {
                        "text": request.data.get("text", "You just received feedback from one of your coaches.\n\nVisit https://learning.nss.team to view your messages."),
                        "token": os.getenv("SLACK_BOT_TOKEN"),
                        "channel": student.slack_handle
                    }

                    requests.post(
                        "https://slack.com/api/chat.postMessage",
                        data=channel_payload,
                        headers=headers
                    )
                except Exception:
                    pass

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response({'message': 'Student note created'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def student_score(self, obj):
    """Return total learning score"""

    # First get the total of the student's technical objectives
    total = 0
    scores = LearningRecord.objects.\
        filter(student=obj, achieved=True).\
        order_by("-id")

    for score in scores:
        total += score.weight.weight

    # Get the average of the core skills' levels and adjust the
    # technical score positively by the percent
    core_skill_records = CoreSkillRecord.objects.filter(
        student=obj).order_by("pk")
    scores = [record.level for record in core_skill_records]
    # for record in core_skill_records:
    #     scores.append(record.level)

    try:
        # Hannah and I did this on a Monday morning, so it may be the wrong
        # approach, but it's a step in the right direction
        mean = statistics.mean(scores)
        total = round(total * (1 + (mean / 10)))

    except statistics.StatisticsError:
        pass

    return total


class StudentNoteSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = OneOnOneNote
        fields = ['id', 'notes', 'session_date', 'author']


class StudentStatusSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = DailyStatus
        fields = ['id', 'status', 'created_on', 'author']


class LearningRecordEntrySerializer(serializers.ModelSerializer):
    """JSON serializer"""
    instructor = serializers.SerializerMethodField()

    def get_instructor(self, obj):
        return f'{obj.instructor.user.first_name} {obj.instructor.user.last_name}'

    class Meta:
        model = LearningRecordEntry
        fields = ('id', 'note', 'recorded_on', 'instructor')


class LearningRecordSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    entries = LearningRecordEntrySerializer(many=True)
    objective = serializers.SerializerMethodField()

    def get_objective(self, obj):
        return obj.weight.label

    class Meta:
        model = LearningRecord
        fields = ('id', 'objective', 'achieved', 'entries', )


class PersonalitySerializer(serializers.ModelSerializer):
    """Serializer for a student's personality info"""
    briggs_myers_type = serializers.SerializerMethodField()

    def get_briggs_myers_type(self, obj):
        if obj.briggs_myers_type != "":
            return {
                "code": obj.briggs_myers_type,
                "description": myers_briggs_persona(obj.briggs_myers_type)
            }
        else:
            return {}

    class Meta:
        model = StudentPersonality
        fields = (
            'briggs_myers_type', 'bfi_extraversion',
            'bfi_agreeableness', 'bfi_conscientiousness',
            'bfi_neuroticism', 'bfi_openness',
        )


class StudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    statuses = StudentStatusSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    core_skill_records = serializers.SerializerMethodField()
    personality = PersonalitySerializer(many=False)

    def get_score(self, obj):
        return student_score(self, obj)

    def get_records(self, obj):
        records = LearningRecord.objects.filter(
            student=obj).order_by("achieved")
        return LearningRecordSerializer(records, many=True).data

    def get_core_skill_records(self, obj):
        records = CoreSkillRecord.objects.filter(student=obj).order_by("pk")
        return CoreSkillRecordSerializer(records, many=True).data

    def get_github(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["login"]

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'github', 'score', 'core_skill_records',
                  'cohorts', 'feedback', 'records', 'statuses', 'personality')


class MicroStudents(serializers.ModelSerializer):
    """JSON serializer"""
    name = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        return student_score(self, obj)

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'score')


class SingleStudent(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    repos = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        return student_score(self, obj)

    def get_staff(self, obj):
        return False

    def get_github(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["login"]

    def get_repos(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["repos_url"]

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'github', 'staff', 'slack_handle',
                  'cohorts', 'feedback', 'repos', 'score',)


PERSONALITY_TYPES = {
    "ISTJ": """Quiet, serious, earn success by thoroughness and dependability.
    Practical, matter-of-fact, realistic, and responsible. Decide logically
    what should be done and work toward it steadily, regardless of distractions.
    Take pleasure in making everything orderly and organized - their work, their
    home, their life. Value traditions and loyalty.""",
    "ISFJ": {
        "summary": """Quiet, friendly, responsible, and conscientious. Committed and steady in meeting their obligations. Thorough, painstaking, and accurate. Loyal, considerate, notice and remember specifics about people who are important to them, concerned with how others feel. Strive to create an orderly and harmonious environment at work and at home.""",
        "emotion": """

                    """
        },
    "INFJ": {
        "summary": """Seek meaning and connection in ideas, relationships, and material possessions. Want to understand what motivates people and are insightful about others. Conscientious and committed to their firm values. Develop a clear vision about how best to serve the common good. Organized and decisive in implementing their vision""",
        "emotion": """

                    """
        },
    "INTJ": {
        "summary": """Have original minds and great drive for implementing their ideas and achieving their goals. Quickly see patterns in external events and develop long-range explanatory perspectives. When committed, organize a job and carry it through. Skeptical and independent, have high standards of competence and performance - for themselves and others.""",
        "emotion": """Tend to prioritize rationality and success over politeness and pleasantries – in other words, they’d rather be right than popular.
                    Many common social practices – from small talk to white lies – may seem pointless or downright stupid to them. As a result, they may inadvertently come across as rude or even offensive when they’re only trying to be honest.
                    """
        },
    "ISTP": {
        "summary": """Tolerant and flexible, quiet observers until a problem appears, then act quickly to find workable solutions. Analyze what makes things work and readily get through large amounts of data to isolate the core of practical problems. Interested in cause and effect, organize facts using logical principles, value efficiency""",
        "emotion": """

                    """
        },
    "ISFP": {
        "summary": """Quiet, friendly, sensitive, and kind. Enjoy the present moment, what's going on around them. Like to have their own space and to work within their own time frame. Loyal and committed to their values and to people who are important to them. Dislike disagreements and conflicts, do not force their opinions or values on others.""",
        "emotion": """

                    """
        },
    "INFP": {
        "summary": """Idealistic, loyal to their values and to people who are important to them. Want an external life that is congruent with their values. Curious, quick to see possibilities, can be catalysts for implementing ideas. Seek to understand people and to help them fulfill their potential. Adaptable, flexible, and accepting unless a value is threatened.""",
        "emotion": """

                    """
        },
    "INTP": {
        "summary": """Seek to develop logical explanations for everything that interests them. Theoretical and abstract, interested more in ideas than in social interaction. Quiet, contained, flexible, and adaptable. Have unusual ability to focus in depth to solve problems in their area of interest. Skeptical, sometimes critical, always analytical.""",
        "emotion": """Can find themselves baffled by the illogical, irrational ways that feelings and emotions influence people’s behavior – including their own.
                    Want to offer emotional support to their friends and loved ones, but they don’t necessarily know how.
                    Since they can’t decide on the best, most efficient way to offer support, they may hold off on doing or saying anything at all.
                    """
        },
    "ESTP": {
        "summary": """Flexible and tolerant, they take a pragmatic approach focused on immediate results. Theories and conceptual explanations bore them - they want to act energetically to solve the problem. Focus on the here-and-now, spontaneous, enjoy each moment that they can be active with others. Enjoy material comforts and style. Learn best through doing.""",
        "emotion": """

                    """
        },
    "ESFP": {
        "summary": """Outgoing, friendly, and accepting. Exuberant lovers of life, people, and material comforts. Enjoy working with others to make things happen. Bring common sense and a realistic approach to their work, and make work fun. Flexible and spontaneous, adapt readily to new people and environments. Learn best by trying a new skill with other people.""",
        "emotion": """

                    """
        },
    "ENFP": {
        "summary": """Warmly enthusiastic and imaginative. See life as full of possibilities. Make connections between events and information very quickly, and confidently proceed based on the patterns they see. Want a lot of affirmation from others, and readily give appreciation and support. Spontaneous and flexible, often rely on their ability to improvise and their verbal fluency.""",
        "emotion": """

                    """
        },
    "ENTP": {
        "summary": """Quick, ingenious, stimulating, alert, and outspoken. Resourceful in solving new and challenging problems. Adept at generating conceptual possibilities and then analyzing them strategically. Good at reading other people. Bored by routine, will seldom do the same thing the same way, apt to turn to one new interest after another.""",
        "emotion": """Challenge is to translate their wide-ranging intellectual energy into real-world achievements and contributions.
                    May find that their quarrelsome fun burns many bridges, often inadvertently.
                    Unless they cultivate a bit of sensitivity, they may struggle to maintain deeper relationships.
                    """
        },
    "ESTJ": {
        "summary": """Practical, realistic, matter-of-fact. Decisive, quickly move to implement decisions. Organize projects and people to get things done, focus on getting results in the most efficient way possible. Take care of routine details. Have a clear set of logical standards, systematically follow them and want others to also. Forceful in implementing their plans.""",
        "emotion": """

                    """
        },
    "ESFJ": {
        "summary": """Warmhearted, conscientious, and cooperative. Want harmony in their environment, work with determination to establish it. Like to work with others to complete tasks accurately and on time. Loyal, follow through even in small matters. Notice what others need in their day-by-day lives and try to provide it. Want to be appreciated for who they are and for what they contribute.""",
        "emotion": """

                    """
        },
    "ENFJ": {
        "summary": """Warm, empathetic, responsive, and responsible. Highly attuned to the emotions, needs, and motivations of others. Find potential in everyone, want to help others fulfill their potential. May act as catalysts for individual and group growth. Loyal, responsive to praise and criticism. Sociable, facilitate others in a group, and provide inspiring leadership.""",
        "emotion": """

                    """
        },
    "ENTJ": {
        "summary": """Frank, decisive, assume leadership readily. Quickly see illogical
                and inefficient procedures and policies. Enjoy long-term planning and goal
                setting. Usually well informed, well read, enjoy expanding their knowledge and
                passing it on to others. Forceful in presenting their ideas.""",
        "emotion": """Emotional expression isn’t a strength. Will simply crush the sensitivities
                of those they view as inefficient, incompetent or lazy. Emotional displays are
                displays of weakness, and it’s easy to make enemies with this approach.
                """
    }
}

def myers_briggs_persona(code):
    return PERSONALITY_TYPES[code[0:4]]
