from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from users.models import OtpToken
from django.core.mail import send_mail
from django.utils import timezone


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
            OtpToken.create_new_opt_code(instance)
            instance.is_active = False
            instance.save()

            # Email credentials
            OtpToken.send_email(instance)