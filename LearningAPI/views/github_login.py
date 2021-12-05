import os
import urllib.parse
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.urls import reverse
from django.shortcuts import redirect

class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client

    @property
    def callback_url(self):
        # use the same callback url as defined in your GitHub app, this url
        # must be absolute:
        return self.request.build_absolute_uri(reverse('github_callback'))


def github_callback(request):
    CALLBACK = os.getenv("LEARNING_GITHUB_CALLBACK")
    params = urllib.parse.urlencode(request.GET)
    return redirect(f'{CALLBACK}?{params}')
