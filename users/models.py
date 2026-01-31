from django.db import models
from django.core.validators import validate_email
from django.db import models
from django.contrib.auth.models import AbstractUser

# Manager
from users.managers import CustomUserBaseManager

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, validators=[validate_email])

    objects = CustomUserBaseManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email