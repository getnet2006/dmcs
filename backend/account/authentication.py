# authentication.py
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to get the user
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        # Check password
        if user.check_password(password):
            # Check if password change is required
            if user.must_change_password:
                # Don't raise exception - just return None or set a flag
                # Store the user in request if available for later use
                if request:
                    request.pending_password_change_user = user
                return None  # Return None to indicate authentication failed

            return user

        return None
