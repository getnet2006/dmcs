from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "codename", "name"]
        ordering = ["id"]


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
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "roles",
        ]
        read_only_fields = [
            "id",
            "roles",
            "email",
            "first_name",
            "last_name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If this is an update operation (instance exists)
        if self.instance:
            request = self.context.get("request")

            # If admin is updating an existing user
            if (
                request
                and request.user.is_authenticated
                and request.user.has_admin_role()
            ):
                # Make first_name and last_name read-only
                self.fields["first_name"].read_only = True
                self.fields["last_name"].read_only = True
                self.fields["email"].read_only = True

    def update(self, instance, validated_data):
        """
        Custom update logic: Only roles and is_active can be updated by admin.
        """
        request = self.context.get("request")

        # If admin is updating
        if request and request.user.has_admin_role():
            # Only allow these fields to be updated
            allowed_update_fields = ["is_active", "roles"]

            for field in allowed_update_fields:
                if field in validated_data:
                    setattr(instance, field, validated_data[field])

            # Save without touching other fields
            instance.save()
            return instance

        # Non-admin updates (owners) - only allow PATCH for certain fields
        return super().update(instance, validated_data)


class UserCreateSerializer(serializers.ModelSerializer):
    role_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role_ids",
        ]

    def create(self, validated_data):
        role_ids = validated_data.pop("role_ids")
        password = validated_data.pop("password")

        # Validate that all role_ids exist
        if not Group.objects.filter(id__in=role_ids).count() == len(role_ids):
            raise serializers.ValidationError(
                {"role_ids": "One or more role IDs do not exist."}
            )
        admin_group = Group.objects.filter(name="Admin").first()
        is_admin = admin_group and admin_group.id in role_ids

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.groups.set(role_ids)
        user.must_change_password = True
        if is_admin:
            user.is_staff = True
        user.save()
        return user


class AssignRoleSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()

    def validate_role_id(self, value):
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("Role does not exist")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        # Check if password change is required
        if user.must_change_password:
            refresh = RefreshToken.for_user(user)
            # Add claim to indicate password change required
            refresh["must_change_password"] = True
            print(refresh["must_change_password"])
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "must_change_password": user.must_change_password,
                "user_id": user.id,
            }

        refresh = RefreshToken.for_user(user)

        return {
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "must_change_password": user.must_change_password,
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        token = RefreshToken(self.validated_data["refresh"])
        token.blacklist()
