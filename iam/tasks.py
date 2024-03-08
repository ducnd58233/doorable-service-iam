from celery import shared_task
from templated_mail.mail import BaseEmailMessage


@shared_task
def send_email(message):
    email = BaseEmailMessage(template_name="emails/auth.html", context=message)
    email.send(message["recipient_list"])
