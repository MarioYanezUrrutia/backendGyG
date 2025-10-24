# scripts/populate_database.py
import os
import sys
import django
import pandas as pd
from datetime import datetime

print("🔧 Iniciando script de población de datos...")

# =============================================================================
# CONFIGURACIÓN AUTOMÁTICA PARA RENDER Y DESARROLLO
# =============================================================================

# Determinar si estamos en Render
IS_RENDER = 'RENDER' in os.environ

# Configurar paths según el entorno
if IS_RENDER:
    # RENDER: Directorio fijo
    PROJECT_ROOT = '/opt/render/project/src'
    print("🌐 Entorno: RENDER (Producción)")
else:
    # DESARROLLO: Directorio relativo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(current_dir)  # Sube un nivel desde scripts/
    print("💻 Entorno: DESARROLLO LOCAL")

print(f"📁 Raíz del proyecto: {PROJECT_ROOT}")

# Agregar al path de Python
sys.path.append(PROJECT_ROOT)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GraficaGyG_backend.settings')

# =============================================================================
# CONFIGURACIÓN DJANGO
# =============================================================================

try:
    django.setup()
    print("✅ Django configurado correctamente")
    
    # Importar modelos
    from apps.core.models import (
        Categoria, Subcategoria, Marca, UnidadMedida, 
        Proveedor, Producto
    )
    print("✅ Modelos importados correctamente")
    
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    print("💡 Verifica:")
    print("   - Que el nombre del proyecto en settings.py sea correcto")
    print("   - Que los modelos estén en la app correcta")
    sys.exit(1)

# =============================================================================
# CLASE PRINCIPAL (FUNCIONA EN AMBOS ENTORNOS)
# =============================================================================

