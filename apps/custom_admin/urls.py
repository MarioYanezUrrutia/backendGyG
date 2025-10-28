from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoAdminViewSet, CategoriaAdminViewSet, SubcategoriaAdminViewSet,
    CarruselAdminViewSet, MarcaAdminViewSet, UnidadMedidaAdminViewSet,
    ProveedorAdminViewSet
)

router = DefaultRouter()
router.register(r'productos', ProductoAdminViewSet, basename='productos-admin')
router.register(r'categorias', CategoriaAdminViewSet, basename='categorias-admin')
router.register(r'subcategorias', SubcategoriaAdminViewSet, basename='subcategorias-admin')
router.register(r'carrusel', CarruselAdminViewSet, basename='carrusel-admin')
router.register(r'marcas', MarcaAdminViewSet, basename='marcas-admin')
router.register(r'unidades-medida', UnidadMedidaAdminViewSet, basename='unidades-medida-admin')
router.register(r'proveedores', ProveedorAdminViewSet, basename='proveedores-admin')


urlpatterns = [
    path('', include(router.urls)),
]


