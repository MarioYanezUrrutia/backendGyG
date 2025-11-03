from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProductFile
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count
from apps.core.models import (
    Producto, ImagenProducto, Categoria, Subcategoria, Terminacion, TiempoProduccion,
    Carrusel, Marca, UnidadMedida, Proveedor
)
from .serializers import (
    ProductoAdminSerializer, ProductoListAdminSerializer, TerminacionSerializer,
    ImagenProductoAdminSerializer, CategoriaAdminSerializer, TiempoProduccionSerializer,
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
        
        if activo is not None and activo != '':  # ✅ Agregado: and activo != ''
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

    # ==================== TERMINACIONES ====================
    @action(detail=True, methods=['get', 'post'])
    def terminaciones(self, request, pk=None):
        """Obtener terminaciones de un producto"""
        producto = self.get_object()
        if request.method == 'GET':
            terminaciones = producto.terminaciones.all().order_by('orden', 'nombre_terminacion')
            serializer = TerminacionSerializer(terminaciones, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            data = request.data.copy()
            data['producto'] = producto.producto_id
            
            serializer = TerminacionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @action(detail=True, methods=['post'], url_path='terminaciones/agregar')
    # def agregar_terminacion(self, request, pk=None):
    #     """Agregar una terminación a un producto"""
    #     producto = self.get_object()
        
    #     data = request.data.copy()
    #     data['producto'] = producto.producto_id
        
    #     serializer = TerminacionSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put', 'patch'], url_path='terminaciones/(?P<terminacion_id>[^/.]+)')
    def actualizar_terminacion(self, request, pk=None, terminacion_id=None):
        """Actualizar una terminación"""
        producto = self.get_object()
        from apps.core.models import Terminacion
        from .serializers import TerminacionSerializer
        
        try:
            terminacion = producto.terminaciones.get(terminacion_id=terminacion_id)
        except Terminacion.DoesNotExist:
            return Response(
                {'error': 'Terminación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TerminacionSerializer(terminacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='terminaciones/(?P<terminacion_id>[^/.]+)/eliminar')
    def eliminar_terminacion(self, request, pk=None, terminacion_id=None):
        """Eliminar una terminación"""
        producto = self.get_object()
        from apps.core.models import Terminacion
        
        try:
            terminacion = producto.terminaciones.get(terminacion_id=terminacion_id)
            terminacion.delete()
            return Response({'message': 'Terminación eliminada'}, status=status.HTTP_200_OK)
        except Terminacion.DoesNotExist:
            return Response(
                {'error': 'Terminación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # ==================== TIEMPOS DE PRODUCCIÓN ====================
    @action(detail=True, methods=['get', 'post'], url_path='tiempos-produccion')
    def tiempos_produccion(self, request, pk=None):
        """Obtener o agregar tiempos de producción de un producto"""
        producto = self.get_object()
                
        if request.method == 'GET':
            tiempos = producto.tiempos_produccion.all().order_by('orden', 'dias_estimados')
            serializer = TiempoProduccionSerializer(tiempos, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            data = request.data.copy()
            data['producto'] = producto.producto_id
            
            serializer = TiempoProduccionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @action(detail=True, methods=['post'], url_path='tiempos-produccion/agregar')
    # def agregar_tiempo_produccion(self, request, pk=None):
    #     """Agregar un tiempo de producción a un producto"""
    #     producto = self.get_object()
    #     from apps.core.models import TiempoProduccion
    #     from .serializers import TiempoProduccionSerializer
        
    #     data = request.data.copy()
    #     data['producto'] = producto.producto_id
        
    #     serializer = TiempoProduccionSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put', 'patch'], url_path='tiempos-produccion/(?P<tiempo_id>[^/.]+)')
    def actualizar_tiempo_produccion(self, request, pk=None, tiempo_id=None):
        """Actualizar un tiempo de producción"""
        producto = self.get_object()
        from apps.core.models import TiempoProduccion
        from .serializers import TiempoProduccionSerializer
        
        try:
            tiempo = producto.tiempos_produccion.get(tiempo_produccion_id=tiempo_id)
        except TiempoProduccion.DoesNotExist:
            return Response(
                {'error': 'Tiempo de producción no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TiempoProduccionSerializer(tiempo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='tiempos-produccion/(?P<tiempo_id>[^/.]+)/eliminar')
    def eliminar_tiempo_produccion(self, request, pk=None, tiempo_id=None):
        """Eliminar un tiempo de producción"""
        producto = self.get_object()
        from apps.core.models import TiempoProduccion
        
        try:
            tiempo = producto.tiempos_produccion.get(tiempo_produccion_id=tiempo_id)
            tiempo.delete()
            return Response({'message': 'Tiempo de producción eliminado'}, status=status.HTTP_200_OK)
        except TiempoProduccion.DoesNotExist:
            return Response(
                {'error': 'Tiempo de producción no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # ==================== ACABADOS ====================
    @action(detail=True, methods=['get'])
    def acabados(self, request, pk=None):
        """Obtener acabados de un producto"""
        producto = self.get_object()
        from apps.core.models import ProductoAcabado
        from .serializers import ProductoAcabadoSerializer
        
        producto_acabados = producto.producto_acabados.all().select_related('acabado').order_by('orden')
        serializer = ProductoAcabadoSerializer(producto_acabados, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='acabados/agregar')
    def agregar_acabado(self, request, pk=None):
        """Agregar un acabado a un producto"""
        producto = self.get_object()
        from apps.core.models import ProductoAcabado, Acabado
        from .serializers import ProductoAcabadoSerializer
        
        acabado_id = request.data.get('acabado_id')
        es_predeterminado = request.data.get('es_predeterminado', False)
        orden = request.data.get('orden', 0)
        
        if not acabado_id:
            return Response(
                {'error': 'Se requiere acabado_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            acabado = Acabado.objects.get(acabado_id=acabado_id)
        except Acabado.DoesNotExist:
            return Response(
                {'error': 'Acabado no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si ya existe
        if ProductoAcabado.objects.filter(producto=producto, acabado=acabado).exists():
            return Response(
                {'error': 'Este acabado ya está asignado al producto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        producto_acabado = ProductoAcabado.objects.create(
            producto=producto,
            acabado=acabado,
            es_predeterminado=es_predeterminado,
            orden=orden
        )
        
        serializer = ProductoAcabadoSerializer(producto_acabado)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='acabados/(?P<acabado_id>[^/.]+)/eliminar')
    def eliminar_acabado(self, request, pk=None, acabado_id=None):
        """Eliminar un acabado de un producto"""
        producto = self.get_object()
        from apps.core.models import ProductoAcabado
        
        try:
            producto_acabado = ProductoAcabado.objects.get(
                producto=producto,
                acabado_id=acabado_id
            )
            producto_acabado.delete()
            return Response({'message': 'Acabado eliminado del producto'}, status=status.HTTP_200_OK)
        except ProductoAcabado.DoesNotExist:
            return Response(
                {'error': 'Acabado no encontrado en este producto'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='acabados/disponibles')
    def acabados_disponibles(self, request):
        """Obtener lista de todos los acabados disponibles"""
        from apps.core.models import Acabado
        from .serializers import AcabadoSerializer
        
        acabados = Acabado.objects.filter(activo=True).order_by('nombre_acabado')
        serializer = AcabadoSerializer(acabados, many=True)
        return Response(serializer.data)
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
