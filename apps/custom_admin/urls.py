from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoAdminViewSet, ProductFileViewSet

router = DefaultRouter()
router.register(r'productos-admin', ProductoAdminViewSet)
router.register(r'archivos-productos', ProductFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


