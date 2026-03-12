from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from users.models import OtpToken, UrlCodeOtp
import os
from dotenv import load_dotenv

load_dotenv()

User = get_user_model()

@shared_task
def send_password_reset_user_email(email):

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    token = UrlCodeOtp.create_url_code(user)
    link = f'http://{os.getenv("SITE_DOMAIN")}/{email}/{token}'
    send_mail(
        subject="Reset Password",
        message=f"Olá, {email}. Here is your link to change the password {link} . It expires in 5 minutes.",
        from_email="carlos704estudo@gmail.com",
        recipient_list=[email],
    )


@shared_task
def send_otp_code_to_user_email(user_id):
    user = User.objects.get(pk=user_id)

    token = OtpToken.create_new_opt_code(user)

    send_mail(
        subject="Login Token",
        message=f"Olá, {user.email}. Here is your vefication code {token}. It expires in 20 minutes.",
        from_email="carlos704estudo@gmail.com",
        recipient_list=[user.email],
    )