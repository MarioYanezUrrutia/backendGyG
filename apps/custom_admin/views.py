from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProductFile
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count
from apps.core.models import (
    Producto, ImagenProducto, Categoria, Subcategoria, 
    Carrusel, Marca, UnidadMedida, Proveedor
)
from .serializers import (
    ProductoAdminSerializer, ProductoListAdminSerializer,
    ImagenProductoAdminSerializer, CategoriaAdminSerializer,
    SubcategoriaAdminSerializer, CarruselAdminSerializer,
    MarcaSerializer, UnidadMedidaSerializer, ProveedorSerializer
)
from .permissions import EsAdministrador

# ==================== PRODUCTOS ====================
class ProductoAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet para administración completa de productos
    Solo accesible para administradores
    """
    queryset = Producto.objects.all().select_related(
        'marca', 'subcategoria', 'subcategoria__categoria', 
        'proveedor', 'unidad_medida'
    ).prefetch_related('imagenes')
    permission_classes = [EsAdministrador]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListAdminSerializer
        return ProductoAdminSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        search = self.request.query_params.get('search', None)
        categoria_id = self.request.query_params.get('categoria', None)
        subcategoria_id = self.request.query_params.get('subcategoria', None)
        marca_id = self.request.query_params.get('marca', None)
        activo = self.request.query_params.get('activo', None)
        
        if search:
            queryset = queryset.filter(
                Q(nombre_producto__icontains=search) |
                Q(sku__icontains=search) |
                Q(descripcion_corta__icontains=search)
            )
        
        if categoria_id:
            queryset = queryset.filter(subcategoria__categoria_id=categoria_id)
        
        if subcategoria_id:
            queryset = queryset.filter(subcategoria_id=subcategoria_id)
        
        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)
        
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        return queryset.order_by('-fecha_creacion')
    
    @action(detail=True, methods=['post'])
    def agregar_imagenes(self, request, pk=None):
        """Endpoint para agregar imágenes a un producto existente"""
        producto = self.get_object()
        imagenes = request.FILES.getlist('imagenes')
        
        if not imagenes:
            return Response(
                {'error': 'No se enviaron imágenes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        imagenes_creadas = []
        max_orden = producto.imagenes.count()
        
        for i, imagen in enumerate(imagenes):
            imagen_obj = ImagenProducto.objects.create(
                producto=producto,
                imagen=imagen,
                orden=max_orden + i
            )
            imagenes_creadas.append(
                ImagenProductoAdminSerializer(imagen_obj, context={'request': request}).data
            )
        
        return Response({
            'message': f'{len(imagenes_creadas)} imágenes agregadas exitosamente',
            'imagenes': imagenes_creadas
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def eliminar_imagen(self, request, pk=None):
        """Eliminar una imagen específica de un producto"""
        producto = self.get_object()
        imagen_id = request.data.get('imagen_id')
        
        if not imagen_id:
            return Response(
                {'error': 'Se requiere imagen_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            imagen = producto.imagenes.get(imagen_producto_id=imagen_id)
            imagen.delete()
            return Response({
                'message': 'Imagen eliminada exitosamente'
            })
        except ImagenProducto.DoesNotExist:
            return Response(
                {'error': 'Imagen no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def establecer_imagen_principal(self, request, pk=None):
        """Establecer una imagen como principal"""
        producto = self.get_object()
        imagen_id = request.data.get('imagen_id')
        
        if not imagen_id:
            return Response(
                {'error': 'Se requiere imagen_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Quitar principal de todas las imágenes
            producto.imagenes.update(es_principal=False)
            
            # Establecer la nueva imagen principal
            imagen = producto.imagenes.get(imagen_producto_id=imagen_id)
            imagen.es_principal = True
            imagen.save()
            
            return Response({
                'message': 'Imagen principal actualizada',
                'imagen': ImagenProductoAdminSerializer(imagen, context={'request': request}).data
            })
        except ImagenProducto.DoesNotExist:
            return Response(
                {'error': 'Imagen no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas generales de productos"""
        stats = {
            'total_productos': Producto.objects.count(),
            'productos_activos': Producto.objects.filter(activo=True).count(),
            'productos_sin_stock': Producto.objects.filter(stock=0).count(),
            'productos_destacados': Producto.objects.filter(es_destacado=True).count(),
            'productos_en_oferta': Producto.objects.filter(es_oferta=True).count(),
            'productos_novedades': Producto.objects.filter(es_novedad=True).count(),
        }
        return Response(stats)

# ==================== CATEGORÍAS ====================
class CategoriaAdminViewSet(viewsets.ModelViewSet):
    """ViewSet para administración de categorías"""
    queryset = Categoria.objects.all().prefetch_related('subcategorias')
    serializer_class = CategoriaAdminSerializer
    permission_classes = [EsAdministrador]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(nombre_categoria__icontains=search)
        
        return queryset.order_by('nombre_categoria')

# ==================== SUBCATEGORÍAS ====================
class SubcategoriaAdminViewSet(viewsets.ModelViewSet):
    """ViewSet para administración de subcategorías"""
    queryset = Subcategoria.objects.all().select_related('categoria')
    serializer_class = SubcategoriaAdminSerializer
    permission_classes = [EsAdministrador]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria', None)
        search = self.request.query_params.get('search', None)
        
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        if search:
            queryset = queryset.filter(nombre_subcategoria__icontains=search)
        
        return queryset.order_by('categoria__nombre_categoria', 'nombre_subcategoria')

# ==================== CARRUSEL ====================
class CarruselAdminViewSet(viewsets.ModelViewSet):
    """ViewSet para administración del carrusel"""
    queryset = Carrusel.objects.all()
    serializer_class = CarruselAdminSerializer
    permission_classes = [EsAdministrador]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        return super().get_queryset().order_by('orden', '-fecha_creacion')
    
    @action(detail=False, methods=['post'])
    def reordenar(self, request):
        """Reordenar elementos del carrusel"""
        orden_ids = request.data.get('orden', [])
        
        for index, carrusel_id in enumerate(orden_ids):
            try:
                carrusel = Carrusel.objects.get(carrusel_id=carrusel_id)
                carrusel.orden = index
                carrusel.save(update_fields=['orden'])
            except Carrusel.DoesNotExist:
                pass
        
        return Response({'message': 'Orden actualizado correctamente'})

# ==================== MARCAS ====================
class MarcaAdminViewSet(viewsets.ModelViewSet):
    """ViewSet para administración de marcas"""
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [EsAdministrador]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

# ==================== UNIDADES DE MEDIDA ====================
class UnidadMedidaAdminViewSet(viewsets.ModelViewSet):
    """ViewSet para administración de unidades de medida"""
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer
    permission_classes = [EsAdministrador]

# ==================== PROVEEDORES ====================
class ProveedorAdminViewSet(viewsets.ModelViewSet):
    """ViewSet para administración de proveedores"""
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [EsAdministrador]
