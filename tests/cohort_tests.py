import json
from rest_framework import status
from rest_framework.test import APITestCase
from LearningAPI.models import Cohort


class CohortTests(APITestCase):
    def setUp(self):
        """
        Create a new user account
        """
        url = "/accounts"
        data = {
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "first_name": "Steve",
            "last_name": "Brownlee"
        }
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cohort(self):
        """
        Ensure we can create a new game.
        """
        # DEFINE GAME PROPERTIES
        url = "/cohorts"
        data = {
            "name": "Cohort 500",
            "slack_channel": "day-cohort-500",
            "start_date": "2029-09-27",
            "end_date": "2030-03-25",
            "break_start_date": "2029-12-17",
            "break_end_date": "2030-01-03"
        }

        # Make sure request is authenticated
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Initiate request and store response
        response = self.client.post(url, data, format='json')

        # Parse the JSON in the response body
        json_response = json.loads(response.content)

        # Assert that the game was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the properties on the created resource are correct
        self.assertEqual(json_response["name"], "Cohort 500")
        self.assertEqual(json_response["slack_channel"], "day-cohort-500")
        self.assertEqual(json_response["start_date"], "2029-09-27")
        self.assertEqual(json_response["end_date"], "2030-03-25")
        self.assertEqual(json_response["break_start_date"], "2029-12-17")
        self.assertEqual(json_response["break_end_date"], "2030-01-03")
        self.assertEqual(json_response["students"], [])
        self.assertEqual(json_response["instructors"], [])
