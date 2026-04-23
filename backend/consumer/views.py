from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from .models import (
    Consumer,
    Application,
    ConsumerCommunication,
    ConsumerOnboardingStage,
)
from .serializers import (
    ConsumerDetailSerializer,
    ConsumerCreateUpdateSerializer,
    ApplicationSerializer,
    ConsumerCommunicationSerializer,
    ConsumerOnboardingStageSerializer,
)
from .permissions import IsOwner, IsAdminRole


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


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class CommunicationViewSet(viewsets.ModelViewSet):
    queryset = ConsumerCommunication.objects.all()
    serializer_class = ConsumerCommunicationSerializer
