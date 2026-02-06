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

    def create_new_opt_code(user):
        OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=20))
        code = OtpToken.objects.filter(user=user).last()
        return code.otp_code

    def send_email(user):
        code = OtpToken.objects.filter(user=user).last()

        # Email configuration
        subject = 'Email Verification'
        message = f'''
                    Olá, {user.email}. Here is your vefication code {code.otp_code}. It expires in 20 minutes.
                    Use the url to redirect back to website and verify your account.
                    https://teste/verify_email/{user.email}
        '''

        sender = 'carlos704estudo@gmail.com'
        receiver = [user.email]

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