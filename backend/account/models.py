from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)

    REQUIRED_FIELDS = ["fname", "lname"]

    def __str__(self):
        return self.username
