from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Validación de email
    # path('validar-email/', views.validar_email, name='validar_email'),
    
    # Información del usuario
    path('perfil/', views.perfil_actual, name='perfil_actual'),
    path('verificar-admin/', views.verificar_admin, name='verificar_admin'),
]