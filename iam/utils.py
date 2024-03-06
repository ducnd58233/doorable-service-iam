from threading import Thread
from typing import Dict
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = settings.CUSTOM_REDIRECT


class EmailThread(Thread):
    def __init__(self, email: Dict):
        super(EmailThread, self).__init__()
        self.email = email

    def run(self):
        send_mail(
            subject=self.email["subject"],
            message=self.email["message"],
            from_email=self.email["from_email"],
            recipient_list=self.email["recipient_list"],
        )
