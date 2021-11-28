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
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer
from LearningAPI import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'profile', views.Profile, 'profile')
router.register(r'records', views.LearningRecordViewSet, 'record')
router.register(r'weights', views.LearningWeightViewSet, 'weight')
router.register(r'opportunities', views.OpportunityViewSet, 'opportunity')
router.register(r'capstones', views.CapstoneViewSet, 'capstone')
router.register(r'cohorts', views.CohortViewSet, 'cohort')
router.register(r'students', views.StudentViewSet, 'student')
router.register(r'courses', views.CourseViewSet, 'course')
router.register(r'books', views.BookViewSet, 'book')
router.register(r'projects', views.ProjectViewSet, 'project')
router.register(r'chapters', views.ChapterViewSet, 'chapter')
router.register(r'notes', views.ChapterNoteViewSet, 'note')
router.register(r'objectives', views.LearningObjectiveViewSet, 'learningobjective')


urlpatterns = [
    path('records/entries/<int:entryId>', views.LearningRecordViewSet.as_view({'delete': 'entries'}), name="entries"),
    path('', include(router.urls)),
    path('schema', get_schema_view(renderer_classes=[JSONOpenAPIRenderer])),
    path('accounts', views.register_user),
    path('accounts/verify', rest_views.obtain_auth_token, name='api-token-auth'),
    path('admin', admin.site.urls),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework'))

]
