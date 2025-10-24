from rest_framework import serializers
from apps.core.models import Pedido, DetallePedido, Producto, UserProfile, Persona, Direccion

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ['producto_id', 'nombre_producto', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['subtotal']

class CrearPedidoSerializer(serializers.Serializer):
    # Datos del usuario
    user_profile_id = serializers.IntegerField()
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Items del pedido
    items = DetallePedidoSerializer(many=True)
    
    # Datos de entrega
    direccion_entrega = serializers.CharField()
    comuna = serializers.CharField()
    ciudad = serializers.CharField()
    region = serializers.CharField()
    codigo_postal = serializers.CharField(required=False, allow_blank=True)
    
    # Contacto
    telefono_contacto = serializers.CharField()
    email_contacto = serializers.EmailField()
    
    # Montos
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    costo_envio = serializers.DecimalField(max_digits=10, decimal_places=2)
    descuento = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Método de pago
    metodo_pago = serializers.CharField()
    
    # Notas
    notas_cliente = serializers.CharField(required=False, allow_blank=True)
    
    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("El pedido debe tener al menos un producto")
        
        # Validar stock disponible
        for item in items:
            try:
                producto = Producto.objects.get(producto_id=item['producto_id'])
                if not producto.tiene_stock(item['cantidad']):
                    raise serializers.ValidationError(
                        f"Stock insuficiente para {producto.nombre_producto}"
                    )
            except Producto.DoesNotExist:
                raise serializers.ValidationError(
                    f"Producto con ID {item['producto_id']} no existe"
                )
        
        return items
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Crear el pedido
        pedido = Pedido.objects.create(**validated_data)
        
        # Crear los detalles del pedido
        for item_data in items_data:
            producto = Producto.objects.get(producto_id=item_data['producto_id'])
            
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre_producto=item_data.get('nombre_producto', producto.nombre_producto),
                cantidad=item_data['cantidad'],
                precio_unitario=item_data['precio_unitario']
            )
            
            # Actualizar stock del producto
            producto.stock -= item_data['cantidad']
            producto.ventas_totales += item_data['cantidad']
            producto.save()
        
        return pedido

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    persona_id = serializers.IntegerField(source='persona.persona_id', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user_profile_id', 'persona_id', 'mail_verified']

class PersonaSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Persona
        fields = [
            'persona_id', 'primer_nombre', 'segundo_nombre', 
            'apellido_paterno', 'apellido_materno', 'documento_identidad', 
            'dv', 'mail', 'telefono_persona', 'nombre_completo'
        ]

class DireccionSerializer(serializers.ModelSerializer):
    calle_nombre = serializers.CharField(source='calle.nombre_calle', read_only=True)
    comuna_nombre = serializers.CharField(source='comuna.nombre_comuna', read_only=True)
    ciudad_nombre = serializers.CharField(source='ciudad.nombre_ciudad', read_only=True)
    region_nombre = serializers.CharField(source='region.nombre_region', read_only=True)
    
    class Meta:
        model = Direccion
        fields = [
            'direccion_id', 'calle', 'calle_nombre', 'direccion_numero',
            'direccion_depto', 'direccion_block', 'direccion_referencia',
            'comuna', 'comuna_nombre', 'ciudad', 'ciudad_nombre',
            'region', 'region_nombre', 'tipo_direccion'
        ]