from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, PermissionViewSet
from .views import LoginView, LogoutView, TokenRefreshView

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("roles", RoleViewSet)
router.register("permissions", PermissionViewSet)

urlpatterns = router.urls
urlpatterns += [
    path("auth/login/", LoginView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
]
