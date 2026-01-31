# Models
from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
# validation
from django.core.validators import validate_email
import secrets
from django.conf import settings
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


    def __str__(self):
        return self.user.email