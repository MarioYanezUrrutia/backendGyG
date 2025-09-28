# generar_datos_prueba.py
import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GraficaGyG_backend.settings')
django.setup()

from apps.core.models import Categoria, Subcategoria, Producto, Marca, UnidadMedida, Proveedor
from django.core.files import File
from io import BytesIO
from PIL import Image
import random

def crear_imagen_ficticia(nombre, ancho=400, alto=300):
    """Crea una imagen ficticia con texto"""
    color_fondo = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
    color_texto = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
    
    imagen = Image.new('RGB', (ancho, alto), color_fondo)
    
    # Guardar en memoria
    buffer = BytesIO()
    imagen.save(buffer, format='PNG')
    buffer.seek(0)
    
    return File(buffer, name=f'{nombre}.png')

def generar_datos_prueba():
    print("Generando datos de prueba...")
    
    # Crear marcas
    marcas = []
    nombres_marcas = ['HP', 'Canon', 'Epson', 'Xerox', 'Brother', 'Samsung', 'Dell', 'Lenovo']
    for nombre in nombres_marcas:
        marca, created = Marca.objects.get_or_create(nombre_marca=nombre)
        marcas.append(marca)
        print(f"Marca creada: {nombre}")

    # Crear unidades de medida
    unidades = []
    nombres_unidades = ['Unidad', 'Caja', 'Paquete', 'Rollo', 'Resma']
    for nombre in nombres_unidades:
        unidad, created = UnidadMedida.objects.get_or_create(nombre_unidad_medida=nombre)
        unidades.append(unidad)
        print(f"Unidad creada: {nombre}")

    # Crear proveedores
    proveedores = []
    nombres_proveedores = ['Proveedor A', 'Proveedor B', 'Proveedor C', 'Distribuidor X', 'Suministros Y']
    for nombre in nombres_proveedores:
        proveedor, created = Proveedor.objects.get_or_create(nombre_proveedor=nombre)
        proveedores.append(proveedor)
        print(f"Proveedor creado: {nombre}")

    # Crear categorías y subcategorías
    categorias_data = {
        'Impresión y Papelería': [
            'Impresoras',
            'Tóner y Cartuchos',
            'Papel',
            'Tintas'
        ],
        'Computación': [
            'Computadores',
            'Periféricos',
            'Accesorios',
            'Software'
        ],
        'Oficina': [
            'Muebles',
            'Organización',
            'Escritura',
            'Archivo'
        ],
        'Arte y Diseño': [
            'Materiales',
            'Herramientas',
            'Papeles Especiales',
            'Impresión Fine Art'
        ]
    }

    categorias_obj = {}
    subcategorias_obj = {}

    for categoria_nombre, subcategorias in categorias_data.items():
        categoria, created = Categoria.objects.get_or_create(
            nombre_categoria=categoria_nombre,
            defaults={'es_popular': True if categoria_nombre in ['Impresión y Papelería', 'Computación'] else False}
        )
        categorias_obj[categoria_nombre] = categoria
        print(f"Categoría creada: {categoria_nombre}")

        for subcategoria_nombre in subcategorias:
            subcategoria, created = Subcategoria.objects.get_or_create(
                nombre_subcategoria=subcategoria_nombre,
                categoria=categoria
            )
            subcategorias_obj[subcategoria_nombre] = subcategoria
            print(f"  Subcategoría creada: {subcategoria_nombre}")

    # Datos de productos de ejemplo
    productos_data = [
        # Impresión y Papelería -> Impresoras
        {
            'nombre': 'Impresora Laser HP LaserJet Pro',
            'subcategoria': 'Impresoras',
            'precio': 299900,
            'detalle': 'Impresora láser monocromática de alto rendimiento',
            'caracteristicas': 'Wi-Fi, Ethernet, USB, 22 ppm',
            'marca': 'HP',
            'stock': 15
        },
        {
            'nombre': 'Impresora Multifuncional Canon PIXMA',
            'subcategoria': 'Impresoras',
            'precio': 189900,
            'detalle': 'Impresora multifuncional a color',
            'caracteristicas': 'Escáner, copiadora, Wi-Fi',
            'marca': 'Canon',
            'stock': 20
        },
        
        # Impresión y Papelería -> Tóner y Cartuchos
        {
            'nombre': 'Cartucho de Tinta HP 664 Negro',
            'subcategoria': 'Tóner y Cartuchos',
            'precio': 29990,
            'detalle': 'Cartucho de tinta original HP',
            'caracteristicas': 'Alto rendimiento, calidad profesional',
            'marca': 'HP',
            'stock': 100
        },
        {
            'nombre': 'Tóner Brother TN-660',
            'subcategoria': 'Tóner y Cartuchos',
            'precio': 45990,
            'detalle': 'Tóner original Brother',
            'caracteristicas': 'Rendimiento: 2,600 páginas',
            'marca': 'Brother',
            'stock': 50
        },
        
        # Impresión y Papelería -> Papel
        {
            'nombre': 'Papel Carta 75 grs x 500 hojas',
            'subcategoria': 'Papel',
            'precio': 12990,
            'detalle': 'Papel bond blanco 75 gramos',
            'caracteristicas': '500 hojas, formato carta',
            'marca': 'Xerox',
            'stock': 200
        },
        {
            'nombre': 'Papel Fotográfico Brillante A4',
            'subcategoria': 'Papel',
            'precio': 24990,
            'detalle': 'Papel fotográfico de alta calidad',
            'caracteristicas': '50 hojas, superficie brillante',
            'marca': 'Canon',
            'stock': 75
        },
        
        # Computación -> Periféricos
        {
            'nombre': 'Teclado Mecánico RGB',
            'subcategoria': 'Periféricos',
            'precio': 89990,
            'detalle': 'Teclado mecánico gaming',
            'caracteristicas': 'RGB, switches azules, anti-ghosting',
            'marca': 'HP',
            'stock': 30
        },
        {
            'nombre': 'Mouse Inalámbrico Ergonómico',
            'subcategoria': 'Periféricos',
            'precio': 39990,
            'detalle': 'Mouse ergonómico para oficina',
            'caracteristicas': 'Inalámbrico, 1600 DPI, 2.4GHz',
            'marca': 'Dell',
            'stock': 40
        },
        
        # Oficina -> Escritura
        {
            'nombre': 'Set de Bolígrafos Profesionales',
            'subcategoria': 'Escritura',
            'precio': 15990,
            'detalle': 'Set de 12 bolígrafos de colores',
            'caracteristicas': 'Punta fina, tinta de secado rápido',
            'marca': None,
            'stock': 150
        },
        {
            'nombre': 'Marcadores Permanentes Sharpie',
            'subcategoria': 'Escritura',
            'precio': 12990,
            'detalle': 'Pack de 8 marcadores permanentes',
            'caracteristicas': 'Punta fina, varios colores',
            'marca': None,
            'stock': 80
        },
        
        # Arte y Diseño -> Materiales
        {
            'nombre': 'Block de Sketch A3 180 grs',
            'subcategoria': 'Materiales',
            'precio': 18990,
            'detalle': 'Block de papel para sketching',
            'caracteristicas': '50 hojas, grano medio, 180 grs',
            'marca': None,
            'stock': 60
        },
        {
            'nombre': 'Set de Acrílicos Profesionales',
            'subcategoria': 'Materiales',
            'precio': 45990,
            'detalle': 'Set de 12 tubos de acrílico',
            'caracteristicas': 'Colores primarios y secundarios',
            'marca': None,
            'stock': 25
        }
    ]

    # Crear productos
    for i, producto_data in enumerate(productos_data):
        try:
            subcategoria = subcategorias_obj[producto_data['subcategoria']]
            marca_obj = None
            if producto_data['marca']:
                marca_obj = next((m for m in marcas if m.nombre_marca == producto_data['marca']), None)
            
            producto, created = Producto.objects.get_or_create(
                nombre_producto=producto_data['nombre'],
                defaults={
                    'subcategoria': subcategoria,
                    'precio_venta': producto_data['precio'],
                    'precio_neto': producto_data['precio'] * 0.8,  # 20% menos
                    'detalle_producto': producto_data['detalle'],
                    'caracteristicas': producto_data['caracteristicas'],
                    'marca': marca_obj,
                    'stock': producto_data['stock'],
                    'unidad_medida': unidades[0],  # Primera unidad
                    'proveedor': random.choice(proveedores),
                    'es_destacado': random.choice([True, False]),
                    'es_oferta': random.choice([True, False]),
                    'precio_oferta': producto_data['precio'] * 0.9 if random.choice([True, False]) else 0,
                    'color': random.choice(['Negro', 'Blanco', 'Azul', 'Rojo', 'Verde', None]),
                    'medida': random.choice(['Standard', 'Grande', 'Pequeño', None])
                }
            )
            
            if created:
                print(f"Producto creado: {producto_data['nombre']}")
            else:
                print(f"Producto ya existía: {producto_data['nombre']}")
                
        except Exception as e:
            print(f"Error creando producto {producto_data['nombre']}: {e}")

    print("\n¡Datos de prueba generados exitosamente!")
    print(f"- {Categoria.objects.count()} categorías creadas")
    print(f"- {Subcategoria.objects.count()} subcategorías creadas")
    print(f"- {Producto.objects.count()} productos creados")
    print(f"- {Marca.objects.count()} marcas creadas")

if __name__ == '__main__':
    generar_datos_prueba()