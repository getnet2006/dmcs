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
    ConsumerCommunicationCreateUpdateSerializer,
    ConsumerOnboardingStageSerializer,
    SubscriptionReadSerializer,
    SubscriptionCreateUpdateSerializer,
)
from documents.models import Document
from account.models import User
from .permissions import (
    IsOwner,
    IsAdminRole,
    IsAllowedToAddDocument,
    IsAllowedToAddSubscription,
)
from account.permissions import MustChangePasswordBeforeAccess


class ConsumerViewSet(viewsets.ModelViewSet):
    queryset = Consumer.objects.all()
    permission_classes = [
        IsAuthenticated,
        DjangoModelPermissions,
        MustChangePasswordBeforeAccess,
    ]
    http_method_names = ["get", "post", "put", "patch"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ConsumerDetailSerializer
        return ConsumerCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            self.permission_classes = [
                IsOwner | IsAdminRole,
                DjangoModelPermissions,
                MustChangePasswordBeforeAccess,
            ]
        else:
            self.permission_classes = [
                IsAuthenticated,
                DjangoModelPermissions,
                MustChangePasswordBeforeAccess,
            ]
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
    permission_classes = [
        IsAuthenticated,
        DjangoModelPermissions,
        MustChangePasswordBeforeAccess,
    ]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return ApplicationDetailSerializer
        return ApplicationCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAllowedToAddDocument, MustChangePasswordBeforeAccess],
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
        try:
            document = Document.objects.get(document_id=document_id)
        except Document.DoesNotExist:
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
            application.documents.add(document)
            stage_updated = application.transition_by_document(document)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "document added", "stage_updated": stage_updated})

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAllowedToAddSubscription, MustChangePasswordBeforeAccess],
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

        # check if any of the subscriptions are already associated with the application
        existing_subscriptions = application.subscriptions.filter(
            id__in=subscription_ids
        )
        if existing_subscriptions.exists():
            return Response(
                {
                    "error": "One or more subscriptions are already associated with this application."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.subscriptions.add(*subscription_ids)

        return Response(
            {"status": f"Successfully added {len(subscription_ids)} subscriptions."},
            status=status.HTTP_200_OK,
        )


class CommunicationViewSet(viewsets.ModelViewSet):
    queryset = ConsumerCommunication.objects.all()
    http_method_names = ["get", "post"]
    permission_classes = [DjangoModelPermissions, MustChangePasswordBeforeAccess]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return ConsumerCommunicationSerializer
        return ConsumerCommunicationCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return Response(
            {
                "error": "Listing all communications is not allowed. Use by-application endpoint instead."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # action to retrieve communications for a specific application
    @action(
        detail=False,
        methods=["get"],
        url_path="by-application/(?P<application_id>[^/.]+)",
    )
    def by_application(self, request, application_id=None):
        communications = self.queryset.filter(application_id=application_id)
        serializer = self.get_serializer(communications, many=True)
        return Response(serializer.data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    http_method_names = ["get", "post", "put", "patch"]
    permission_classes = [
        IsAuthenticated,
        DjangoModelPermissions,
        MustChangePasswordBeforeAccess,
    ]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SubscriptionReadSerializer
        return SubscriptionCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsOwner | IsAdminRole]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
