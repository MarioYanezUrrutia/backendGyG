from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PedidoViewSet,
    user_profile_detail,
    persona_detail,
    persona_direcciones
)

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet)

# router.register(r'detallepedidos', DetallePedidoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user-profile/<int:user_id>/', user_profile_detail, name='user-profile-detail'),
    path('personas/<int:persona_id>/', persona_detail, name='persona-detail'),
    path('personas/<int:persona_id>/direcciones/', persona_direcciones, name='persona-direcciones'),
]