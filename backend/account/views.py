from django.shortcuts import render
from django.contrib.auth.models import Group, Permission
from rest_framework import viewsets
from .models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    RoleSerializer,
    RoleCreateUpdateSerializer,
    PermissionSerializer,
    LoginSerializer,
    LogoutSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import DjangoModelPermissions


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RoleCreateUpdateSerializer
        return RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer


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
