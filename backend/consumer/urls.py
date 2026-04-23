from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("", ConsumerViewSet)
router.register("stages", StageViewSet)
router.register("applications", ApplicationViewSet)
router.register("communications", CommunicationViewSet)

urlpatterns = router.urls
