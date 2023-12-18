from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from LearningAPI.models.people import Cohort, NssUserCohort, NssUser, StudentPersonality
from LearningAPI.views.profile_view import ProfileSerializer

class ProfileViewTestCase(TestCase):
    def setUp(self):
        # Create a user and log them in
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_profile_authenticated(self):
        # Test getting the profile of an authenticated user
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['person']['first_name'], self.user.first_name)
        self.assertEqual(response.data['person']['last_name'], self.user.last_name)

    def test_get_profile_unauthenticated(self):
        # Test getting the profile when the user is not authenticated
        self.client.force_authenticate(user=None)
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_staff_user(self):
        # Test getting the profile of a staff user
        self.user.is_staff = True
        self.user.save()
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['staff'])

    def test_get_profile_with_cohort(self):
        # Test getting the profile with a specified cohort parameter
        cohort = Cohort.objects.create(name='Test Cohort')
        response = self.client.get(f'/profile/?cohort={cohort.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['person']['active_cohort'], cohort.id)

    def test_get_profile_mimic_mode(self):
        # Test getting the profile in mimic mode
        response = self.client.get('/profile/?mimic=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse('personality' in response.data)  # Personality info should be excluded

    # Add more test cases to cover different scenarios as needed

    def tearDown(self):
        # Clean up after the test
        self.user.delete()
