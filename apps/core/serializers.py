from rest_framework import serializers
from .models import (
    Categoria, Subcategoria, Producto, Carrusel, Cliente, Pedido, DetallePedido, 
    PreguntaFrecuente, Carrito, ItemCarrito, ImagenProducto, Marca,
    UnidadMedida, Proveedor, Terminacion, Acabado, TiempoProduccion, TamanoPredefinido
)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class TamanoPredefinidoSerializer(serializers.ModelSerializer):
    """Serializer para tamaños preestablecidos"""
    class Meta:
        model = TamanoPredefinido
        fields = ['tamano_id', 'nombre_tamano', 'ancho_cm', 'alto_cm', 'es_predeterminado', 'orden']
        read_only_fields = ['tamano_id']

class TerminacionSerializer(serializers.ModelSerializer):
    """Serializer para terminaciones (materiales)"""
    class Meta:
        model = Terminacion
        fields = ['terminacion_id', 'nombre_terminacion', 'descripcion', 'precio', 'es_predeterminado', 'orden']
        read_only_fields = ['terminacion_id']

class AcabadoSerializer(serializers.ModelSerializer):
    """Serializer para acabados"""
    class Meta:
        model = Acabado
        fields = ['acabado_id', 'nombre_acabado', 'descripcion']
        read_only_fields = ['acabado_id']

class TiempoProduccionSerializer(serializers.ModelSerializer):
    """Serializer para tiempos de producción"""
    class Meta:
        model = TiempoProduccion
        fields = ['tiempo_produccion_id', 'nombre_tiempo', 'descripcion', 'dias_estimados', 'precio', 'es_predeterminado', 'orden']
        read_only_fields = ['tiempo_produccion_id']

class SubcategoriaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre_categoria', read_only=True)
    class Meta:
        model = Subcategoria
        fields = '__all__'

# ============= SERIALIZERS DE PRODUCTOS =============
class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de productos"""
    imagen_principal = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()
    caracteristicas_list = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='subcategoria.categoria.nombre_categoria', read_only=True)
    subcategoria_nombre = serializers.CharField(source='subcategoria.nombre_subcategoria', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre_marca', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'producto_id', 'nombre_producto', 'descripcion_corta', 'detalle_producto',
            'precio_venta', 'precio_oferta', 'es_oferta', 'precio_final',
            'imagen_principal', 'es_destacado', 'es_novedad', 'es_solucion_inteligente',
            'stock', 'categoria_nombre', 'subcategoria_nombre', 'marca_nombre',
            'caracteristicas_list'
        ]
    
    def get_imagen_principal(self, obj):
        imagen = obj.imagenes.filter(es_principal=True).first() or obj.imagenes.first()
        if imagen and imagen.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(imagen.imagen.url)
            return imagen.imagen.url
        return None
    
    def get_precio_final(self, obj):
        return float(obj.precio_final())
    
    def get_caracteristicas_list(self, obj):
        if obj.caracteristicas:
            return [c.strip() for c in obj.caracteristicas.split('\n') if c.strip()]
        return []

class ProductoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar productos"""
    imagenes_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Producto
        exclude = ['vistas', 'ventas_totales']
    
    def create(self, validated_data):
        imagenes_data = validated_data.pop('imagenes_upload', [])
        producto = Producto.objects.create(**validated_data)
        
        # Crear imágenes
        for i, imagen in enumerate(imagenes_data):
            ImagenProducto.objects.create(
                producto=producto,
                imagen=imagen,
                es_principal=(i == 0),
                orden=i
            )
        
        return producto
    
    def update(self, instance, validated_data):
        imagenes_data = validated_data.pop('imagenes_upload', [])
        
        # Actualizar producto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Agregar nuevas imágenes si las hay
        if imagenes_data:
            max_orden = instance.imagenes.count()
            for i, imagen in enumerate(imagenes_data):
                ImagenProducto.objects.create(
                    producto=instance,
                    imagen=imagen,
                    orden=max_orden + i
                )
        
        return instance
    
class ImagenProductoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ImagenProducto
        fields = ['imagen_producto_id', 'imagen', 'url', 'es_principal', 'orden', 'alt_text']
    
    def get_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
    
class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de producto con opciones de personalización"""
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    marca = MarcaSerializer(read_only=True)
    subcategoria = SubcategoriaSerializer(read_only=True)
    unidad_medida = UnidadMedidaSerializer(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)
    
    # Opciones de personalización
    tamanos_predefinidos = TamanoPredefinidoSerializer(many=True, read_only=True)
    terminaciones = TerminacionSerializer(many=True, read_only=True)
    tiempos_produccion = TiempoProduccionSerializer(many=True, read_only=True)
    acabados = serializers.SerializerMethodField()
    
    precio_final = serializers.SerializerMethodField()
    caracteristicas_list = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='subcategoria.categoria.nombre_categoria', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'producto_id', 'nombre_producto', 'descripcion_corta', 'detalle_producto',
            'precio_venta', 'precio_oferta', 'es_oferta',
            'imagenes', 'es_destacado', 'es_novedad', 'es_solucion_inteligente',
            'stock', 'categoria_nombre', 'marca', 'subcategoria', 'unidad_medida',
            'proveedor', 'caracteristicas_list', 'precio_final',
            'tamanos_predefinidos', 'terminaciones', 'tiempos_produccion', 'acabados',
            'tiene_personalizaciones'
        ]
        read_only_fields = fields
    
    def get_acabados(self, obj):
        """Obtiene los acabados disponibles para este producto"""
        acabados_disponibles = obj.producto_acabados.filter(
            acabado__activo=True
        ).select_related('acabado').order_by('orden')
        return AcabadoSerializer(
            [pa.acabado for pa in acabados_disponibles],
            many=True
        ).data
    
    def get_precio_final(self, obj):
        """Retorna el precio final considerando ofertas (para referencia)"""
        return float(obj.precio_final())
    
    def get_caracteristicas_list(self, obj):
        """Convierte las características de texto a lista"""
        if obj.caracteristicas:
            return [c.strip() for c in obj.caracteristicas.split('\n') if c.strip()]
        return []
    
class CarruselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrusel
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = '__all__'

class PreguntaFrecuenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaFrecuente
        fields = '__all__'

class CalcularPrecioPersonalizadoSerializer(serializers.Serializer):
    """Serializer para calcular precio dinámico basado en personalización"""
    ancho_cm = serializers.IntegerField(min_value=1)
    alto_cm = serializers.IntegerField(min_value=1)
    terminacion_id = serializers.IntegerField()
    tiempo_produccion_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1, default=1)
    acabado_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate_terminacion_id(self, value):
        """Valida que la terminación exista"""
        if not Terminacion.objects.filter(terminacion_id=value, activo=True).exists():
            raise serializers.ValidationError("Terminación no válida o inactiva")
        return value
    
    def validate_tiempo_produccion_id(self, value):
        """Valida que el tiempo de producción exista"""
        if not TiempoProduccion.objects.filter(tiempo_produccion_id=value, activo=True).exists():
            raise serializers.ValidationError("Tiempo de producción no válido o inactivo")
        return value
    
    def validate_acabado_ids(self, value):
        """Valida que los acabados existan"""
        if value:
            acabados_validos = Acabado.objects.filter(
                acabado_id__in=value,
                activo=True
            ).count()
            if acabados_validos != len(value):
                raise serializers.ValidationError("Uno o más acabados no válidos o inactivos")
        return value or []
    
    def validate(self, data):
        """Validación adicional del ancho y alto"""
        if data['ancho_cm'] <= 0 or data['alto_cm'] <= 0:
            raise serializers.ValidationError("Las dimensiones deben ser mayores a 0")
        return data
    
class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        fields = '__all__'

class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrito
        fields = '__all__'


