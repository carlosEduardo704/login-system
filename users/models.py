from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    
    username = None

    def __str__(self):
        return self.email