from django.shortcuts import render
from django.contrib.auth.models import Group, Permission
from rest_framework import viewsets
from .models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    AssignRoleSerializer,
    RoleSerializer,
    RoleCreateUpdateSerializer,
    PermissionSerializer,
    LoginSerializer,
    LogoutSerializer,
)
from .permissions import (
    IsAdminRole,
    IsAdminOrOwner,
    IsOwnerOnly,
    AdminUpdateRestriction,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.decorators import action


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    permission_classes = [DjangoModelPermissions]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RoleCreateUpdateSerializer
        return RoleSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     permission_classes = [UserAccessPermission]

#     def get_serializer_class(self):
#         if self.action == "create":
#             return UserCreateSerializer
#         return UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_permissions(self):
        """
        Apply different permissions based on the action.
        """
        # List and Create: Admin only
        if self.action in ["list", "create"]:
            permission_classes = [IsAdminRole]

        # Destroy: Admin only (nobody should delete users except admin)
        elif self.action == "destroy":
            permission_classes = [IsAdminRole]

        # Full update (PUT): Admin only
        elif self.action == "update":
            permission_classes = [IsAdminRole]

        # Retrieve (GET) and Partial update (PATCH): Admin or Owner
        elif self.action in ["retrieve", "partial_update"]:
            permission_classes = [IsAdminOrOwner]

        elif self.action in ["change_password", "me_change_password"]:
            # Use custom permission that only checks authentication
            permission_classes = [
                IsOwnerOnly,
                AdminUpdateRestriction,
            ]

        else:
            permission_classes = [IsAdminRole]  # Default to admin

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optimize queryset based on user role.
        """
        user = self.request.user

        # Admin sees all users
        if user.has_admin_role():
            return User.objects.all()

        # Non-admin only sees themselves
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_serializer_context(self):
        """Pass request to serializer context."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests, allowing owners to update their password.
        """
        instance = self.get_object()

        # If user is not admin and is updating password, ensure it's their own
        if not request.user.has_admin_role() and instance.id == request.user.id:
            # Optional: Add validation for old password
            if "password" in request.data:
                # add logic to validate old password
                pass

        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrOwner])
    def change_password(self, request, pk=None):
        """
        Dedicated endpoint for password change: POST /users/{id}/change_password/
        """
        user = self.get_object()

        # Check if requester is admin or the user themselves
        if not (request.user.has_admin_role() or user.id == request.user.id):
            return Response(
                {"detail": "You don't have permission to change this user's password."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate old password
        old_password = request.data.get("old_password")
        if not old_password or not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        new_password = request.data.get("new_password")
        if not new_password:
            return Response(
                {"detail": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Logged out successfully"})
