# core/views.py
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt 
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging
from .models import (
    Categoria, Subcategoria, Producto, Carrusel, Cliente, 
    Pedido, DetallePedido, PreguntaFrecuente, Carrito, ItemCarrito, ImagenProducto
)
from .serializers import(
    CategoriaSerializer, SubcategoriaSerializer, ProductoSerializer, CarruselSerializer, 
    ClienteSerializer, PedidoSerializer, DetallePedidoSerializer, PreguntaFrecuenteSerializer, 
    CarritoSerializer, ItemCarritoSerializer
) 

logger = logging.getLogger(__name__)

def obtener_categorias_con_productos(request):
    try:
        logger.info("Solicitud recibida para categorías con productos")
        
        # Obtener categorías activas con sus subcategorías
        categorias = Categoria.objects.filter(activo=True)
        
        logger.info(f"Encontradas {categorias.count()} categorías")
        
        datos_categorias = []
        
        for categoria in categorias:
            categoria_data = {
                'id': categoria.categoria_id,
                'name': categoria.nombre_categoria,
                'subcategories': []
            }
            
            # Obtener subcategorías activas de esta categoría
            subcategorias = Subcategoria.objects.filter(
                categoria=categoria,
                activo=True
            )
            
            logger.info(f"Categoría {categoria.nombre_categoria}: {subcategorias.count()} subcategorías")
            
            # Procesar cada subcategoría
            for subcategoria in subcategorias:
                # CAMBIO IMPORTANTE: Obtener TODOS los productos activos, no solo destacados
                productos = Producto.objects.filter(
                    subcategoria=subcategoria,
                    activo=True
                ).order_by('nombre_producto')  # Ordenar alfabéticamente
                
                logger.info(f"Subcategoría {subcategoria.nombre_subcategoria}: {productos.count()} productos")
                
                productos_data = []
                for producto in productos:
                    try:
                        # Obtener la primera imagen del producto si existe
                        imagen = producto.imagenes.first() if hasattr(producto, 'imagenes') else None
                        imagen_url = ''
                        
                        if imagen and hasattr(imagen, 'imagen'):
                            imagen_url = request.build_absolute_uri(imagen.imagen.url)
                        
                        producto_data = {
                            'id': producto.producto_id,
                            'name': producto.nombre_producto,
                            'price': f"${producto.precio_venta:,}".replace(',', '.') if producto.precio_venta else '$0',
                            'image': imagen_url,
                            'description': producto.detalle_producto or '',
                            'characteristics': producto.caracteristicas or ''
                        }
                        productos_data.append(producto_data)
                        logger.debug(f"Producto agregado: {producto.nombre_producto} (ID: {producto.producto_id})")
                        
                    except Exception as e:
                        logger.error(f"Error procesando producto {producto.producto_id}: {e}")
                        continue
                
                subcategoria_data = {
                    'id': subcategoria.subcategoria_id,
                    'name': subcategoria.nombre_subcategoria,
                    'products': productos_data
                }
                
                categoria_data['subcategories'].append(subcategoria_data)
            
            datos_categorias.append(categoria_data)
        
        logger.info(f"Enviando {len(datos_categorias)} categorías con productos")
        
        # Debug log para verificar estructura
        for cat in datos_categorias:
            logger.debug(f"Categoría: {cat['name']} ({cat['id']})")
            for subcat in cat['subcategories']:
                logger.debug(f"  - Subcategoría: {subcat['name']} ({subcat['id']}) - {len(subcat['products'])} productos")
        
        return JsonResponse(datos_categorias, safe=False)
        
    except Exception as e:
        logger.error(f"Error en obtener_categorias_con_productos: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)

@csrf_exempt
def obtener_productos_por_subcategoria(request, subcategoria_id):
    try:
        logger.info(f"=== SOLICITUD SUBCATEGORÍA ID: {subcategoria_id} ===")
        
        subcategoria = Subcategoria.objects.get(subcategoria_id=subcategoria_id, activo=True)
        productos = Producto.objects.filter(subcategoria=subcategoria, activo=True).order_by('nombre_producto')
        
        logger.info(f"Subcategoría encontrada: {subcategoria.nombre_subcategoria}")
        logger.info(f"Productos encontrados: {productos.count()}")
        
        productos_data = []
        for producto in productos:
            try:
                # Debug detallado de cada producto
                logger.info(f"Procesando producto: {producto.nombre_producto} (ID: {producto.producto_id})")
                
                # Obtener la primera imagen del producto con más detalle
                imagen_url = ''
                try:
                    if hasattr(producto, 'imagenes'):
                        imagen = producto.imagenes.first()
                        if imagen and hasattr(imagen, 'imagen') and imagen.imagen:
                            imagen_url = request.build_absolute_uri(imagen.imagen.url)
                            logger.info(f"Imagen encontrada para {producto.nombre_producto}: {imagen_url}")
                        else:
                            logger.warning(f"No se encontró imagen válida para {producto.nombre_producto}")
                    else:
                        logger.warning(f"El producto {producto.nombre_producto} no tiene relación con imágenes")
                except Exception as img_error:
                    logger.error(f"Error obteniendo imagen para {producto.nombre_producto}: {img_error}")
                
                producto_data = {
                    'id': producto.producto_id,  # Asegurar que el ID es correcto
                    'name': producto.nombre_producto,
                    'price': f"${producto.precio_venta:,}".replace(',', '.') if producto.precio_venta else '$0',
                    'image': imagen_url,
                    'description': producto.detalle_producto or '',
                    'characteristics': producto.caracteristicas or '',
                    # Campos adicionales para debug
                    'debug_info': {
                        'original_id': producto.producto_id,
                        'has_image': bool(imagen_url),
                        'subcategoria_id': subcategoria_id
                    }
                }
                productos_data.append(producto_data)
                logger.info(f"Producto procesado exitosamente: {producto.nombre_producto} con ID {producto.producto_id}")
                
            except Exception as e:
                logger.error(f"Error procesando producto individual {producto.producto_id}: {e}")
                continue
        
        response_data = {
            'subcategoria': {
                'id': subcategoria.subcategoria_id,
                'name': subcategoria.nombre_subcategoria,
                'categoria': subcategoria.categoria.nombre_categoria if subcategoria.categoria else ''
            },
            'products': productos_data,
            'debug': {
                'total_productos_procesados': len(productos_data),
                'subcategoria_id_solicitada': subcategoria_id
            }
        }
        
        # Log de resumen
        logger.info(f"=== RESUMEN SUBCATEGORÍA {subcategoria_id} ===")
        logger.info(f"Productos enviados: {len(productos_data)}")
        for i, prod in enumerate(productos_data):
            logger.info(f"  {i+1}. {prod['name']} (ID: {prod['id']}) - Imagen: {'Sí' if prod['image'] else 'No'}")
        
        return JsonResponse(response_data, safe=False)
        
    except Subcategoria.DoesNotExist:
        logger.error(f"Subcategoría {subcategoria_id} no encontrada")
        return JsonResponse({'error': 'Subcategoría no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error en obtener_productos_por_subcategoria: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
        
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class SubcategoriaViewSet(viewsets.ModelViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class CarruselViewSet(viewsets.ModelViewSet):
    queryset = Carrusel.objects.all()
    serializer_class = CarruselSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    @action(detail=True, methods=["get"])
    def seguimiento(self, request, pk=None):
        pedido = self.get_object()
        # Aquí se podría implementar una lógica más compleja de seguimiento
        # Por ahora, solo devolvemos el estado del pedido
        return Response({"estado": pedido.estado})

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer

class PreguntaFrecuenteViewSet(viewsets.ModelViewSet):
    queryset = PreguntaFrecuente.objects.all()
    serializer_class = PreguntaFrecuenteSerializer

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

    @action(detail=True, methods=["post"])
    def agregar_item(self, request, pk=None):
        carrito = self.get_object()
        producto_id = request.data.get("producto_id")
        cantidad = request.data.get("cantidad", 1)

        producto = get_object_or_404(Producto, pk=producto_id)
        item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            item.cantidad += int(cantidad)
        else:
            item.cantidad = int(cantidad)
        item.save()
        return Response(ItemCarritoSerializer(item).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def eliminar_item(self, request, pk=None):
        carrito = self.get_object()
        producto_id = request.data.get("producto_id")

        producto = get_object_or_404(Producto, pk=producto_id)
        item = get_object_or_404(ItemCarrito, carrito=carrito, producto=producto)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def ver_items(self, request, pk=None):
        carrito = self.get_object()
        items = ItemCarrito.objects.filter(carrito=carrito)
        serializer = ItemCarritoSerializer(items, many=True)
        return Response(serializer.data)

class ItemCarritoViewSet(viewsets.ModelViewSet):
    queryset = ItemCarrito.objects.all()
    serializer_class = ItemCarritoSerializer


