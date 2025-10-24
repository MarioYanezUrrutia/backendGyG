from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pedidos', views.PedidoViewSet, basename='pedido')

urlpatterns = [
    path('', include(router.urls)),
    path('user-profile/<int:user_id>/', views.user_profile_detail, name='user-profile-detail'),
    path('personas/<int:persona_id>/', views.persona_detail, name='persona-detail'),
    path('personas/<int:persona_id>/direcciones/', views.persona_direcciones, name='persona-direcciones'),
]