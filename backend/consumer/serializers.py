from rest_framework import serializers
from .models import (
    Consumer,
    Application,
    ConsumerCommunication,
    ConsumerOnboardingStage,
)
from documents.models import Document


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
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class ConsumerOnboardingStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerOnboardingStage
        fields = "__all__"


class ConsumerCommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerCommunication
        fields = "__all__"
