from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from apps.core.models import UserProfile, Persona, Direccion, Cliente
from apps.orders.models import Pedido, DetallePedido, SeguimientoDespacho, EstadoPedido
from .serializers import (
    CrearPedidoSerializer, PedidoSerializer, PedidoConSeguimientoSerializer,
    ActualizarEstadoPedidoSerializer, SeguimientoDespachoSerializer,
    UserProfileSerializer, PersonaSerializer, DireccionSerializer
)

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CrearPedidoSerializer
        elif self.action in ['retrieve', 'list']:
            return PedidoConSeguimientoSerializer
        return PedidoSerializer
    
    def get_queryset(self):
        """Filtrar pedidos según el rol del usuario"""
        user = self.request.user
        
        # Si es admin, ver todos los pedidos
        if user.is_staff or user.is_superuser:
            return Pedido.objects.all().select_related(
                'cliente', 'user_profile', 'user_profile__persona'
            ).prefetch_related('detalles', 'seguimientos')
        
        # Si es usuario normal, solo sus pedidos
        try:
            user_profile = UserProfile.objects.get(user=user)
            return Pedido.objects.filter(
                user_profile=user_profile
            ).select_related(
                'cliente', 'user_profile', 'user_profile__persona'
            ).prefetch_related('detalles', 'seguimientos')
        except UserProfile.DoesNotExist:
            return Pedido.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Crear un nuevo pedido"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()
        
        # Crear primer seguimiento
        SeguimientoDespacho.objects.create(
            pedido=pedido,
            estado=EstadoPedido.PENDIENTE,
            descripcion='Pedido creado y en espera de confirmación de pago'
        )
        
        # Enviar email de confirmación al cliente
        self._enviar_email_confirmacion(pedido)
        
        response_data = {
            'pedido_id': pedido.pedido_id,
            'numero_pedido': pedido.numero_pedido,
            'total': pedido.total,
            'estado': pedido.estado,
            'mensaje': 'Pedido creado exitosamente'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def actualizar_estado(self, request, pk=None):
        """Actualizar el estado de un pedido (solo admin)"""
        pedido = self.get_object()
        
        serializer = ActualizarEstadoPedidoSerializer(
            data=request.data,
            context={'pedido': pedido}
        )
        serializer.is_valid(raise_exception=True)
        
        nuevo_estado = serializer.validated_data['estado']
        descripcion = serializer.validated_data['descripcion']
        ubicacion = serializer.validated_data.get('ubicacion', '')
        
        # Actualizar estado del pedido
        pedido.estado = nuevo_estado
        
        # Si se entregó, guardar fecha real de entrega
        if nuevo_estado == EstadoPedido.ENTREGADO:
            from django.utils import timezone
            pedido.fecha_entrega_real = timezone.now()
        
        pedido.save()
        
        # Crear registro de seguimiento
        seguimiento = SeguimientoDespacho.objects.create(
            pedido=pedido,
            estado=nuevo_estado,
            descripcion=descripcion,
            ubicacion=ubicacion
        )
        
        # Enviar notificación por email
        self._enviar_email_actualizacion_estado(pedido, seguimiento)
        
        return Response({
            'mensaje': f'Estado actualizado a {nuevo_estado}',
            'pedido_id': pedido.pedido_id,
            'numero_pedido': pedido.numero_pedido,
            'estado': pedido.estado,
            'seguimiento': SeguimientoDespachoSerializer(seguimiento).data
        })
    
    @action(detail=True, methods=['get'])
    def seguimiento(self, request, pk=None):
        """Obtener el seguimiento completo de un pedido"""
        pedido = self.get_object()
        seguimientos = pedido.seguimientos.all().order_by('-fecha_creacion')
        serializer = SeguimientoDespachoSerializer(seguimientos, many=True)
        
        return Response({
            'pedido_id': pedido.pedido_id,
            'numero_pedido': pedido.numero_pedido,
            'estado_actual': pedido.estado,
            'seguimientos': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def mis_pedidos(self, request):
        """Obtener pedidos del usuario actual"""
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            pedidos = Pedido.objects.filter(
                user_profile=user_profile
            ).select_related(
                'cliente', 'user_profile', 'user_profile__persona'
            ).prefetch_related('detalles', 'seguimientos')
            
            serializer = self.get_serializer(pedidos, many=True)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def estadisticas(self, request):
        """Obtener estadísticas de pedidos (solo admin)"""
        from django.db.models import Count, Sum
        
        stats = {
            'total_pedidos': Pedido.objects.count(),
            'por_estado': dict(
                Pedido.objects.values('estado').annotate(
                    total=Count('pedido_id')
                ).values_list('estado', 'total')
            ),
            'pendientes': Pedido.objects.filter(estado=EstadoPedido.PENDIENTE).count(),
            'en_preparacion': Pedido.objects.filter(estado=EstadoPedido.PREPARANDO).count(),
            'en_camino': Pedido.objects.filter(estado=EstadoPedido.EN_CAMINO).count(),
            'entregados': Pedido.objects.filter(estado=EstadoPedido.ENTREGADO).count(),
            'cancelados': Pedido.objects.filter(estado=EstadoPedido.CANCELADO).count(),
            'ventas_totales': Pedido.objects.exclude(
                estado=EstadoPedido.CANCELADO
            ).aggregate(total=Sum('total'))['total'] or 0
        }
        
        return Response(stats)
    
    def _enviar_email_confirmacion(self, pedido):
        """Enviar email de confirmación de pedido"""
        try:
            asunto = f'Confirmación de Pedido #{pedido.numero_pedido}'
            mensaje = f"""
            Hola,
            
            Tu pedido ha sido creado exitosamente.
            
            Número de pedido: {pedido.numero_pedido}
            Total: ${pedido.total}
            Estado: {pedido.get_estado_display()}
            
            Puedes hacer seguimiento de tu pedido en nuestra plataforma.
            
            Gracias por tu compra.
            Gráfica G&G
            """
            
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [pedido.email_contacto],
                fail_silently=True
            )
        except Exception as e:
            print(f"Error enviando email de confirmación: {e}")
    
    def _enviar_email_actualizacion_estado(self, pedido, seguimiento):
        """Enviar email cuando cambia el estado del pedido"""
        try:
            asunto = f'Actualización de Pedido #{pedido.numero_pedido}'
            mensaje = f"""
            Hola,
            
            Tu pedido ha sido actualizado.
            
            Número de pedido: {pedido.numero_pedido}
            Nuevo estado: {pedido.get_estado_display()}
            
            {seguimiento.descripcion}
            
            {f"Ubicación: {seguimiento.ubicacion}" if seguimiento.ubicacion else ""}
            
            Puedes hacer seguimiento de tu pedido en nuestra plataforma.
            
            Gracias por tu compra.
            Gráfica G&G
            """
            
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [pedido.email_contacto],
                fail_silently=True
            )
        except Exception as e:
            print(f"Error enviando email de actualización: {e}")
            
    @action(detail=True, methods=['DELETE'])
    def eliminar_pedido(self, request, pk=None):
        """Eliminar un pedido (solo admin)"""
        try:
            pedido = self.get_object()
            numero_pedido = pedido.numero_pedido
            
            # Eliminar archivos físicos si existen
            import os
            from django.conf import settings
            pedido_folder = os.path.join(settings.MEDIA_ROOT, 'pedidos', str(pedido.pedido_id))
            if os.path.exists(pedido_folder):
                import shutil
                shutil.rmtree(pedido_folder)
            
            pedido.delete()
            return Response({
                'message': f'Pedido {numero_pedido} eliminado correctamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_detail(request, user_id):
    """Obtener detalles del UserProfile"""
    try:
        user_profile = UserProfile.objects.select_related('persona').get(user_id=user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'UserProfile no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def persona_detail(request, persona_id):
    """Obtener detalles de la Persona"""
    persona = get_object_or_404(Persona, persona_id=persona_id)
    serializer = PersonaSerializer(persona)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def persona_direcciones(request, persona_id):
    """Obtener direcciones de una Persona"""
    persona = get_object_or_404(Persona, persona_id=persona_id)
    direcciones = Direccion.objects.filter(
        persona=persona, 
        activo=True
    ).select_related('calle', 'comuna', 'ciudad', 'region')
    serializer = DireccionSerializer(direcciones, many=True)
    return Response(serializer.data)