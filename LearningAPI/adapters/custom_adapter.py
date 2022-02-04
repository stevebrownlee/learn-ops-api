import json
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpResponse
from allauth.exceptions import ImmediateHttpResponse
from django.core.exceptions import BadRequest



class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).
        """

        if sociallogin.account.extra_data['name'] is None:
            data = json.dumps({
                "message": "You have not provided your name in your Github account profile. Visit https://github.com/settings/profile to update your profile.",
                "next": "https://github.com/settings/profile"
            })
            raise ImmediateHttpResponse(
                HttpResponse(
                    content=data,
                    status=500,
                    content_type="application/json"
                )
            )
            # raise ImmediateHttpResponse('Deleting subcribers is not allowed!')
            # raise BadRequest("You have not provided your name in your Github account profile. Visit https://github.com/settings/profile to update your profile.")
