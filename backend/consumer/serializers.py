from rest_framework import serializers
from .models import (
    Consumer,
    Application,
    ConsumerCommunication,
    ConsumerOnboardingStage,
    Subscription,
)
from documents.models import Document
from account.models import User


# Consumer related serializers
class ApplicationNestedSerializer(serializers.ModelSerializer):
    current_stage = serializers.StringRelatedField()

    class Meta:
        model = Application
        fields = ["name", "current_stage"]


class ConsumerCreateUpdateSerializer(serializers.ModelSerializer):
    applications = ApplicationNestedSerializer(many=True, read_only=True)
    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Consumer
        exclude = ["created_at", "updated_at"]  # Exclude these fields

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)

        # Define the order of fields in the response
        ordered_fields = [
            "id",
            "name",
            "owner_work_unit",
            "purpose_of_usage",
            "consumer_type",
            "email",
            "phone",
            "created_by",
            "applications",
        ]

        # Reorder the fields dictionary according to ordered_fields
        ordered_fields_dict = {}
        for field_name in ordered_fields:
            if field_name in fields:
                ordered_fields_dict[field_name] = fields[field_name]

        # Add any remaining fields that weren't in ordered_fields
        for field_name, field in fields.items():
            if field_name not in ordered_fields:
                ordered_fields_dict[field_name] = field

        return ordered_fields_dict


class ConsumerDetailSerializer(serializers.ModelSerializer):
    applications = ApplicationNestedSerializer(many=True, read_only=True)
    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Consumer
        fields = [
            "id",
            "name",
            "owner_work_unit",
            "purpose_of_usage",
            "consumer_type",
            "email",
            "phone",
            "created_by",
            "applications",
        ]


# Application related serializers
class DocumentNestedSerializer(serializers.ModelSerializer):
    category = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Document
        fields = ["document_id", "name", "category"]


class SubscriptionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "name"]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    consumer_name = serializers.ReadOnlyField(source="consumer.name")
    created_by = serializers.ReadOnlyField(source="user.username")
    current_stage_name = serializers.ReadOnlyField(source="current_stage.name")
    documents = DocumentNestedSerializer(many=True, read_only=True)
    subscriptions = SubscriptionNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "name",
            "consumer_name",
            "created_by",
            "current_stage_name",
            "source_ip",
            "description",
            "last_stage_updated_at",
            "created_at",
            "updated_at",
            "documents",
            "subscriptions",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_stage_updated_at"]


class ApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    consumer = serializers.PrimaryKeyRelatedField(queryset=Consumer.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Application
        fields = [
            "id",
            "name",
            "consumer",
            "user",
            "current_stage",
            "source_ip",
            "description",
            "last_stage_updated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "last_stage_updated_at",
            "documents",
            "subscriptions",
        ]

    def update(self, instance, validated_data):
        new_stage = validated_data.get("current_stage")
        if new_stage and new_stage != instance.current_stage:
            from django.utils import timezone

            instance.last_stage_updated_at = timezone.now()

        return super().update(instance, validated_data)


class ConsumerOnboardingStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerOnboardingStage
        fields = "__all__"


class ConsumerCommunicationSerializer(serializers.ModelSerializer):
    application_name = serializers.ReadOnlyField(source="application.name")
    created_by = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = ConsumerCommunication
        fields = [
            "id",
            "application_name",
            "remark",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConsumerCommunicationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerCommunication
        fields = [
            "id",
            "application",
            "remark",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
