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


class IsAllowedToAddDocument(permissions.BasePermission):
    """
    Permission to check if the user can add a document to an application.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm("consumer.add_document_to_application")


class IsAllowedToAddSubscription(permissions.BasePermission):
    """
    Permission to check if the user can add a subscription to an application.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm("consumer.add_subscription_to_application")
