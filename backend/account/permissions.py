from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)


class IsAdminRole(permissions.BasePermission):
    """Admin only permission."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_admin_role()

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.has_admin_role()


class IsAdminOrOwner(permissions.BasePermission):
    """Admin can do anything, owner can view and PATCH only."""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.has_admin_role():
            return True

        # Owner access
        if obj.id == request.user.id:
            # Allow GET (retrieve) and PATCH (partial_update)
            return view.action in ["retrieve", "partial_update"]

        return False


class IsOwnerOnly(permissions.BasePermission):
    """Only the owner of the object can access."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.id == request.user.id


class AdminUpdateRestriction(permissions.BasePermission):
    """
    Restrict admin from updating certain fields after creation.
    """

    def has_object_permission(self, request, view, obj):
        # Only applies to admin users
        if not (request.user.is_authenticated and request.user.has_admin_role()):
            return True

        # For UPDATE and PARTIAL_UPDATE actions
        if view.action in ["update", "partial_update"]:
            # Check if trying to modify forbidden fields
            forbidden_fields = ["first_name", "last_name", "email"]

            # Get requested data from the request
            request_data = request.data

            for field in forbidden_fields:
                if field in request_data:
                    # Check if the field value is actually changing
                    current_value = getattr(obj, field)
                    new_value = request_data.get(field)

                    if str(current_value) != str(new_value):
                        # User is trying to change a forbidden field
                        return False

        return True


class CanChangeFirstLoginPassword(permissions.BasePermission):
    """
    Permission to change password on first login.
    User must be authenticated and have must_change_password=True.
    """

    def has_permission(self, request, view):
        logger.info(f"=== CanChangeFirstLoginPassword Debug ===")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"User: {request.user}")
        logger.info(
            f"Is authenticated: {request.user.is_authenticated if request.user else False}"
        )

        if not request.user or not request.user.is_authenticated:
            logger.warning("Failed: User not authenticated")
            return False

        logger.info(
            f"Has must_change_password attr: {hasattr(request.user, 'must_change_password')}"
        )
        if hasattr(request.user, "must_change_password"):
            logger.info(
                f"must_change_password value: {request.user.must_change_password}"
            )

        if not hasattr(request.user, "must_change_password"):
            logger.warning("Failed: User has no must_change_password attribute")
            return False

        if not request.user.must_change_password:
            logger.warning("Failed: must_change_password is False")
            return False

        logger.info("Permission granted!")
        return True
