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
            OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            instance.is_active = False
            instance.save()

            # Email credentials
            otp = OtpToken.objects.filter(user=instance).last()
            subject = 'Email Verification'
            message = f'''
                        Olá, {instance.email}. Here is your vefication code {otp.otp_code}.
                        It expires in {otp.otp_expires_at - timezone.now()} minutes.
                        Use the url to redirect back to website and verify your account.
                        https://teste/verify_email/{instance.email}
            '''

            sender = 'carlos704estudo@gmail.com'
            receiver = [instance.email]

            # send Email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False
            )