class DataLoader:
    def __init__(self):
        # Ruta al Excel - funciona en ambos entornos
        self.excel_file = os.path.join(PROJECT_ROOT, 'backendGyG/PoblacionTablas.xlsx')
        
        self.stats = {
            'categorias': 0, 'subcategorias': 0, 'marcas': 0,
            'unidades_medida': 0, 'proveedores': 0, 'productos': 0,
            'errors': []
        }
        
        print(f"📁 Buscando Excel en: {self.excel_file}")
    
    def check_environment(self):
        """Verificar características del entorno"""
        print(f"🔍 Verificando entorno...")
        print(f"   - RENDER: {IS_RENDER}")
        print(f"   - Python: {sys.version.split()[0]}")
        print(f"   - Django: {django.get_version()}")
        
        # Verificar pandas
        try:
            import pandas as pd
            print(f"   - Pandas: {pd.__version__}")
        except ImportError:
            print("❌ Pandas no está instalado")
            if IS_RENDER:
                print("💡 Agrega 'pandas' a requirements.txt")
            else:
                print("💡 Ejecuta: pip install pandas openpyxl")
            return False
            
        return True
    
    def check_file_exists(self):
        """Verificar que el archivo Excel existe"""
        if not os.path.exists(self.excel_file):
            print(f"❌ Archivo no encontrado: {self.excel_file}")
            if IS_RENDER:
                print("💡 En RENDER: Sube el Excel al repositorio en la raíz del proyecto")
            else:
                print("💡 En LOCAL: Coloca 'PoblacionTablas.xlsx' junto a manage.py")
            return False
        
        print("✅ Archivo Excel encontrado")
        
        # Verificar que se puede leer
        try:
            sheets = pd.ExcelFile(self.excel_file).sheet_names
            print(f"✅ Hojas disponibles: {', '.join(sheets)}")
            return True
        except Exception as e:
            print(f"❌ Error leyendo Excel: {e}")
            return False

    def safe_bool(self, value):
        """Conversión segura de booleanos para ambos entornos"""
        if pd.isna(value):
            return False
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes', 'si', 'verdadero')
    
    def parse_datetime(self, value):
        """Convertir string a datetime - robusto para ambos entornos"""
        if pd.isna(value) or value == '' or value is None:
            return datetime.now()
        try:
            return pd.to_datetime(value)
        except:
            return datetime.now()
    
    def safe_int(self, value, default=0):
        """Conversión segura a entero"""
        if pd.isna(value):
            return default
        try:
            return int(value)
        except:
            return default
    
    def safe_float(self, value, default=0.0):
        """Conversión segura a float"""
        if pd.isna(value):
            return default
        try:
            return float(value)
        except:
            return default
    
    def safe_str(self, value, default=''):
        """Conversión segura a string"""
        if pd.isna(value) or value is None:
            return default
        return str(value)
    
    # =========================================================================
    # MÉTODOS DE CARGA DE DATOS - COMPLETOS
    # =========================================================================
    
    def load_categorias(self):
        """Cargar datos de categorías - COMPLETO"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Categorias')
            print(f"📊 Cargando {len(df)} categorías...")
            
            for index, row in df.iterrows():
                try:
                    # Conversión segura para ambos entornos
                    activo = self.safe_bool(row['activo'])
                    es_popular = self.safe_bool(row['es_popular'])
                    orden_popularidad = self.safe_int(row['orden_popularidad'])
                    
                    categoria, created = Categoria.objects.update_or_create(
                        categoria_id=row['categoria_id'],
                        defaults={
                            'activo': activo,
                            'fecha_creacion': self.parse_datetime(row['fecha_creacion']),
                            'fecha_modificacion': self.parse_datetime(row['fecha_modificacion']),
                            'nombre_categoria': self.safe_str(row['nombre_categoria']),
                            'descripcion': self.safe_str(row['descripcion']),
                            'es_popular': es_popular,
                            'orden_popularidad': orden_popularidad
                        }
                    )
                    
                    if created:
                        self.stats['categorias'] += 1
                        print(f"✅ Categoría creada: {categoria.nombre_categoria}")
                    else:
                        print(f"↻ Categoría actualizada: {categoria.nombre_categoria}")
                        
                except Exception as e:
                    error_msg = f"Error en categoría ID {row['categoria_id']}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                    if not IS_RENDER:  # En desarrollo mostrar traceback completo
                        import traceback
                        traceback.print_exc()
                    continue
                    
        except Exception as e:
            error_msg = f"Error cargando categorías: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def load_subcategorias(self):
        """Cargar datos de subcategorías - COMPLETO"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Subcategorias')
            print(f"📊 Cargando {len(df)} subcategorías...")
            
            for index, row in df.iterrows():
                try:
                    # Obtener la categoría padre
                    categoria_id = self.safe_int(row['categoria_id'])
                    categoria = Categoria.objects.get(categoria_id=categoria_id)
                    
                    activo = self.safe_bool(row['activo'])
                    
                    subcategoria, created = Subcategoria.objects.update_or_create(
                        subcategoria_id=row['subcategoria_id'],
                        defaults={
                            'activo': activo,
                            'fecha_creacion': self.parse_datetime(row['fecha_creacion']),
                            'fecha_modificacion': self.parse_datetime(row['fecha_modificacion']),
                            'nombre_subcategoria': self.safe_str(row['nombre_subcategoria']),
                            'descripcion': self.safe_str(row.get('descripcion', '')),
                            'categoria': categoria
                        }
                    )
                    
                    if created:
                        self.stats['subcategorias'] += 1
                        print(f"✅ Subcategoría creada: {subcategoria.nombre_subcategoria}")
                    else:
                        print(f"↻ Subcategoría actualizada: {subcategoria.nombre_subcategoria}")
                        
                except Categoria.DoesNotExist:
                    error_msg = f"Categoría {row['categoria_id']} no existe para subcategoría {row['subcategoria_id']}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                except Exception as e:
                    error_msg = f"Error en subcategoría ID {row['subcategoria_id']}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                    continue
                    
        except Exception as e:
            error_msg = f"Error cargando subcategorías: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def load_marcas(self):
        """Cargar datos de marcas - COMPLETO"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Marcas')
            print(f"📊 Cargando {len(df)} marcas...")
            
            for index, row in df.iterrows():
                try:
                    activo = self.safe_bool(row['activo'])
                    
                    marca, created = Marca.objects.update_or_create(
                        marca_id=row['marca_id'],
                        defaults={
                            'activo': activo,
                            'fecha_creacion': self.parse_datetime(row['fecha_creacion']),
                            'fecha_modificacion': self.parse_datetime(row['fecha_modificacion']),
                            'nombre_marca': self.safe_str(row['nombre_marca'])
                        }
                    )
                    
                    if created:
                        self.stats['marcas'] += 1
                        print(f"✅ Marca creada: {marca.nombre_marca}")
                    else:
                        print(f"↻ Marca actualizada: {marca.nombre_marca}")
                        
                except Exception as e:
                    error_msg = f"Error en marca ID {row['marca_id']}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                    continue
                    
        except Exception as e:
            error_msg = f"Error cargando marcas: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def load_unidades_medida(self):
        """Cargar datos de unidades de medida - COMPLETO"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Unidades_Medida')
            print(f"📊 Cargando {len(df)} unidades de medida...")
            
            for index, row in df.iterrows():
                try:
                    activo = self.safe_bool(row['activo'])
                    
                    unidad, created = UnidadMedida.objects.update_or_create(
                        unidad_medida_id=row['unidad_medida_id'],
                        defaults={
                            'activo': activo,
                            'fecha_creacion': self.parse_datetime(row['fecha_creacion']),
                            'fecha_modificacion': self.parse_datetime(row['fecha_modificacion']),
                            'nombre_unidad_medida': self.safe_str(row['nombre_unidad_medida']),
                            'abreviatura': self.safe_str(row['abreviatura'])
                        }
                    )
                    
                    if created:
                        self.stats['unidades_medida'] += 1
                        print(f"✅ Unidad medida creada: {unidad.nombre_unidad_medida}")
                    else:
                        print(f"↻ Unidad medida actualizada: {unidad.nombre_unidad_medida}")
                        
                except Exception as e:
                    error_msg = f"Error en unidad medida ID {row['unidad_medida_id']}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                    continue
                    
        except Exception as e:
            error_msg = f"Error cargando unidades_medida: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def load_proveedores(self):
        """Cargar datos de proveedores - COMPLETO"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Proveedores')
            print(f"📊 Cargando {len(df)} proveedores...")
            
            for index, row in df.iterrows():
                try:
                    activo = self.safe_bool(row['activo'])
                    
                    # Manejar fechas vacías
                    fecha_creacion = self.parse_datetime(row.get('fecha_creacion'))
                    fecha_modificacion = self.parse_datetime(row.get('fecha_modificacion'))
                    
                    proveedor, created = Proveedor.objects.update_or_create(
                        proveedor_id=row['proveedor_id'],
                        defaults={
                            'activo': activo,
                            'fecha_creacion': fecha_creacion,
                            'fecha_modificacion': fecha_modificacion,
                            'nombre_proveedor': self.safe_str(row['nombre_proveedor']),
                            'rut_proveedor': self.safe_str(row.get('rut_proveedor', '')),
                            'contacto': self.safe_str(row.get('contacto', '')),
                            'telefono': self.safe_str(row.get('telefono', '')),
                            'email': self.safe_str(row.get('email', ''))
                        }
                    )
                    
                    if created:
                        self.stats['proveedores'] += 1
                        print(f"✅ Proveedor creado: {proveedor.nombre_proveedor}")
                    else:
                        print(f"↻ Proveedor actualizado: {proveedor.nombre_proveedor}")
                        
                except Exception as e:
                    error_msg = f"Error en proveedor ID {row['proveedor_id']}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                    continue
                    
        except Exception as e:
            error_msg = f"Error cargando proveedores: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def load_productos(self):
        """Cargar datos de productos - COMPLETO"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Productos')
            print(f"📊 Cargando {len(df)} productos...")
            
            for index, row in df.iterrows():
                try:
                    # Obtener relaciones
                    subcategoria_id = self.safe_int(row['subcategoria_id'])
                    marca_id = self.safe_int(row.get('marca_id'))
                    proveedor_id = self.safe_int(row.get('proveedor_id'))
                    unidad_medida_id = self.safe_int(row['unidad_medida_id'])
                    
                    subcategoria = Subcategoria.objects.get(subcategoria_id=subcategoria_id)
                    marca = Marca.objects.get(marca_id=marca_id) if marca_id else None
                    proveedor = Proveedor.objects.get(proveedor_id=proveedor_id) if proveedor_id else None
                    unidad_medida = UnidadMedida.objects.get(unidad_medida_id=unidad_medida_id)
                    
                    # Calcular precios según las fórmulas del Excel
                    precio_neto = self.safe_float(row['precio_neto'])
                    iva_amount = precio_neto * 0.19  # IVA 19%
                    precio_venta = precio_neto + iva_amount
                    precio_oferta = precio_venta * 0.85  # 15% descuento
                    
                    activo = self.safe_bool(row['activo'])
                    
                    producto, created = Producto.objects.update_or_create(
                        producto_id=row['producto_id'],
                        defaults={
                            'activo': activo,
                            'fecha_creacion': self.parse_datetime(row['fecha_creacion']),
                            'fecha_modificacion': self.parse_datetime(row['fecha_modificacion']),
                            'nombre_producto': self.safe_str(row['nombre_producto']),
                            'descripcion_corta': self.safe_str(row.get('descripcion_corta', '')),
                            'detalle_producto': self.safe_str(row.get('detalle_producto', '')),
                            'marca': marca,
                            'subcategoria': subcategoria,
                            'proveedor': proveedor,
                            'unidad_medida': unidad_medida,
                            'precio_neto': precio_neto,
                            'precio_venta': precio_venta,
                            'iva': True,  # Según Excel siempre tiene IVA
                            'precio_oferta': precio_oferta,
                            'stock': self.safe_int(row['stock']),
                            'stock_minimo': self.safe_int(row['stock_minimo']),
                            'ancho_cm': self.safe_float(row.get('ancho_cm')),
                            'alto_cm': self.safe_float(row.get('alto_cm')),
                            'largo_cm': self.safe_float(row.get('largo_cm'))
                        }
                    )
                    
                    if created:
                        self.stats['productos'] += 1
                        print(f"✅ Producto creado: {producto.nombre_producto}")
                    else:
                        print(f"↻ Producto actualizado: {producto.nombre_producto}")
                        
                except Subcategoria.DoesNotExist:
                    error_msg = f"Subcategoría {row['subcategoria_id']} no existe para producto {row['producto_id']}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                except Marca.DoesNotExist:
                    error_msg = f"Marca {row['marca_id']} no existe para producto {row['producto_id']}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                except UnidadMedida.DoesNotExist:
                    error_msg = f"Unidad medida {row['unidad_medida_id']} no existe para producto {row['producto_id']}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                except Exception as e:
                    error_msg = f"Error en producto ID {row['producto_id']}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                    if not IS_RENDER:
                        import traceback
                        traceback.print_exc()
                    continue
                    
        except Exception as e:
            error_msg = f"Error cargando productos: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
    
    def run_all(self):
        """Ejecutar toda la carga de datos"""
        print("🚀 Iniciando carga de datos...")
        print("=" * 50)
        
        # Verificar entorno
        if not self.check_environment():
            return
        
        # Verificar archivo
        if not self.check_file_exists():
            return
        
        print("🎯 Comenzando carga de tablas...")
        
        # Cargar datos en orden correcto (por dependencias)
        self.load_categorias()
        print("-" * 30)
        
        self.load_subcategorias()  # Depende de categorías
        print("-" * 30)
        
        self.load_marcas()
        print("-" * 30)
        
        self.load_unidades_medida()
        print("-" * 30)
        
        self.load_proveedores()
        print("-" * 30)
        
        self.load_productos()  # Depende de todos los anteriores
        print("-" * 30)
        
        # Mostrar estadísticas
        self.print_stats()

    def print_stats(self):
        """Mostrar estadísticas finales con info del entorno"""
        print("=" * 50)
        print("📊 ESTADÍSTICAS FINALES:")
        print(f"🌐 Entorno: {'RENDER' if IS_RENDER else 'DESARROLLO LOCAL'}")
        print(f"✅ Categorías: {self.stats['categorias']}")
        print(f"✅ Subcategorías: {self.stats['subcategorias']}")
        print(f"✅ Marcas: {self.stats['marcas']}")
        print(f"✅ Unidades de medida: {self.stats['unidades_medida']}")
        print(f"✅ Proveedores: {self.stats['proveedores']}")
        print(f"✅ Productos: {self.stats['productos']}")
        
        if self.stats['errors']:
            print(f"❌ Errores: {len(self.stats['errors'])}")
            for i, error in enumerate(self.stats['errors'][:10], 1):
                print(f"   {i}. {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... y {len(self.stats['errors']) - 10} errores más")
        else:
            print("🎉 ¡Todos los datos se cargaron exitosamente!")

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

def main():
    print("=" * 60)
    print("📦 SCRIPT DE POBLACIÓN DE BASE DE DATOS")
    print("   ✅ Funciona en RENDER y DESARROLLO LOCAL")
    print("=" * 60)
    
    loader = DataLoader()
    loader.run_all()
    
    print("=" * 60)
    print("🏁 Script finalizado")

if __name__ == '__main__':
    main()