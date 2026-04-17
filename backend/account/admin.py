from django.contrib import admin
from .models import User
from django.contrib.auth.models import Permission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "fname",
        "lname",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("id",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "codename")
    search_fields = ("name", "codename")
    ordering = ("id",)
