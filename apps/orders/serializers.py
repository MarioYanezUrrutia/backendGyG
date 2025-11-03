import os
import base64
from django.conf import settings
from rest_framework import serializers
from apps.core.models import Producto, UserProfile, Persona, Direccion, Terminacion
from .models import Pedido, DetallePedido, SeguimientoDespacho, EstadoPedido

class SeguimientoDespachoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeguimientoDespacho
        fields = ['seguimiento_id', 'estado', 'descripcion', 'ubicacion', 'fecha_creacion']
        read_only_fields = ['seguimiento_id', 'fecha_creacion']

class ActualizarEstadoPedidoSerializer(serializers.Serializer):
    """Serializer para actualizar el estado de un pedido"""
    estado = serializers.ChoiceField(choices=EstadoPedido.choices)
    descripcion = serializers.CharField(required=True)
    ubicacion = serializers.CharField(required=False, allow_blank=True)
    
    def validate_estado(self, value):
        """Validar transiciones de estado permitidas"""
        pedido = self.context.get('pedido')
        if not pedido:
            raise serializers.ValidationError("Pedido no encontrado en el contexto")
        
        # Validar transiciones lógicas
        transiciones_validas = {
            EstadoPedido.PENDIENTE: [EstadoPedido.CONFIRMADO, EstadoPedido.CANCELADO],
            EstadoPedido.CONFIRMADO: [EstadoPedido.PREPARANDO, EstadoPedido.CANCELADO],
            EstadoPedido.PREPARANDO: [EstadoPedido.EN_CAMINO, EstadoPedido.CANCELADO],
            EstadoPedido.EN_CAMINO: [EstadoPedido.ENTREGADO],
            EstadoPedido.ENTREGADO: [],  # Estado final
            EstadoPedido.CANCELADO: []   # Estado final
        }
        
        if value not in transiciones_validas.get(pedido.estado, []):
            raise serializers.ValidationError(
                f"No se puede cambiar de {pedido.estado} a {value}"
            )
        
        return value

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'

class DetallePedidoSerializer(serializers.ModelSerializer):
    # Información adicional de acabado
    acabado_info = serializers.SerializerMethodField()
    terminacion_info = serializers.SerializerMethodField()
    tiempo_produccion_info = serializers.SerializerMethodField()
    
    class Meta:
        model = DetallePedido
        fields = [
            'detalle_pedido_id',
            'producto_id', 
            'nombre_producto', 
            'cantidad', 
            'precio_unitario',
            'subtotal',
            # Acabado
            'acabado',
            'nombre_acabado',
            'costo_acabado',
            'acabado_info',
            # Terminación
            'terminacion',
            'nombre_terminacion',
            'costo_terminacion',
            'terminacion_info',
            # Tiempo de producción
            'tiempo_produccion',
            'nombre_tiempo_produccion',
            'dias_produccion',
            'costo_tiempo_produccion',
            'tiempo_produccion_info',
            # Personalización
            'personalizacion_texto',
            'archivo_cara1',
            'archivo_cara2',
            'archivos',
            'notas_producto'
        ]
        read_only_fields = ['subtotal']
    
    def get_terminacion_info(self, obj):
        """Devuelve información completa de la terminación"""
        if obj.terminacion:
            return {
                'terminacion_id': obj.terminacion.terminacion_id,
                'nombre': obj.terminacion.nombre_terminacion,
                'descripcion': obj.terminacion.descripcion,
                'costo': obj.costo_terminacion
            }
        elif obj.nombre_terminacion:
            return {
                'nombre': obj.nombre_terminacion,
                'costo': obj.costo_terminacion
            }
        return None
    
    def get_acabado_info(self, obj):
        """Devuelve información completa del acabado"""
        if obj.acabado:
            return {
                'acabado_id': obj.acabado.acabado_id,
                'nombre': obj.acabado.nombre_acabado,
                'descripcion': obj.acabado.descripcion,
                'costo': obj.costo_acabado
            }
        elif obj.nombre_acabado:
            return {
                'nombre': obj.nombre_acabado,
                'costo': obj.costo_acabado
            }
        return None
    
    def get_tiempo_produccion_info(self, obj):
        """Devuelve información completa del tiempo de producción"""
        if obj.tiempo_produccion:
            return {
                'tiempo_produccion_id': obj.tiempo_produccion.tiempo_produccion_id,
                'nombre': obj.tiempo_produccion.nombre_tiempo,
                'descripcion': obj.tiempo_produccion.descripcion,
                'dias': obj.dias_produccion,
                'costo': obj.costo_tiempo_produccion
            }
        elif obj.nombre_tiempo_produccion:
            return {
                'nombre': obj.nombre_tiempo_produccion,
                'dias': obj.dias_produccion,
                'costo': obj.costo_tiempo_produccion
            }
        return None
    
    def get_archivos(self, obj):
        """Devuelve URLs completas de los archivos"""
        archivos = []
        if obj.archivo_cara1:
            archivos.append({
                'tipo': 'cara1',
                'nombre': os.path.basename(obj.archivo_cara1),
                'url': f"{self.context.get('request').build_absolute_uri('/media/')}{obj.archivo_cara1}" if self.context.get('request') else obj.archivo_cara1
            })
        if obj.archivo_cara2:
            archivos.append({
                'tipo': 'cara2',
                'nombre': os.path.basename(obj.archivo_cara2),
                'url': f"{self.context.get('request').build_absolute_uri('/media/')}{obj.archivo_cara2}" if self.context.get('request') else obj.archivo_cara2
            })
        return archivos

    archivos = serializers.SerializerMethodField()

