from rest_framework import permissions

class EsAdministrador(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es administrador o superadministrador
    """
    message = "Solo los administradores pueden acceder a este recurso."
    
    def has_permission(self, request, view):
        # El usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si es superusuario de Django
        if request.user.is_superuser:
            return True
        
        # Verificar si tiene perfil y roles de admin
        try:
            user_profile = request.user.perfil
            return user_profile.roles.filter(
                rol__codigo_rol__in=['ADMIN', 'SUPERADMIN']
            ).exists()
        except:
            return False

class EsSuperAdministrador(permissions.BasePermission):
    """
    Permiso personalizado solo para superadministradores
    """
    message = "Solo los superadministradores pueden acceder a este recurso."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si es superusuario de Django
        if request.user.is_superuser:
            return True
        
        # Verificar si tiene rol de superadmin
        try:
            user_profile = request.user.perfil
            return user_profile.roles.filter(
                rol__codigo_rol='SUPERADMIN'
            ).exists()
        except:
            return False

class EsAdminOSoloLectura(permissions.BasePermission):
    """
    Permite lectura a todos, pero solo administradores pueden modificar
    """
    def has_permission(self, request, view):
        # Métodos de solo lectura permitidos para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Métodos de escritura solo para admins
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            user_profile = request.user.perfil
            return user_profile.roles.filter(
                rol__codigo_rol__in=['ADMIN', 'SUPERADMIN']
            ).exists()
        except:
            return False
        
