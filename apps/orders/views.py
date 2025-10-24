from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.models import Pedido, UserProfile, Persona, Direccion
from .serializers import (
    CrearPedidoSerializer, PedidoSerializer, 
    UserProfileSerializer, PersonaSerializer, DireccionSerializer
)

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CrearPedidoSerializer
        return PedidoSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()
        
        # Aquí puedes agregar lógica para procesar el pago
        metodo_pago = request.data.get('metodo_pago')
        
        response_data = {
            'pedido_id': pedido.pedido_id,
            'numero_pedido': pedido.numero_pedido,
            'total': pedido.total,
            'estado': pedido.estado
        }
        
        # Si es Webpay, generar URL de pago (implementar según tu integración)
        if metodo_pago == 'webpay':
            # TODO: Integrar con Webpay
            response_data['payment_url'] = None  # URL de Webpay
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mis_pedidos(self, request):
        """Obtener pedidos del usuario actual"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'Se requiere user_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            pedidos = Pedido.objects.filter(user_profile=user_profile)
            serializer = self.get_serializer(pedidos, many=True)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

@api_view(['GET'])
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
def persona_detail(request, persona_id):
    """Obtener detalles de la Persona"""
    persona = get_object_or_404(Persona, persona_id=persona_id)
    serializer = PersonaSerializer(persona)
    return Response(serializer.data)

@api_view(['GET'])
def persona_direcciones(request, persona_id):
    """Obtener direcciones de una Persona"""
    persona = get_object_or_404(Persona, persona_id=persona_id)
    direcciones = Direccion.objects.filter(
        persona=persona, 
        activo=True
    ).select_related('calle', 'comuna', 'ciudad', 'region')
    serializer = DireccionSerializer(direcciones, many=True)
    return Response(serializer.data)