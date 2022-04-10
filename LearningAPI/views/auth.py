import json
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from LearningAPI.models.people import NssUser, Cohort, NssUserCohort


@csrf_exempt
def login_user(request):
    '''Handles the authentication of a user

    Method arguments:
      request -- The full HTTP request object
    '''

    req_body = json.loads(request.body.decode())

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # Use the built-in authenticate method to verify
        username = req_body['username']
        password = req_body['password']
        authenticated_user = authenticate(username=username, password=password)

        # If authentication was successful, respond with their token
        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)
            data = json.dumps({"valid": True, "token": token.key})
            return HttpResponse(data, content_type='application/json')

        else:
            # Bad login details were provided. So we can't log the user in.
            data = json.dumps({"valid": False})
            return HttpResponse(data, content_type='application/json')


@csrf_exempt
def register_user(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''
    # Load the JSON string of the request body into a dict
    req_body = json.loads(request.body.decode())

    is_new_instructor = 'level' in req_body and req_body['level'] == 'instructor'

    # Create a new user by invoking the `create_user` helper method
    # on Django's built-in User model
    new_user = User.objects.create_user(
        username=req_body['email'],
        email=req_body['email'],
        password=req_body['password'],
        first_name=req_body['first_name'],
        last_name=req_body['last_name'],
        is_staff=is_new_instructor
    )

    nss_user = NssUser.objects.create(
        slack_handle=req_body['slackHandle'] if 'slackHandle' in req_body else None,
        github_handle=req_body['githubHandle'] if 'githubHandle' in req_body else None,
        user=new_user
    )

    # Commit the user to the database by saving it
    nss_user.save()

    if is_new_instructor:
        nss_user.user.groups.add(Group.objects.get(name='Instructors'))
    else:

        try:
            cohort = Cohort.objects.get(pk=req_body['cohort'])
            NssUserCohort.objects.get(cohort=cohort, nss_user=nss_user)

            return Response(
                {'message': 'Person is already assigned to cohort'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except NssUserCohort.DoesNotExist as ex:
            relationship = NssUserCohort()
            relationship.cohort = cohort
            relationship.nss_user = nss_user

            relationship.save()
        except Cohort.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        nss_user.user.groups.add(Group.objects.get(name='Students'))

    # Use the REST Framework's token generator on the new user account
    token = Token.objects.create(user=new_user)

    # Return the token to the client
    data = json.dumps({"token": token.key})
    return HttpResponse(data, content_type='application/json', status=status.HTTP_201_CREATED)
