# Models
from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
# validation
from django.core.validators import validate_email
import secrets
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

# Manager
from users.managers import CustomUserBaseManager

class CustomUser(AbstractUser):
    
    username = None
    email = models.EmailField(unique=True, validators=[validate_email])
    is_verified = models.BooleanField(default=False)

    objects = CustomUserBaseManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def create_new_opt_code(self):
        if self.otp_expires_at < timezone.now():
            OtpToken.objects.create(user=self.user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            return self.otp_code
        else:
            new_opt = OtpToken.objects.filter(user=self.user).last().otp_code
            return  new_opt


    def send_email(self):
        if CustomUser.objects.filter(email=self.email).exists():
            code = OtpToken.objects.filter(user=self).last()

            # Email configuration
            subject = 'Email Verification'
            message = f'''
                        Olá, {self.email}. Here is your new vefication code {code.otp_code}. It expires in 5 minutes.
                        Use the url to redirect back to website and verify your account.
                        https://teste/verify_email/{self.email}
            '''

            sender = 'carlos704estudo@gmail.com'
            receiver = [self.email]

            # send Email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False
            )
        else:
            code = OtpToken.objects.filter(user=self).last()

            # Email configuration
            subject = 'Email Verification'
            message = f'''
                        Olá, {self.email}. Here is your vefication code {code.otp_code}. It expires in 5 minutes.
                        Use the url to redirect back to website and verify your account.
                        https://teste/verify_email/{self.email}
            '''

            sender = 'carlos704estudo@gmail.com'
            receiver = [self.email]

            # send Email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False
            )


    def __str__(self):
        return self.user.email