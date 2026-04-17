from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "codename", "name"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Group
        fields = ["id", "name", "permission_ids"]

    def create(self, validated_data):
        permission_ids = validated_data.pop("permission_ids")
        role = Group.objects.create(**validated_data)
        role.permissions.set(permission_ids)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop("permission_ids", None)
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        if permission_ids is not None:
            instance.permissions.set(permission_ids)

        return instance


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Group.objects.all(), source="groups"
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "fname", "lname", "is_active", "roles"]


class UserCreateSerializer(serializers.ModelSerializer):
    role_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "fname", "lname", "password", "role_ids"]

    def create(self, validated_data):
        role_ids = validated_data.pop("role_ids")
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.groups.set(role_ids)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        refresh = RefreshToken.for_user(user)

        return {
            "user_id": user.id,
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        token = RefreshToken(self.validated_data["refresh"])
        token.blacklist()
