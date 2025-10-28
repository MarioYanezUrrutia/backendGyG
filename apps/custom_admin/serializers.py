from rest_framework import serializers
from .models import ProductFile
from apps.core.models import (
    Producto, ImagenProducto, Categoria, Subcategoria, 
    Carrusel, Marca, UnidadMedida, Proveedor
)

class ProductFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
        fields = '__all__'

# ==================== SERIALIZERS BÁSICOS ====================
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

# ==================== CATEGORIA ====================
class CategoriaAdminSerializer(serializers.ModelSerializer):
    total_subcategorias = serializers.SerializerMethodField()
    total_productos = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = '__all__'
    
    def get_total_subcategorias(self, obj):
        return obj.subcategorias.count()
    
    def get_total_productos(self, obj):
        return Producto.objects.filter(subcategoria__categoria=obj).count()
    
    def get_imagen_url(self, obj):
        if obj.imagen_categoria:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen_categoria.url)
            return obj.imagen_categoria.url
        return None

# ==================== SUBCATEGORIA ====================
class SubcategoriaAdminSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre_categoria', read_only=True)
    total_productos = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Subcategoria
        fields = '__all__'
    
    def get_total_productos(self, obj):
        return obj.productos.count()
    
    def get_imagen_url(self, obj):
        if obj.imagen_subcategoria:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen_subcategoria.url)
            return obj.imagen_subcategoria.url
        return None

# ==================== IMAGEN PRODUCTO ====================
class ImagenProductoAdminSerializer(serializers.ModelSerializer):
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

# ==================== PRODUCTO ADMIN ====================
class ProductoAdminSerializer(serializers.ModelSerializer):
    imagenes = ImagenProductoAdminSerializer(many=True, read_only=True)
    imagenes_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Lista de imágenes para subir"
    )
    
    # Campos de solo lectura para mostrar información relacionada
    categoria_nombre = serializers.CharField(source='subcategoria.categoria.nombre_categoria', read_only=True)
    subcategoria_nombre = serializers.CharField(source='subcategoria.nombre_subcategoria', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre_marca', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_proveedor', read_only=True)
    unidad_medida_nombre = serializers.CharField(source='unidad_medida.nombre_unidad_medida', read_only=True)
    
    # Campos calculados
    precio_final = serializers.SerializerMethodField()
    tiene_stock = serializers.SerializerMethodField()
    total_imagenes = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = '__all__'
        extra_kwargs = {
            'vistas': {'read_only': True},
            'ventas_totales': {'read_only': True},
        }
    
    def get_precio_final(self, obj):
        return float(obj.precio_final())
    
    def get_tiene_stock(self, obj):
        return obj.stock > 0
    
    def get_total_imagenes(self, obj):
        return obj.imagenes.count()
    
    def create(self, validated_data):
        imagenes_data = validated_data.pop('imagenes_upload', [])
        
        # Crear producto
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
        
        # Actualizar campos del producto
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

class ProductoListAdminSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados en el panel admin"""
    imagen_principal = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='subcategoria.categoria.nombre_categoria', read_only=True)
    subcategoria_nombre = serializers.CharField(source='subcategoria.nombre_subcategoria', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre_marca', read_only=True)
    precio_final = serializers.SerializerMethodField()
    tiene_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'producto_id', 'nombre_producto', 'sku', 'precio_venta', 
            'precio_oferta', 'es_oferta', 'precio_final', 'stock', 
            'tiene_stock', 'imagen_principal', 'categoria_nombre', 
            'subcategoria_nombre', 'marca_nombre', 'activo', 
            'es_destacado', 'es_novedad'
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
    
    def get_tiene_stock(self, obj):
        return obj.stock > 0

# ==================== CARRUSEL ====================
class CarruselAdminSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Carrusel
        fields = '__all__'
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None