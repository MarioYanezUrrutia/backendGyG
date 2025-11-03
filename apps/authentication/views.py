from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from apps.core.models import UserProfile
from .serializers import RegistroSerializer, UserProfileSerializer, LoginResponseSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def registro(request):
    """
    Registra un nuevo usuario y envía email de validación
    """
    
    serializer = RegistroSerializer(data=request.data)
    
    if serializer.is_valid():
        user_profile = serializer.save()
    
        # Email de validación deshabilitado - Usuario activo automáticamente
        # enviar_email_validacion(user_profile)
        
        return Response({
            'message': 'Usuario registrado exitosamente. Ya puedes iniciar sesión.',
            'email': user_profile.user.email
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Autentica un usuario y retorna tokens JWT
    """
    print("=" * 50)
    print("INTENTO DE LOGIN:")
    print(f"Datos recibidos: {request.data}")
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'None'}")




    
    if not username or not password:
        return Response({
            'error': 'Por favor proporciona usuario y contraseña'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Autenticar usuario
    user = authenticate(username=username, password=password)
    
    print(f"Usuario autenticado: {user}")
    print(f"Usuario es None: {user is None}")

    if user:
        print(f"Usuario encontrado: {user.username}")
        print(f"Usuario activo: {user.is_active}")
    else:
        print("❌ Usuario NO encontrado - Credenciales inválidas")
        
        # Verificar si el usuario existe
        from django.contrib.auth.models import User
        try:
            existing_user = User.objects.get(username=username)
            print(f"⚠️ El usuario '{username}' SÍ existe en la BD")
            print(f"is_active: {existing_user.is_active}")
            print(f"has_usable_password: {existing_user.has_usable_password()}")
        except User.DoesNotExist:
            print(f"⚠️ El usuario '{username}' NO existe en la BD")

    print("=" * 50)

    if user is None:
        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'Tu cuenta no ha sido activada. Por favor, verifica tu email.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Obtener UserProfile
    try:
        user_profile = user.perfil
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Perfil de usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Generar tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserProfileSerializer(user_profile).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def validar_email(request):
    """
    Valida el email del usuario mediante el token
    """
    token = request.GET.get('token')
    
    if not token:
        return Response({
            'error': 'Token no proporcionado'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_profile = UserProfile.objects.get(token_validacion=token)
        
        if user_profile.mail_verified:
            return Response({
                'message': 'Tu email ya ha sido verificado anteriormente'
            }, status=status.HTTP_200_OK)
        
        # Activar usuario
        user_profile.user.is_active = True
        user_profile.user.save()
        
        # Marcar email como verificado
        user_profile.mail_verified = True
        user_profile.token_validacion = None  # Invalidar token
        user_profile.save()
        
        # Generar tokens para login automático
        refresh = RefreshToken.for_user(user_profile.user)
        
        return Response({
            'message': 'Email verificado exitosamente',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user_profile).data
        }, status=status.HTTP_200_OK)
        
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Token inválido o expirado'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_actual(request):
    """
    Retorna el perfil del usuario autenticado
    """
    try:
        user_profile = request.user.perfil
        return Response(UserProfileSerializer(user_profile).data)
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Perfil no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_admin(request):
    """
    Verifica si el usuario autenticado es administrador
    """
    try:
        user_profile = request.user.perfil
        es_admin = user_profile.roles.filter(
            rol__codigo_rol__in=['ADMIN', 'SUPERADMIN']
        ).exists()
        
        return Response({
            'es_admin': es_admin,
            'roles': list(user_profile.roles.values_list('rol__codigo_rol', flat=True))
        })
    except UserProfile.DoesNotExist:
        return Response({
            'es_admin': False,
            'error': 'Perfil no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Cierra sesión del usuario (blacklist del refresh token)
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Sesión cerrada exitosamente'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==================== FUNCIÓN AUXILIAR ====================
def enviar_email_validacion(user_profile):
    """
    Envía el email de validación al usuario
    """
    validation_url = f"{settings.BACKEND_URL}/api/auth/validar-email/?token={user_profile.token_validacion}"
    
    # Renderizar template HTML
    html_message = render_to_string('emails/validacion_email.html', {
        'nombre': user_profile.persona.primer_nombre,
        'validation_url': validation_url,
        'frontend_url': settings.FRONTEND_URL
    })
    
    # Enviar email
    send_mail(
        subject='Valida tu cuenta en Gráfica GyG',
        message=f'Hola {user_profile.persona.primer_nombre}, por favor valida tu cuenta haciendo clic en el siguiente enlace: {validation_url}',
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@graficagyg.com',
        recipient_list=[user_profile.user.email],
        html_message=html_message,
        fail_silently=False,
    )