import json, time, os, logging, requests
import structlog
from functools import wraps
import time
import uuid
from requests.exceptions import ConnectionError

from LearningAPI.models.people import NssUser

# Get a logger instance
logger = structlog.get_logger("LearningAPI")

def get_logger(module_name):
    """Get a logger for a specific module"""
    return structlog.get_logger(f"LearningAPI.{module_name}")

def bind_request_context(logger, request):
    """Bind common request context to a logger"""
    user_id = getattr(request.auth, 'user_id', None) if hasattr(request, 'auth') else None
    username = getattr(request.auth.user, 'username', None) if hasattr(request, 'auth') and hasattr(request.auth, 'user') else None

    return logger.bind(
        request_id=str(uuid.uuid4()),
        user_id=user_id,
        username=username,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        path=request.path,
        method=request.method,
    )

def log_action(action_type):
    """Decorator to log actions with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            module_name = self.__class__.__module__.split('.')[-1]
            action_logger = get_logger(module_name)
            action_logger = bind_request_context(action_logger, request)

            # Extract relevant IDs from kwargs or request
            pk = kwargs.get('pk')

            # Log the start of the action
            action_logger.info(
                f"{action_type}_started",
                view=self.__class__.__name__,
                action=func.__name__,
                pk=pk,
            )

            start_time = time.time()
            try:
                result = func(self, request, *args, **kwargs)

                # Log successful completion
                action_logger.info(
                    f"{action_type}_completed",
                    view=self.__class__.__name__,
                    action=func.__name__,
                    pk=pk,
                    duration_ms=int((time.time() - start_time) * 1000),
                    status_code=getattr(result, 'status_code', None),
                )
                return result
            except Exception as e:
                # Log exception
                action_logger.exception(
                    f"{action_type}_failed",
                    view=self.__class__.__name__,
                    action=func.__name__,
                    pk=pk,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error=str(e),
                )
                raise
        return wrapper
    return decorator

class SlackAPI(object):
    """ This class is used to create a Slack channel for a student team """
    def __init__(self):
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def send_message(self, channel, text):
        """Send a message to a Slack channel"""
        # Log the start of message sending
        logger.info(
            "slack_message_send_started",
            channel=channel,
            message_length=len(text)
        )

        # Configure the config for the Slack message
        channel_payload = {
            "text": text,
            "token": os.getenv("SLACK_BOT_TOKEN"),
            "channel": channel
        }

        # Log the request
        logger.info(
            "slack_api_request_sent",
            api_endpoint="chat.postMessage",
            channel=channel
        )

        try:
            response = requests.post(
                url="https://slack.com/api/chat.postMessage",
                data=channel_payload,
                headers=self.headers,
                timeout=10
            )
            response_json = response.json()

            # Log the response
            logger.info(
                "slack_api_response_received",
                api_endpoint="chat.postMessage",
                status_code=response.status_code,
                response_ok=response_json.get("ok", False),
                response=response_json
            )

            if not response_json.get("ok", False):
                error_msg = response_json.get("error", "unknown_error")
                logger.error(
                    "slack_message_send_failed",
                    channel=channel,
                    error=error_msg,
                    full_response=response_json
                )
            else:
                logger.info(
                    "slack_message_sent_successfully",
                    channel=channel,
                    timestamp=response_json.get("ts")
                )

            return response_json

        except requests.exceptions.RequestException as e:
            logger.exception(
                "slack_api_request_failed",
                api_endpoint="chat.postMessage",
                channel=channel,
                error=str(e)
            )
            raise


    def delete_channel(self, channel_id):
        """Archive/delete a Slack channel"""
        # Log the start of channel deletion
        logger.info(
            "slack_channel_deletion_started",
            channel_id=channel_id
        )

        channel_payload = {
            "channel": channel_id,
            "token": os.getenv("SLACK_BOT_TOKEN")
        }

        # Log the request
        logger.info(
            "slack_api_request_sent",
            api_endpoint="conversations.archive",
            channel_id=channel_id
        )

        try:
            # Archive the Slack channel
            res = requests.post(
                "https://slack.com/api/conversations.archive",
                timeout=10,
                data=channel_payload,
                headers=self.headers
            )
            channel_res = res.json()

            # Log the response
            logger.info(
                "slack_api_response_received",
                api_endpoint="conversations.archive",
                status_code=res.status_code,
                response_ok=channel_res.get("ok", False),
                response=channel_res
            )

            if not channel_res.get("ok", False):
                error_msg = channel_res.get("error", "unknown_error")
                logger.error(
                    "slack_channel_deletion_failed",
                    channel_id=channel_id,
                    error=error_msg,
                    full_response=channel_res
                )
            else:
                logger.info(
                    "slack_channel_deleted_successfully",
                    channel_id=channel_id
                )

            return channel_res['ok']

        except requests.exceptions.RequestException as e:
            logger.exception(
                "slack_api_request_failed",
                api_endpoint="conversations.archive",
                channel_id=channel_id,
                error=str(e)
            )
            raise

    def create_channel(self, name, members):
        """Create a Slack channel for a student team"""
        # Log the start of channel creation
        logger.info(
            "slack_channel_creation_started",
            channel_name=name,
            member_count=len(members),
            member_ids=members
        )

        channel_payload = {
            "name": name,
            "token": os.getenv("SLACK_BOT_TOKEN")
        }

        # Log the channel creation request
        logger.info(
            "slack_api_request_sent",
            api_endpoint="conversations.create",
            channel_name=name,
            payload_keys=list(channel_payload.keys())
        )

        # Create a Slack channel with the given name
        try:
            res = requests.post(
                "https://slack.com/api/conversations.create",
                timeout=10,
                data=channel_payload,
                headers=self.headers
            )
            channel_res = res.json()

            # Log the full response
            logger.info(
                "slack_api_response_received",
                api_endpoint="conversations.create",
                status_code=res.status_code,
                response_ok=channel_res.get("ok", False),
                response=channel_res
            )

            if not channel_res["ok"]:
                error_msg = channel_res.get("error", "unknown_error")
                logger.error(
                    "slack_channel_creation_failed",
                    channel_name=name,
                    error=error_msg,
                    full_response=channel_res
                )
                raise Exception(json.dumps(channel_res))

            channel_id = channel_res["channel"]["id"]
            logger.info(
                "slack_channel_created_successfully",
                channel_name=name,
                channel_id=channel_id
            )

        except requests.exceptions.RequestException as e:
            logger.exception(
                "slack_api_request_failed",
                api_endpoint="conversations.create",
                error=str(e)
            )
            raise

        # Create a set of Slack IDs for the members to be added to the channel
        member_slack_ids = set()
        members_without_slack = []

        for member_id in members:
            try:
                member = NssUser.objects.get(pk=member_id)
                if member.slack_handle is not None:
                    member_slack_ids.add(member.slack_handle)
                else:
                    members_without_slack.append({
                        "id": member_id,
                        "name": getattr(member, 'full_name', 'unknown')
                    })
            except NssUser.DoesNotExist:
                logger.warning(
                    "member_not_found",
                    member_id=member_id
                )

        # Log member information
        logger.info(
            "slack_channel_members_prepared",
            channel_id=channel_id,
            total_members_requested=len(members),
            members_with_slack_handles=len(member_slack_ids),
            members_without_slack_handles=len(members_without_slack),
            slack_ids=list(member_slack_ids),
            members_without_slack=members_without_slack
        )

        # Create a payload to invite students and instructors to the channel
        invitation_payload = {
            "channel": channel_id,
            "users": ",".join(list(member_slack_ids)),
            "token": os.getenv("SLACK_BOT_TOKEN")
        }

        # Log the invitation request
        logger.info(
            "slack_api_request_sent",
            api_endpoint="conversations.invite",
            channel_id=channel_id,
            user_count=len(member_slack_ids),
            users=",".join(list(member_slack_ids))
        )

        # Invite students and instructors to the channel
        try:
            invite_res = requests.post(
                "https://slack.com/api/conversations.invite",
                timeout=10,
                data=invitation_payload,
                headers=self.headers
            )
            invite_res_json = invite_res.json()

            # Log the full invitation response
            logger.info(
                "slack_api_response_received",
                api_endpoint="conversations.invite",
                status_code=invite_res.status_code,
                response_ok=invite_res_json.get("ok", False),
                response=invite_res_json
            )

            # Check if invitation was successful
            if not invite_res_json.get("ok", False):
                error_msg = invite_res_json.get("error", "unknown_error")
                logger.error(
                    "slack_invitation_failed",
                    channel_id=channel_id,
                    error=error_msg,
                    full_response=invite_res_json,
                    attempted_users=",".join(list(member_slack_ids))
                )
            else:
                logger.info(
                    "slack_invitation_successful",
                    channel_id=channel_id,
                    invited_user_count=len(member_slack_ids)
                )

        except requests.exceptions.RequestException as e:
            logger.exception(
                "slack_api_request_failed",
                api_endpoint="conversations.invite",
                channel_id=channel_id,
                error=str(e)
            )

        # Log successful completion
        logger.info(
            "slack_channel_creation_completed",
            channel_name=name,
            channel_id=channel_id
        )

        # Return the channel ID for the team
        return channel_id


class GithubRequest(object):
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "nss/ticket-migrator",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f'Bearer {os.getenv("GITHUB_TOKEN")}'
        }

    def create_repository(self, source_url: str, student_org_url: str, repo_name: str, project_name: str) -> requests.Response:
        """Create a repository for a student team

        Args:
            source_url (str): The URL of the source repository
            student_org_url (str): The URL of the student organization
            repo_name (str): The name of the repository
            project_name (str): The name of the project

        Returns:
            requests.Response: The response from the GitHub API
        """

        # Split the full URL on '/' and get the last two items
        ( org, repo, ) = source_url.split('/')[-2:]

        student_org_name = student_org_url.split("/")[-1]

        # Construct request body for creating the repository
        request_body = {
            "owner": student_org_name,
            "name": repo_name,
            "description": f"This is your client-side repository for the {project_name} sprint(s).",
            "include_all_branches": False,
            "private": False
        }

        # Create the repository
        response = self.post(url=f'https://api.github.com/repos/{org}/{repo}/generate', data=request_body)

        return response

    def assign_student_permissions(self, student_org_name: str, repo_name: str, student: NssUser, permission: str = "write") -> requests.Response:
        """Assign write permissions to a student for a repository

        Args:
            student_org_name (str): The name of the student organization
            repo_name (str): The name of the repository
            student (NSSUser): The student to assign permissions to

        Returns:
            requests.Response: The response from the GitHub API
        """

        # Construct request body for assigning permissions to the student
        request_body = { "permission":permission }

        # Assign the student write permissions to the repository
        response = self.put(
            url=f'https://api.github.com/repos/{student_org_name}/{repo_name}/collaborators/{student.github_handle}',
            data=request_body
        )

        if response.status_code != 204:
            logger = logging.getLogger("LearningPlatform")
            logger.exception(
                "Error: %s was not added as a collaborator to the assessment repository.",
                student.full_name
            )

        return response


    def get(self, url):
        return self.request_with_retry(lambda: requests.get(url=url, headers=self.headers, timeout=10))

    def put(self, url, data):
        json_data = json.dumps(data)

        return self.request_with_retry(lambda: requests.put(url=url, data=json_data, headers=self.headers, timeout=10))

    def post(self, url, data):
        json_data = json.dumps(data)

        try:
            result = self.request_with_retry(lambda: requests.post(url=url, data=json_data, headers=self.headers, timeout=10))
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


