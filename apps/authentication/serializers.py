from rest_framework import serializers
from django.contrib.auth.models import User
from apps.core.models import UserProfile, Persona, UserRol, Rol
from apps.core.models import Cliente
from django.db import transaction
import secrets

class RegistroSerializer(serializers.Serializer):
    # Datos de autenticación
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    # Datos de persona
    primer_nombre = serializers.CharField(max_length=30)
    segundo_nombre = serializers.CharField(max_length=30, required=False, allow_blank=True)
    apellido_paterno = serializers.CharField(max_length=30)
    apellido_materno = serializers.CharField(max_length=30, required=False, allow_blank=True)
    documento_identidad = serializers.CharField(max_length=15, required=False, allow_blank=True)
    dv = serializers.CharField(max_length=1, required=False, allow_blank=True)
    telefono_persona = serializers.CharField(max_length=15)
    whatsapp_persona = serializers.CharField(max_length=15, required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    
    def validate(self, data):
        # Validar que las contraseñas coincidan
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        
        # Validar que el username no exista
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Este nombre de usuario ya está en uso"})
        
        # Validar que el email no exista
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Este email ya está registrado"})
        
        # Validar que el documento de identidad no exista
        if Persona.objects.filter(documento_identidad=data['documento_identidad']).exists():
            raise serializers.ValidationError({"documento_identidad": "Este documento ya está registrado"})
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Remover password_confirm
        validated_data.pop('password_confirm')
        
        # Crear User de Django
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # user.is_active = False  # Desactivado hasta que valide el email
        user.is_active = True #No es necesaria la validación por mail
        user.save()
        
        # Crear Persona
        persona = Persona.objects.create(
            primer_nombre=validated_data['primer_nombre'],
            segundo_nombre=validated_data.get('segundo_nombre', ''),
            apellido_paterno=validated_data['apellido_paterno'],
            apellido_materno=validated_data.get('apellido_materno', ''),
            documento_identidad=validated_data.get('documento_identidad') or '',
            dv=validated_data.get('dv') or '',
            mail=validated_data['email'],
            telefono_persona=validated_data.get('telefono_persona', ''),
            whatsapp_persona=validated_data.get('whatsapp_persona', ''),
            fecha_nacimiento=validated_data.get('fecha_nacimiento')
        )
        
        # Generar token de validación
        token_validacion = secrets.token_urlsafe(32)
        
        # Crear UserProfile
        user_profile = UserProfile.objects.create(
            user=user,
            persona=persona,
            mail_verified=False,
            token_validacion=token_validacion
        )
        
        # Asignar rol de CLIENTE por defecto
        try:
            rol_cliente = Rol.objects.get(codigo_rol='CLIENTE')
            UserRol.objects.create(user_profile=user_profile, rol=rol_cliente)
        except Rol.DoesNotExist:
            pass
        
        # Crear registro en tabla Cliente
        Cliente.objects.create(
            user_profile=user_profile,
            nombre_cliente=f"{validated_data['primer_nombre']} {validated_data['apellido_paterno']}",
            telefono=validated_data.get('telefono_persona', '')
        )
        
        return user_profile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    nombre_completo = serializers.CharField(source='persona.nombre_completo', read_only=True)
    roles = serializers.SerializerMethodField()
    es_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['user_profile_id', 'username', 'email', 'nombre_completo', 
                  'mail_verified', 'roles', 'es_admin']
    
    def get_roles(self, obj):
        return list(obj.roles.values_list('rol__nombre_rol', flat=True))
    
    def get_es_admin(self, obj):
        return obj.roles.filter(
            rol__codigo_rol__in=['ADMIN', 'SUPERADMIN']
        ).exists()

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()