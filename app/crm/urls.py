from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RequestViewSet, RequestTypeViewSet

router = DefaultRouter()
router.register(r'requests', RequestViewSet, basename='request')
router.register(r'request-types', RequestTypeViewSet, basename='request-type')

urlpatterns = [
    path('', include(router.urls)),
]
