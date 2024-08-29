import json
import time
import os
import requests
from requests.exceptions import ConnectionError

from LearningAPI.models.people import NssUser

class SlackChannel(object):
    """ This class is used to create a Slack channel for a student team """
    def __init__(self, name):
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.channel_payload = {
            "name": name,
            "token": os.getenv("SLACK_BOT_TOKEN")
        }

    def create(self, members):
        # Create a Slack channel with the given name
        res = requests.post("https://slack.com/api/conversations.create", timeout=10, data=self.channel_payload, headers=self.headers)
        channel_res = res.json()

        # Create a set of Slack IDs for the members to be added to the channel
        member_slack_ids = set()
        for member_id in members:
            member = NssUser.objects.get(pk=member_id)
            if member.slack_handle is not None:
                member_slack_ids.add(member.slack_handle)

        # Create a payload to invite students and instructors to the channel
        invitation_payload = {
            "channel": channel_res["channel"]["id"],
            "users": ",".join(list(member_slack_ids)),
            "token": os.getenv("SLACK_BOT_TOKEN")
        }

        # Invite students and instructors to the channel
        requests.post("https://slack.com/api/conversations.invite", timeout=10, data=invitation_payload, headers=self.headers)

        # Return the channel ID for the team
        return channel_res["channel"]["id"]




class GithubRequest(object):
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "Accept: application/vnd.github+json",
            "User-Agent": "nss/ticket-migrator",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f'Bearer {os.getenv("GITHUB_TOKEN")}'
        }

    def get(self, url):
        return self.request_with_retry(
            lambda: requests.get(url=url, headers=self.headers))

    def put(self, url, data):
        json_data = json.dumps(data)

        return self.request_with_retry(
            lambda: requests.put(url=url, data=json_data, headers=self.headers))

    def post(self, url, data):
        json_data = json.dumps(data)

        try:
            result = self.request_with_retry(
                lambda: requests.post(url=url, data=json_data, headers=self.headers))

            return result

        except TimeoutError:
            print("Request timed out. Trying next...")

        except ConnectionError:
            print("Request timed out. Trying next...")

        return None

    def request_with_retry(self, request):
        retry_after_seconds = 1800
        number_of_retries = 0

        response = request()

        while response.status_code == 403 and number_of_retries <= 10:
            number_of_retries += 1

            os.system('cls' if os.name == 'nt' else 'clear')
            self.sleep_with_countdown(retry_after_seconds)

            response = request()

        return response

    def sleep_with_countdown(self, countdown_seconds):
        ticks = countdown_seconds * 2
        for count in range(ticks, -1, -1):
            if count:
                time.sleep(0.5)

