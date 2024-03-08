from threading import Thread
from typing import Dict
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = settings.CUSTOM_REDIRECT