class PedidoConSeguimientoSerializer(serializers.ModelSerializer):
    """Serializer completo del pedido con detalles y seguimiento"""
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    seguimientos = SeguimientoDespachoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    user_profile_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = [
            'pedido_id', 'numero_pedido', 'estado', 'fecha_pedido',
            'cliente', 'cliente_nombre', 'user_profile', 'user_profile_nombre',
            'direccion_entrega', 'comuna', 'ciudad', 'region', 'codigo_postal',
            'telefono_contacto', 'email_contacto',
            'subtotal', 'costo_envio', 'descuento', 'total',
            'notas_cliente', 'notas_internas',
            'fecha_estimada_entrega', 'fecha_entrega_real',
            'detalles', 'seguimientos',
            'fecha_creacion', 'fecha_modificacion'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_cliente if obj.cliente else None
    
    def get_user_profile_nombre(self, obj):
        if obj.user_profile and hasattr(obj.user_profile, 'persona') and obj.user_profile.persona:
            persona = obj.user_profile.persona
            return f"{persona.primer_nombre} {persona.apellido_paterno}"
        return None
    
class ItemPedidoSerializer(serializers.Serializer):
    """Serializer simple para items en la creación de pedidos"""
    producto_id = serializers.IntegerField()
    nombre_producto = serializers.CharField()
    cantidad = serializers.IntegerField()
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # ⭐ NUEVOS CAMPOS - ACABADOS (puede ser lista)
    acabado_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list
    )
    # # ⭐ NUEVOS CAMPOS
    # acabado_id = serializers.IntegerField(required=False, allow_null=True)
    # nombre_acabado = serializers.CharField(required=False, allow_blank=True)
    # costo_acabado = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, required=False)

    terminacion_id = serializers.IntegerField(required=False, allow_null=True)
    nombre_terminacion = serializers.CharField(required=False, allow_blank=True)
    costo_terminacion = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, required=False)
    
    tiempo_produccion_id = serializers.IntegerField(required=False, allow_null=True)
    nombre_tiempo_produccion = serializers.CharField(required=False, allow_blank=True)
    dias_produccion = serializers.IntegerField(required=False, allow_null=True)
    costo_tiempo_produccion = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, required=False)
    
    personalizacion_texto = serializers.CharField(required=False, allow_blank=True)
    notas_producto = serializers.CharField(required=False, allow_blank=True)
    ancho_cm = serializers.IntegerField(required=False, allow_null=True)
    alto_cm = serializers.IntegerField(required=False, allow_null=True)
    # Archivos en Base64
    archivo_cara1_base64 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    archivo_cara1_nombre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    archivo_cara2_base64 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    archivo_cara2_nombre = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class CrearPedidoSerializer(serializers.Serializer):
    # Datos del usuario
    user_profile_id = serializers.IntegerField()
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Items del pedido
    items = ItemPedidoSerializer(many=True)
    
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
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                
                producto = Producto.objects.get(producto_id=producto_id)
                
                # Validar stock solo si el producto tiene gestión de stock
                if hasattr(producto, 'tiene_stock'):
                    if not producto.tiene_stock(cantidad):
                        raise serializers.ValidationError(
                            f"Stock insuficiente para {producto.nombre_producto}"
                        )
                        
            except Producto.DoesNotExist:
                raise serializers.ValidationError(
                    f"Producto con ID {producto_id} no existe"
                )
            except KeyError as e:
                raise serializers.ValidationError(
                    f"Falta el campo {str(e)} en el item"
                )
        
        return items
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Crear el pedido
        pedido = Pedido.objects.create(**validated_data)
        
        # Crear los detalles del pedido
        for item_data in items_data:
            producto = Producto.objects.get(producto_id=item_data['producto_id'])
            
            # Obtener referencias
            acabados_list = []
            tiempo_produccion = None
            terminacion = None
            
            # Procesar acabados (puede ser lista)
            if item_data.get('acabado_ids'):
                try:
                    from apps.core.models import Acabado
                    acabados_list = list(Acabado.objects.filter(acabado_id__in=item_data['acabado_ids']))
                except Exception as e:
                    print(f"Error obteniendo acabados: {e}")
                            
            if item_data.get('terminacion_id'):
                try:
                    terminacion = Terminacion.objects.get(terminacion_id=item_data['terminacion_id'])
                except Terminacion.DoesNotExist:
                    pass

            if item_data.get('tiempo_produccion_id'):
                try:
                    from apps.core.models import TiempoProduccion
                    tiempo_produccion = TiempoProduccion.objects.get(
                        tiempo_produccion_id=item_data['tiempo_produccion_id']
                    )
                except TiempoProduccion.DoesNotExist:
                    pass
            
            # ✅ CALCULAR MULTIPLICADOR DE ACABADOS (producto, no suma)
            multiplicador_acabados = 1.0
            if acabados_list:
                for acabado in acabados_list:
                    multiplicador_acabados *= float(acabado.costo_adicional)
            
            # Crear detalle del pedido
            detalle = DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre_producto=item_data.get('nombre_producto', producto.nombre_producto),
                cantidad=item_data['cantidad'],
                precio_unitario=item_data['precio_unitario'],
                # Acabado (guardar multiplicador acumulado)
                acabado=acabados_list[0] if acabados_list else None,
                nombre_acabado=', '.join([a.nombre_acabado for a in acabados_list]) if acabados_list else None,
                costo_acabado=multiplicador_acabados,  # ✅ Multiplicador acumulado
                # Terminación (guardar multiplicador)
                terminacion=terminacion,
                nombre_terminacion=terminacion.nombre_terminacion if terminacion else None,
                costo_terminacion=float(terminacion.precio) if terminacion else 1.0,  # ✅ Multiplicador
                # Tiempo de producción (este SÍ es suma)
                tiempo_produccion=tiempo_produccion,
                nombre_tiempo_produccion=tiempo_produccion.nombre_tiempo if tiempo_produccion else None,
                dias_produccion=tiempo_produccion.dias_estimados if tiempo_produccion else None,
                costo_tiempo_produccion=float(tiempo_produccion.precio) if tiempo_produccion else 0,  # ✅ Costo a sumar
                # Personalización
                personalizacion_texto=f"{item_data.get('ancho_cm')}cm x {item_data.get('alto_cm')}cm" if item_data.get('ancho_cm') else None,
                notas_producto=item_data.get('notas_producto')
            )

            # 📁 GUARDAR ARCHIVOS EN SISTEMA DE ARCHIVOS (NO EN DB)
            pedido_folder = os.path.join(settings.MEDIA_ROOT, 'pedidos', str(pedido.pedido_id))
            os.makedirs(pedido_folder, exist_ok=True)
            
            # Procesar cara 1
            if item_data.get('archivo_cara1_base64'):
                try:
                    # Extraer datos del base64
                    base64_data = item_data['archivo_cara1_base64']
                    if ',' in base64_data:
                        formato, imgstr = base64_data.split(',', 1)
                    else:
                        imgstr = base64_data
                    
                    # Decodificar y guardar
                    img_data = base64.b64decode(imgstr)
                    # Formato: telefono_pedidoID_cara1.png
                    telefono_limpio = ''.join(filter(str.isdigit, validated_data.get('telefono_contacto', 'cliente')))[:8]
                    nombre_archivo = f"{telefono_limpio}_{pedido.pedido_id}_cara1.png"
                    ruta_completa = os.path.join(pedido_folder, nombre_archivo)
                    
                    with open(ruta_completa, 'wb') as f:
                        f.write(img_data)
                    
                    # Guardar solo la ruta relativa en DB
                    detalle.archivo_cara1 = f'pedidos/{pedido.pedido_id}/{nombre_archivo}'
                    detalle.save(update_fields=['archivo_cara1'])
                    print(f"✅ Archivo cara1 guardado en: {detalle.archivo_cara1}")
                    
                except Exception as e:
                    print(f"❌ Error guardando cara1: {e}")
            
            # Procesar cara 2
            if item_data.get('archivo_cara2_base64'):
                try:
                    base64_data = item_data['archivo_cara2_base64']
                    if ',' in base64_data:
                        formato, imgstr = base64_data.split(',', 1)
                    else:
                        imgstr = base64_data
                    
                    img_data = base64.b64decode(imgstr)
                    telefono_limpio = ''.join(filter(str.isdigit, validated_data.get('telefono_contacto', 'cliente')))[:8]
                    nombre_archivo = f"{telefono_limpio}_{pedido.pedido_id}_cara2.png"
                    ruta_completa = os.path.join(pedido_folder, nombre_archivo)
                    
                    with open(ruta_completa, 'wb') as f:
                        f.write(img_data)
                    
                    detalle.archivo_cara2 = f'pedidos/{pedido.pedido_id}/{nombre_archivo}'
                    detalle.save(update_fields=['archivo_cara2'])
                    print(f"✅ Archivo cara2 guardado en: {detalle.archivo_cara2}")
                    
                except Exception as e:
                    print(f"❌ Error guardando cara2: {e}")
            
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

