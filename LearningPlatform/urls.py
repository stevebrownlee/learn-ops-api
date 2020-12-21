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
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from LearningAPI import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'nssusers', views.NssUserViewSet)
router.register(r'capstones', views.CapstoneViewSet)
router.register(r'proposalstatus', views.ProposalStatusViewSet)
router.register(r'cohorts', views.CohortViewSet)
router.register(r'nssusercohorts', views.NssUserCohortViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('register', views.register_user),
    path('login', views.login_user),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
