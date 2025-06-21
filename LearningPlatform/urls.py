"""LearningPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from rest_framework.authtoken import views as rest_views
from LearningAPI.views.github import views as github_views
from LearningAPI import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'assessments', views.StudentAssessmentView, 'assessment')
router.register(r'bookassessments', views.BookAssessmentView, 'bookassessment')
router.register(r'books', views.BookViewSet, 'book')
router.register(r'capstones', views.CapstoneViewSet, 'capstone')
router.register(r'cohortinfo', views.CohortInfoViewSet, 'info')
router.register(r'events', views.CohortEventsViewSet, 'cohortevent')
router.register(r'cohorts', views.CohortViewSet, 'cohort')
router.register(r'coreskillrecords', views.CoreSkillRecordViewSet, 'coreskillrecord')
router.register(r'coreskills', views.CoreSkillViewSet, 'coreskill')
router.register(r'courses', views.CourseViewSet, 'course')
router.register(r'notes', views.StudentNoteViewSet, 'note')
router.register(r'notetypes', views.StudentNoteTypeViewSet, 'notetypes')
router.register(r'objectives', views.LearningObjectiveViewSet, 'learningobjective')
router.register(r'opportunities', views.OpportunityViewSet, 'opportunity')
router.register(r'personalities', views.PersonalityView, 'person')
router.register(r'profile', views.Profile, 'profile')
router.register(r'projects', views.ProjectViewSet, 'project')
router.register(r'proposalstatuses', views.ProposalStatusView, 'proposalstatus')
router.register(r'personality', views.StudentPersonalityViewSet, 'personality')
router.register(r'records', views.LearningRecordViewSet, 'record')
router.register(r'statuses', views.AssessmentStatusView, 'status')
router.register(r'students', views.StudentViewSet, 'student')
router.register(r'studenttags', views.StudentTagViewSet, 'studenttag')
router.register(r'tags', views.TagViewSet, 'tag')
router.register(r'teams', views.TeamMakerView, 'team_maker')
router.register(r'timelines', views.TimelineView, 'timeline')
router.register(r'weights', views.LearningWeightViewSet, 'weight')
router.register(r'foundations', views.FoundationsViewSet, 'foundation')


urlpatterns = [
    path('', include(router.urls)),
    path('records/entries/<int:entry_id>', views.LearningRecordViewSet.as_view({'delete': 'entries'}), name="entries"),
    path('queries/popular', views.popular_queries, name='popular-queries'),

    path('accounts', views.register_user),
    path('notify', views.notify, name='notify'),
    path('accounts/verify', rest_views.obtain_auth_token, name='api-token-auth'),

    path('auth/', include('dj_rest_auth.urls')),
    path('auth/github', views.GithubLogin.as_view(), name='github_login'),
    path('auth/github/callback', views.github_login.github_callback, name='github_callback'),
    path('auth/github/url', github_views.oauth2_login),

    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
    path('admin', admin.site.urls),
]
