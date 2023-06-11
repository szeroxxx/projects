from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
import requests
from django.conf import settings


class EmailAuthBackend(ModelBackend):
    def authenticate(self, username=None, token=None, portal_username=None):
        try:
            user = User.objects.get(username=username, is_active=True)
            url = settings.EC_PORTAL_DOMAIN + "verify_token/"
            response = requests.request("POST", url, data={"token":token, "usernmame":username, "portal_username":portal_username})
            response = response.json()
            if user and response["code"] == 1:
                return user
        except User.DoesNotExist:
            return None
