from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScanViewSet, start_nfc, stop_nfc_view

router = DefaultRouter()
router.register(r'scans', ScanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('start/', start_nfc, name='start_nfc'),
    path('stop/', stop_nfc_view, name='stop_nfc'),
]
