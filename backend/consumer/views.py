from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django.utils import timezone
from .models import (
    Consumer,
    Application,
    ConsumerCommunication,
    ConsumerOnboardingStage,
    Subscription,
)
from .serializers import (
    ConsumerDetailSerializer,
    ConsumerCreateUpdateSerializer,
    ApplicationCreateUpdateSerializer,
    ApplicationDetailSerializer,
    ConsumerCommunicationSerializer,
    ConsumerOnboardingStageSerializer,
)
from documents.models import Document
from account.models import User
from .permissions import (
    IsOwner,
    IsAdminRole,
    IsAllowedToAddDocument,
    IsAllowedToAddSubscription,
)


class ConsumerViewSet(viewsets.ModelViewSet):
    queryset = Consumer.objects.all()
    permission_classes = [
        IsAuthenticated,
        DjangoModelPermissions,
    ]
    http_method_names = ["get", "post", "put", "patch"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ConsumerDetailSerializer
        return ConsumerCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            self.permission_classes = [IsOwner | IsAdminRole]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def my_consumers(self, request):
        """Get consumers created by the current user"""
        consumers = Consumer.objects.filter(created_by=request.user)
        serializer = ConsumerDetailSerializer(consumers, many=True)
        return Response(serializer.data)


class StageViewSet(viewsets.ModelViewSet):
    queryset = ConsumerOnboardingStage.objects.all()
    serializer_class = ConsumerOnboardingStageSerializer
    http_method_names = ["get"]


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    A viewset for Application instances.
    """

    queryset = (
        Application.objects.all()
        .select_related("consumer", "user", "current_stage")
        .prefetch_related("documents", "subscriptions")
    )
    http_method_names = ["get", "post", "put", "patch"]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return ApplicationDetailSerializer
        return ApplicationCreateUpdateSerializer

    def perform_create(self, serializer):
        # add current stage as the first stage of the onboarding process
        current_stage = ConsumerOnboardingStage.objects.order_by("order").first()
        serializer.save(user=self.request.user, current_stage=current_stage)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAllowedToAddDocument],
    )
    def add_document(self, request, pk=None):
        application = self.get_object()
        document_id = request.data.get("document_id")

        # check if the document_id is provided
        if not document_id:
            return Response(
                {"error": "Document ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # check if the document exists
        if not Document.objects.filter(document_id=document_id).exists():
            return Response(
                {"error": "Document with this ID does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if the document is already associated with the application
        if application.documents.filter(document_id=document_id).exists():
            return Response(
                {"error": "Document is already associated with this application."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            document = Document.objects.get(document_id=document_id)
            application.documents.add(document_id)
            new_stage = ConsumerOnboardingStage.objects.filter(
                document_category=document.category.name
            ).first()
            if new_stage:
                application.current_stage = new_stage
                application.last_stage_updated_at = timezone.now()
                application.save()
                stage_updated = True
            else:
                stage_updated = False
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "document added"})

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAllowedToAddSubscription],
    )
    def add_subscription(self, request, pk=None):
        application = self.get_object()
        subscription_ids = request.data.get("subscription_ids", [])

        if not isinstance(subscription_ids, list):
            return Response(
                {"error": "Expected a list of subscription IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter the database for these IDs and see how many we actually find
        existing_count = Subscription.objects.filter(id__in=subscription_ids).count()

        if existing_count != len(set(subscription_ids)):
            return Response(
                {"error": "One or more subscription IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.subscriptions.add(*subscription_ids)

        return Response(
            {"status": f"Successfully added {len(subscription_ids)} subscriptions."},
            status=status.HTTP_200_OK,
        )


class CommunicationViewSet(viewsets.ModelViewSet):
    queryset = ConsumerCommunication.objects.all()
    serializer_class = ConsumerCommunicationSerializer
