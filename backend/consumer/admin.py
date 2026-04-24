from django.contrib import admin
from .models import Consumer, ConsumerOnboardingStage, Application, Subscription


@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(ConsumerOnboardingStage)
class ConsumerOnboardingStageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "order")
    search_fields = ("name",)
    ordering = ("order",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "consumer",
        "user",
        "current_stage",
        "source_ip",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "consumer__name", "user__username")
    ordering = ("-created_at",)
