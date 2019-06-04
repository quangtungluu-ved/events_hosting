from django.db import models
from django.contrib.auth.models import AbstractUser

# Create models from here.


class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
