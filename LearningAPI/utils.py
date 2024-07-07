import json
import time
import os
import requests
from requests.exceptions import ConnectionError


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
            remaining = str(int(0.5 + count / 2)).rjust(2)
            spinner = ['-', '/', '|', '\\'][count % 4]

            progress = '=' * (ticks - count)
            if count:
                progress = progress[:-1] + '>'

            print(
                f'[bright_white]  {spinner} [{progress.ljust(ticks)}] {remaining}[/bright_white]', end='\r')

            if count:
                time.sleep(0.5)

        print()
