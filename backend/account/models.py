from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    def has_admin_role(self):
        """Check if user has Admin role"""
        return self.groups.filter(name="Admin").exists()

    # Optional: cache this for performance
    @property
    def is_admin(self):
        return self.has_admin_role()

    def __str__(self):
        return self.username
