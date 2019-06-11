import json
import requests

from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login as django_login

from accounts.models import User


CLIENT_ID = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
CLIENT_SECRET = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
REDIRECT_URI = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI
SCOPE = 'email%20profile%20openid'
VERIFY_AUTH_CODE_URI = 'https://www.googleapis.com/oauth2/v4/token'
GET_AUTH_USERINFO_URI = 'https://www.googleapis.com/oauth2/v3/userinfo'


def oauth2(request):
    if 'code' not in request.GET:
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                    '&client_id={}&redirect_uri={}&scope={}').format(
                        CLIENT_ID,
                        REDIRECT_URI,
                        SCOPE)
        return redirect(auth_uri)
    try:
        auth_code = request.GET.get('code')
        data = {
            'code': auth_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        # Verify code to get access_token
        resp = requests.post(url=VERIFY_AUTH_CODE_URI, data=data).json()
        # Use given access_token to get user's info
        resp = requests.get(url=GET_AUTH_USERINFO_URI, params={'access_token': resp['access_token']}).json()
        user = User.objects.get(email=resp['email'], is_superuser=True)
        django_login(request, user)
    except User.DoesNotExist as error:
        pass
    except Exception as error:
        pass
    return redirect("/admin")
