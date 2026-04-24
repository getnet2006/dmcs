from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("stages", StageViewSet, basename="stage")
router.register("applications", ApplicationViewSet, basename="application")
router.register("communications", CommunicationViewSet, basename="communication")
router.register("", ConsumerViewSet, basename="consumer")

urlpatterns = [
    path("", include(router.urls)),
]
