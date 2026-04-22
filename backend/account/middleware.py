from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from rest_framework import status


class MustChangePasswordMiddleware:
    """
    Middleware to block access to other endpoints if user must change password.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Safely check if user attribute exists
        user = getattr(request, "user", None)

        # Skip if no user (not authenticated) or user is anonymous
        if user and user.is_authenticated and hasattr(user, "must_change_password"):
            # Skip admin paths (important!)
            if request.path.startswith("/admin/"):
                return self.get_response(request)

            # Skip password change endpoint and login endpoints
            skip_paths = [
                "/api/users/change_first_login_password/",
                "/api/login/",
                "/api/token/",
                "/api/token/refresh/",
            ]

            if any(request.path.endswith(path) for path in skip_paths):
                return self.get_response(request)

            # Block access if password change is required
            if user.must_change_password:
                return JsonResponse(
                    {
                        "detail": "You must change your password before accessing other endpoints."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        return self.get_response(request)
