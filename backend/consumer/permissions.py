from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission for the user who created the consumer.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.created_by == request.user


class IsAdminRole(permissions.BasePermission):
    """
    Permission for users with admin role.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name="Admin").exists()
