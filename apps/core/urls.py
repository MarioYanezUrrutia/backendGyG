from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, SubcategoriaViewSet, ProductoViewSet, CarruselViewSet, 
    ClienteViewSet, PedidoViewSet, DetallePedidoViewSet, PreguntaFrecuenteViewSet, 
    CarritoViewSet, ItemCarritoViewSet, obtener_categorias_con_productos, obtener_productos_por_subcategoria, 
    user_profile, crear_orden
)
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'subcategorias', SubcategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'carruseles', CarruselViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'detallepedidos', DetallePedidoViewSet)
router.register(r'preguntasfrecuentes', PreguntaFrecuenteViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'itemscarrito', ItemCarritoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('categorias-con-productos/', obtener_categorias_con_productos, name='categorias-con-productos'),
    path('subcategoria/<int:subcategoria_id>/productos/', obtener_productos_por_subcategoria, name='productos-por-subcategoria'),
    path('user-profile/', user_profile, name='user-profile'),
    path('crear-orden/', crear_orden, name='crear-orden'),
]


