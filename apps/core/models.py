from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from PIL import Image
import os
from django.conf import settings
import io
from django.core.files.base import ContentFile

class BaseModel(models.Model):
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Modelos geográficos (sin cambios)
class Pais(BaseModel):
    pais_id = models.AutoField(primary_key=True)
    nombre_pais = models.CharField(max_length=100)
    codigo_pais = models.CharField(max_length=5)
    codigo_iso = models.CharField(max_length=5)

    class Meta:
        db_table = 'paises'
        verbose_name = 'País'
        verbose_name_plural = 'Países'

    def __str__(self):
        return self.nombre_pais

class Region(BaseModel):
    region_id = models.AutoField(primary_key=True)
    nombre_region = models.CharField(max_length=100)
    codigo_region = models.CharField(max_length=5)
    pais = models.ForeignKey(Pais, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'regiones'
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'

    def __str__(self):
        return self.nombre_region

class Ciudad(BaseModel):
    ciudad_id = models.AutoField(primary_key=True)
    nombre_ciudad = models.CharField(max_length=100)
    codigo_ciudad = models.CharField(max_length=5)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'ciudades'
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'

    def __str__(self):
        return self.nombre_ciudad

class Comuna(BaseModel):
    comuna_id = models.AutoField(primary_key=True)
    nombre_comuna = models.CharField(max_length=100)
    codigo_comuna = models.CharField(max_length=5)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'comunas'
        verbose_name = 'Comuna'
        verbose_name_plural = 'Comunas'

    def __str__(self):
        return self.nombre_comuna

class Calle(BaseModel):
    calle_id = models.AutoField(primary_key=True)
    nombre_calle = models.CharField(max_length=150)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'calles'
        verbose_name = 'Calle'
        verbose_name_plural = 'Calles'

    def __str__(self):
        return self.nombre_calle

class TipoDireccion(BaseModel):
    """Modelo para tipos de dirección, particular, trabajo, comercial, etc"""
    tipo_direccion_id = models.AutoField(primary_key=True)
    nombre_tipo_direccion = models.CharField(max_length=50)
    codigo_tipo_direccion = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = 'tipos_direccion'
        verbose_name = 'Tipo de Dirección'
        verbose_name_plural = 'Tipos de Dirección'

    def __str__(self):
        return self.nombre_tipo_direccion

class Persona(BaseModel):
    """Modelo para personas"""
    persona_id = models.AutoField(primary_key=True)
    primer_nombre = models.CharField(max_length=30)
    segundo_nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=30)
    apellido_materno = models.CharField(max_length=30, blank=True, null=True)
    documento_identidad = models.CharField(max_length=15, unique=True, blank=True, null=True)
    dv = models.CharField(max_length=1, blank=True, null=True, verbose_name="Dígito Verificador")
    mail = models.EmailField(unique=True)
    cod_tel_pais = models.CharField(max_length=5, blank=True, null=True)
    cod_telefono = models.CharField(max_length=5, blank=True, null=True)
    telefono_persona = models.CharField(max_length=15, blank=True, null=True)
    cod_tel_pais_wp = models.CharField(max_length=5, blank=True, null=True)
    cod_tel_wp = models.CharField(max_length=5, blank=True, null=True)
    whatsapp_persona = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'personas'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return f"{self.primer_nombre} {self.apellido_paterno} {self.apellido_materno}"

    def nombre_completo(self):
        return f"{self.primer_nombre} {self.segundo_nombre or ''} {self.apellido_paterno} {self.apellido_materno or ''}".strip()

class Direccion(BaseModel):
    """Modelo para direcciones"""
    direccion_id = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, related_name='direcciones')
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    localizacion_google = models.CharField(max_length=150, blank=True, null=True)
    calle = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True)
    direccion_numero = models.CharField(max_length=10)
    direccion_depto = models.CharField(max_length=10, blank=True, null=True)
    direccion_block = models.CharField(max_length=10, blank=True, null=True)
    direccion_referencia = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    pais = models.ForeignKey(Pais, on_delete=models.SET_NULL, null=True)
    tipo_direccion = models.ForeignKey(TipoDireccion, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'direcciones'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return f"{self.calle} {self.direccion_numero}, {self.comuna}"

class Rol(BaseModel):
    """Modelo para roles de usuario"""
    rol_id = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)
    codigo_rol = models.CharField(max_length=10, unique=True)
    descripcion_rol = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre_rol

class UserProfile(BaseModel):
    """Modelo para perfiles de usuario"""
    user_profile_id = models.AutoField(primary_key=True)
    persona = models.OneToOneField(Persona, on_delete=models.SET_NULL, null=True, related_name='perfil')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='perfil')
    mail_verified = models.BooleanField(default=False)
    token_validacion = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'users_profile'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        if self.user:
            return f"Perfil de {self.user.username}"
        return "Perfil sin usuario asignado"
    
    def es_administrador(self):
        """Verifica si el usuario tiene rol de administrador"""
        return self.roles.filter(rol__codigo_rol='ADMIN').exists()
    
class UserRol(BaseModel):
    """Modelo para relación muchos a muchos entre UserProfile y Rol"""
    user_rol_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='roles')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'users_roles'
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuario'
        unique_together = ('user_profile', 'rol')

    def __str__(self):
        return f"{self.user_profile} - {self.rol}"

class SesionUsuario(BaseModel):
    """Modelo para sesiones de usuario"""
    sesion_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='sesiones')
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sesiones_usuario'
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'

    def __str__(self):
        return f"Sesión de {self.user_profile} - {self.fecha_inicio}" 
    
class RegistroPendiente(models.Model):
    token = models.CharField(max_length=100, unique=True)
    datos_serializados = models.JSONField()  # Aquí guardamos todos los datos del formulario
    email = models.EmailField()
    creado_en = models.DateTimeField(auto_now_add=True)
    expiracion = models.DateTimeField()

    def expirado(self):
        return timezone.now() > self.expiracion

    def __str__(self):
        return f"Registro pendiente: {self.email}"
    class Meta:
        db_table = 'registros_pendiente'
    
class VisitaPagina(models.Model):
    visita_pagina_id = models.AutoField(primary_key=True)
    ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    ruta = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ruta} - {self.fecha}"
    
    class Meta:
        db_table = 'visitas_pagina'

class Cargo(BaseModel):
    cargo_id = models.AutoField(primary_key=True)
    nombre_cargo = models.CharField(max_length=50)
    class Meta:
        db_table = 'cargos'
    def __str__(self):
        return f"Cargo #{self.cargo_id}"
  
# ============= MODELOS DE PRODUCTOS =============
class Marca(BaseModel):
    marca_id = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=30)
    logo_marca = models.ImageField(upload_to='marcas/', null=True, blank=True)
    class Meta:
        db_table = 'marcas'
    def __str__(self):
        return self.nombre_marca

class UnidadMedida(BaseModel):
    unidad_medida_id = models.AutoField(primary_key=True)
    nombre_unidad_medida = models.CharField(max_length=20)
    abreviatura = models.CharField(max_length=5, null=True, blank=True)
    
    class Meta:
        db_table = 'unidades_medida'

    def __str__(self):
        return self.nombre_unidad_medida
    
class Proveedor(BaseModel):
    proveedor_id = models.AutoField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=100)
    rut_proveedor = models.CharField(max_length=15, null=True, blank=True)
    contacto = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    class Meta:
        db_table = 'proveedores'

    def __str__(self):
        return self.nombre_proveedor
    
class Categoria(BaseModel):
    categoria_id = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    imagen_categoria = models.ImageField(upload_to='categorias/', null=True, blank=True)
    es_popular = models.BooleanField(default=False)
    orden_popularidad = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'categorias'
        ordering = ['-es_popular', 'orden_popularidad', 'nombre_categoria']

    def __str__(self):
        return self.nombre_categoria

    def productos_destacados(self, limit=4):
        return Producto.objects.filter(
            subcategoria__categoria=self,
            activo=True,
            es_destacado=True
        )[:limit]
    
class Subcategoria(BaseModel):
    subcategoria_id = models.AutoField(primary_key=True)
    nombre_subcategoria = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    imagen_subcategoria = models.ImageField(upload_to='subcategorias/', null=True, blank=True)
    
    class Meta:
        db_table = 'subcategorias'
        ordering = ['nombre_subcategoria']

    def __str__(self):
        return f"{self.categoria.nombre_categoria} - {self.nombre_subcategoria}"

# ============= OTROS MODELOS ============= 
class Cliente(BaseModel):
    cliente_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, unique=True)
    ultima_interaccion = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return f'Cliente: {self.nombre_cliente or self.telefono}'
    
class Carrusel(BaseModel):
    carrusel_id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100, null=True, blank=True)
    subtitulo = models.CharField(max_length=300, null=True, blank=True)
    imagen = models.ImageField(upload_to='carruseles/', null=True, blank=True)
    texto_boton = models.CharField(max_length=30, null=True, blank=True, default='Ver más')
    descripcion = models.TextField(null=True, blank=True)
    link_boton = models.URLField(null=True, blank=True)
    orden = models.PositiveIntegerField(default=0)

    color_fondo = models.CharField(max_length=20, null=True, blank=True, default='#2563eb')  # Azul por defecto

    class Meta:
        db_table = 'carruseles'

    def __str__(self):
        return self.titulo
    
class PreguntaFrecuente(BaseModel):
    pregunta_frecuente_id = models.AutoField(primary_key=True)
    pregunta = models.CharField(max_length=255)
    respuesta = models.TextField()
    orden = models.IntegerField(default=0, help_text="Orden de aparición (menor número aparece primero)")
    categoria = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('general', 'General'),
        ('productos', 'Productos'),
        ('envios', 'Envíos'),
        ('pagos', 'Pagos'),
        ('devoluciones', 'Devoluciones')
    ])
    
    class Meta:
        db_table = 'preguntas_frecuentes'
        verbose_name = 'Pregunta Frecuente'
        verbose_name_plural = 'Preguntas Frecuentes'
        ordering = ['orden', 'pregunta']

    def __str__(self):
        return self.pregunta

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        # Establecer el precio unitario desde el producto si no está establecido
        if not self.precio_unitario and self.producto:
            self.precio_unitario = self.producto.precio_venta
        super().save(*args, **kwargs)

# ============= MODELOS DE CARRITO =============
class Carrito(BaseModel):
    carrito_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    user_profile = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, blank=True)
    sesion_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID de sesión para usuarios no autenticados")
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carritos'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def __str__(self):
        if self.cliente:
            return f"Carrito de {self.cliente}"
        elif self.user_profile:
            return f"Carrito de {self.user_profile}"
        else:
            return f"Carrito #{self.carrito_id} (Sesión: {self.sesion_id})"
    def __str__(self):
        return f"Carrito de {self.user.username if self.user else 'Anónimo'}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class ItemCarrito(BaseModel):
    item_carrito_id = models.AutoField(primary_key=True)
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'items_carrito'
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        unique_together = ['carrito', 'producto']

    def __str__(self):
        return f"{self.cantidad} x {self.producto} en Carrito #{self.carrito.carrito_id}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        # Establecer el precio unitario desde el producto si no está establecido
        if not self.precio_unitario and self.producto:
            self.precio_unitario = self.producto.precio_venta
        super().save(*args, **kwargs)

class Terminacion(BaseModel):
    """Representa una terminación/material con precio específico para un producto."""
    terminacion_id = models.AutoField(primary_key=True)
    nombre_terminacion = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    # FOREIGN KEY: Esta terminación pertenece a un producto específico
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        related_name='terminaciones'
    )
    # Precio específico de esta terminación para este producto
    precio = models.PositiveIntegerField(default=0, null=True, blank=True,
       help_text="Precio final con esta terminación"
    )
    es_predeterminado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'terminaciones'
        verbose_name = 'Terminación'
        verbose_name_plural = 'Terminaciones'
        ordering = ['orden', 'nombre_terminacion']

    def __str__(self):
        return f"{self.nombre_terminacion} - {self.producto.nombre_producto} (${self.precio})"

class TiempoProduccion(BaseModel):
    """Representa un tiempo de producción con precio específico para un producto."""
    tiempo_produccion_id = models.AutoField(primary_key=True)
    nombre_tiempo = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    # FOREIGN KEY: Este tiempo pertenece a un producto específico
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        related_name='tiempos_produccion'
    )
    dias_estimados = models.PositiveIntegerField(help_text="Días estimados de producción")
    # Precio específico para este tiempo de producción en este producto
    precio = models.PositiveIntegerField(default=0, null=True, blank=True,
        help_text="Precio final con este tiempo de producción"
    )
    es_predeterminado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'tiempos_produccion'
        verbose_name = 'Tiempo de Producción'
        verbose_name_plural = 'Tiempos de Producción'
        ordering = ['orden', 'dias_estimados']

    def __str__(self):
        return f"{self.nombre_tiempo} ({self.dias_estimados} días) - {self.producto.nombre_producto} (${self.precio})"

class Acabado(BaseModel):
    """Representa las opciones de acabado (pueden ser compartidas entre productos)."""
    acabado_id = models.AutoField(primary_key=True)
    nombre_acabado = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    costo_adicional = models.PositiveIntegerField(default=0, null=True, blank=True,
        help_text="Costo adicional por este acabado"
    )
    
    class Meta:
        db_table = 'acabados'
        verbose_name = 'Acabado'
        verbose_name_plural = 'Acabados'

    def __str__(self):
        return f"{self.nombre_acabado} (+${self.costo_adicional})"

class ProductoAcabado(BaseModel):
    """Tabla intermedia para relacionar productos con acabados disponibles."""
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        related_name='producto_acabados'
    )
    acabado = models.ForeignKey(
        Acabado,
        on_delete=models.CASCADE,
        related_name='producto_acabados'
    )
    es_predeterminado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'productos_acabados'
        unique_together = ['producto', 'acabado']
        ordering = ['orden'] 
        verbose_name = 'Acabado del Producto'
        verbose_name_plural = 'Acabados del Producto'

    def __str__(self):
        return f"{self.producto.nombre_producto} - {self.acabado.nombre_acabado}"

class Producto(BaseModel):
    """Modelo principal de Producto."""
    producto_id = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=100)
    descripcion_corta = models.CharField(max_length=200, null=True, blank=True)
    detalle_producto = models.TextField(null=True, blank=True)
    
    # Características como JSON o texto separado por líneas
    caracteristicas = models.TextField(
        null=True, 
        blank=True,
        help_text="Una característica por línea"
    )
    
    # Especificaciones técnicas
    especificaciones = models.JSONField(
        null=True, 
        blank=True,
        help_text="Diccionario con especificaciones técnicas"
    )
    
    # Relaciones
    marca = models.ForeignKey('Marca', null=True, blank=True, on_delete=models.SET_NULL, related_name='productos')
    subcategoria = models.ForeignKey('Subcategoria', on_delete=models.CASCADE, related_name='productos')
    proveedor = models.ForeignKey('Proveedor', null=True, blank=True, on_delete=models.SET_NULL, related_name='productos')
    unidad_medida = models.ForeignKey('UnidadMedida', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Relación Many-to-Many con Acabados (los acabados sí se comparten entre productos)
    acabados = models.ManyToManyField(
        Acabado,
        through='ProductoAcabado',
        related_name='productos',
        blank=True
    )
    
    # Atributos del producto
    modelo = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    medida = models.CharField(max_length=100, null=True, blank=True)
    sku = models.CharField(max_length=50, null=True, blank=True, unique=True)
    
    # Precios e impuestos
    precio_neto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.BooleanField(default=True)
    impuesto_adicional = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Porcentaje de impuesto adicional")
    
    # Ofertas
    es_oferta = models.BooleanField(default=False)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_inicio_oferta = models.DateTimeField(null=True, blank=True)
    fecha_fin_oferta = models.DateTimeField(null=True, blank=True)
    
    # Categorización especial
    es_destacado = models.BooleanField(default=False)
    es_novedad = models.BooleanField(default=False)
    es_solucion_inteligente = models.BooleanField(default=False)
    es_insumo = models.BooleanField(default=False)
    
    # Stock y logística
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5, help_text="Alerta cuando el stock sea menor")
    ubicacion_bodega = models.CharField(max_length=100, null=True, blank=True)
    
    # Ventas al por mayor
    unidad_por_mayor = models.IntegerField(default=0, null=True, blank=True, help_text="Cantidad mínima para precio por mayor")
    precio_por_mayor = models.BigIntegerField(default=0, null=True, blank=True)
    
    # Peso y dimensiones (para envíos)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    largo_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ancho_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    alto_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Metadata
    vistas = models.PositiveIntegerField(default=0, null=True, blank=True, )
    ventas_totales = models.PositiveIntegerField(default=0, null=True, blank=True, )
    
    class Meta:
        db_table = 'productos'
        ordering = ['-es_destacado', '-es_novedad', 'nombre_producto']

    def __str__(self):
        return self.nombre_producto

    def get_absolute_url(self):
        return reverse('productos:detalle_producto', args=[str(self.producto_id)])

    def precio_final(self):
        """Retorna el precio final considerando ofertas"""
        if self.es_oferta and self.precio_oferta:
            return self.precio_oferta
        return self.precio_venta

    def tiene_stock(self, cantidad=1):
        """Verifica si hay stock disponible"""
        return self.stock >= cantidad

    def incrementar_vistas(self):
        """Incrementa el contador de vistas"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
    
    # ===== MÉTODOS PARA TERMINACIONES =====
    
    def get_terminaciones_disponibles(self):
        """Obtiene todas las terminaciones activas de este producto."""
        return self.terminaciones.filter(activo=True).order_by('orden', 'nombre_terminacion')
    
    def get_terminacion_predeterminada(self):
        """Obtiene la terminación marcada como predeterminada."""
        try:
            return self.terminaciones.filter(activo=True, es_predeterminada=True).first()
        except Terminacion.DoesNotExist:
            return self.terminaciones.filter(activo=True).first()
    
    def get_precio_por_terminacion(self, terminacion_id):
        """Obtiene el precio según la terminación seleccionada."""
        try:
            terminacion = self.terminaciones.get(terminacion_id=terminacion_id, activo=True)
            return terminacion.precio
        except Terminacion.DoesNotExist:
            return self.precio_venta
    
    # ===== MÉTODOS PARA TIEMPOS DE PRODUCCIÓN =====
    
    def get_tiempos_produccion_disponibles(self):
        """Obtiene todos los tiempos de producción activos de este producto."""
        return self.tiempos_produccion.filter(activo=True).order_by('orden', 'dias_estimados')
    
    def get_tiempo_produccion_predeterminado(self):
        """Obtiene el tiempo de producción marcado como predeterminado."""
        try:
            return self.tiempos_produccion.filter(activo=True, es_predeterminado=True).first()
        except TiempoProduccion.DoesNotExist:
            return self.tiempos_produccion.filter(activo=True).first()
    
    def get_precio_por_tiempo_produccion(self, tiempo_id):
        """Obtiene el precio según el tiempo de producción seleccionado."""
        try:
            tiempo = self.tiempos_produccion.get(tiempo_produccion_id=tiempo_id, activo=True)
            return tiempo.precio
        except TiempoProduccion.DoesNotExist:
            return self.precio_venta
    
    # ===== MÉTODOS PARA ACABADOS =====
    
    def get_acabados_disponibles(self):
        """Obtiene todos los acabados disponibles para este producto."""
        return self.producto_acabados.select_related('acabado').filter(
            acabado__activo=True
        ).order_by('orden')
    
    def get_acabado_predeterminado(self):
        """Obtiene el acabado marcado como predeterminado."""
        try:
            return self.producto_acabados.filter(
                acabado__activo=True, 
                es_predeterminado=True
            ).first()
        except ProductoAcabado.DoesNotExist:
            return self.producto_acabados.filter(acabado__activo=True).first()
    # ===== CÁLCULO DE PRECIO FINAL =====  
    def calcular_precio_personalizado(self, ancho_cm, alto_cm, terminacion_id, tiempo_produccion_id, cantidad=1, acabado_ids=None):
        """
        Calcula el precio final del producto personalizado según la fórmula:
        precio_unitario = (ancho_cm × alto_cm × precio_m2_material × precio_tiempo_produccion) / 10000
        precio_total = precio_unitario × cantidad
        
        Args:
            ancho_cm: Ancho en centímetros
            alto_cm: Alto en centímetros
            terminacion_id: ID de la terminación (material)
            tiempo_produccion_id: ID del tiempo de producción
            cantidad: Cantidad de unidades
            acabado_ids: Lista de IDs de acabados (no afecta precio, solo información)
        
        Returns:
            dict con desglose de precios y validaciones
        """
        try:
            # Obtener terminación (material con precio por 100cm)
            try:
                terminacion = self.terminaciones.get(
                    terminacion_id=terminacion_id,
                    activo=True
                )
            except Terminacion.DoesNotExist:
                return {
                    'error': True,
                    'mensaje': f'Terminación con ID {terminacion_id} no encontrada o inactiva'
                }
            
            # Obtener tiempo de producción (factor multiplicador)
            try:
                tiempo = self.tiempos_produccion.get(
                    tiempo_produccion_id=tiempo_produccion_id,
                    activo=True
                )
            except TiempoProduccion.DoesNotExist:
                return {
                    'error': True,
                    'mensaje': f'Tiempo de producción con ID {tiempo_produccion_id} no encontrado o inactivo'
                }
            
            # Validar dimensiones
            if ancho_cm <= 0 or alto_cm <= 0:
                return {
                    'error': True,
                    'mensaje': 'Las dimensiones deben ser mayores a 0'
                }
            
            # Validar cantidad
            if cantidad <= 0:
                return {
                    'error': True,
                    'mensaje': 'La cantidad debe ser mayor a 0'
                }
            
            # Validar stock
            if not self.tiene_stock(cantidad):
                return {
                    'error': True,
                    'mensaje': f'Stock insuficiente. Disponibles: {self.stock}'
                }
            
            # FÓRMULA: (ancho × alto × precio_material × precio_tiempo) / 10000
            # donde precio_material es por 100cm (no por m²)
            # precio_unitario = (ancho_cm * alto_cm * terminacion.precio * tiempo.precio) // 10000
            
            # # Si el resultado es 0 (porque es muy pequeño), al menos cobrar 1000 (ajustable)
            # if precio_unitario < 1000:
            #     precio_unitario = 1000
            
            # # Precio total por cantidad
            # precio_total = precio_unitario * cantidad
            
            # # Validar acabados si se proporcionan
            # costo_acabados = 0
            # acabados_info = []
            # Calcular costo de acabados (multiplicador acumulado)
            costo_acabados = 1  # Factor neutro si no hay acabados
            acabados_info = []

            if acabado_ids:
                acabados_disponibles = self.producto_acabados.filter(
                    acabado_id__in=acabado_ids,
                    acabado__activo=True
                ).select_related('acabado')
                
                if acabados_disponibles.count() != len(acabado_ids):
                    return {
                        'error': True,
                        'mensaje': 'Uno o más acabados no válidos o inactivos'
                    }
                
                for pa in acabados_disponibles:
                    # Multiplicar el costo adicional del acabado
                    costo_acabados *= pa.acabado.costo_adicional
                    acabados_info.append({
                        'acabado_id': pa.acabado.acabado_id,
                        'nombre_acabado': pa.acabado.nombre_acabado,
                        'costo_adicional': pa.acabado.costo_adicional
                    })
            
            # FÓRMULA CORRECTA: ((alto × ancho × acabado × terminacion) / 10000) + tiempo_produccion
            precio_base = int((ancho_cm * alto_cm * costo_acabados * terminacion.precio) / 10000)
            precio_unitario = precio_base + tiempo.precio
            
            # Precio total por cantidad
            precio_total = precio_unitario * cantidad
            
            return {
                'error': False,
                'precio_unitario': precio_unitario,
                'precio_total': precio_total,
                'cantidad': cantidad,
                'ancho_cm': ancho_cm,
                'alto_cm': alto_cm,
                'terminacion': {
                    'terminacion_id': terminacion.terminacion_id,
                    'nombre_terminacion': terminacion.nombre_terminacion,
                    'precio_por_100cm': terminacion.precio
                },
                'tiempo_produccion': {
                    'tiempo_produccion_id': tiempo.tiempo_produccion_id,
                    'nombre_tiempo': tiempo.nombre_tiempo,
                    'dias_estimados': tiempo.dias_estimados,
                    'factor_precio': float(tiempo.precio)
                },
                'acabados': acabados_info,
                'desglose': {
                    'base_calculo': f'(({ancho_cm} × {alto_cm} × {costo_acabados} × {terminacion.precio}) / 10000) + {tiempo.precio} = {precio_unitario}',
                    'total': f'{precio_unitario} × {cantidad} = {precio_total}',
                    'componentes': {
                        'area_cm2': ancho_cm * alto_cm,
                        'multiplicador_acabados': costo_acabados,
                        'precio_terminacion': terminacion.precio,
                        'precio_base': precio_base,
                        'costo_tiempo': tiempo.precio
                    }
                }
            }
        
        except Exception as e:
            return {
                'error': True,
                'mensaje': f'Error al calcular precio: {str(e)}'
            }
    
    def tiene_personalizaciones(self):
        """Verifica si el producto tiene opciones de personalización."""
        return (
            self.terminaciones.filter(activo=True).exists() or
            self.tiempos_produccion.filter(activo=True).exists() or
            self.acabados.filter(activo=True).exists()
        )
    
def producto_imagen_path(instance, filename):
    """
    Genera la ruta: productos/{producto_id}/{imagen_id}.png
    El nombre del archivo será el ID de la imagen en la BD
    """
    producto_id = instance.producto.producto_id if instance.producto else 'temp'
    
    # Si ya tenemos el ID de la imagen (cuando se actualiza)
    if instance.pk:
        return f'productos/{producto_id}/{instance.pk}.png'
    
    # Para nuevas imágenes, usamos placeholder temporal
    # Se renombrará en el método save()
    return f'productos/{producto_id}/temp_{filename}'

class ImagenProducto(BaseModel):
    imagen_producto_id = models.AutoField(primary_key=True)
    imagen = models.ImageField(upload_to=producto_imagen_path)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    es_principal = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    alt_text = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 'imagenes_productos'
        ordering = ['-es_principal', 'orden']

    def __str__(self):
        return f"Imagen de {self.producto.nombre_producto}"

    def save(self, *args, **kwargs):
        es_nueva = self.pk is None
        
        # Guardar primero para obtener el PK
        super(ImagenProducto, self).save(*args, **kwargs)
        
        # Si es nueva imagen y tiene archivo
        if es_nueva and self.imagen:
            try:
                # Obtener ruta actual del archivo temporal
                old_path = self.imagen.path
                
                if os.path.exists(old_path):
                    # Procesar la imagen
                    img = Image.open(old_path)
                    
                    # Convertir a RGB si es necesario
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    # Redimensionar
                    max_size = (800, 600)
                    img.thumbnail(max_size, Image.Lanczos)
                    
                    # Crear nueva ruta con el ID de la imagen
                    producto_id = self.producto.producto_id
                    new_filename = f'{self.pk}.png'
                    new_path = os.path.join(settings.MEDIA_ROOT, f'productos/{producto_id}/{new_filename}')
                    
                    # Crear directorio si no existe
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    # Guardar imagen procesada con nuevo nombre
                    img.save(new_path, 'PNG', optimize=True, quality=85)
                    
                    # Eliminar archivo temporal si tiene nombre diferente
                    if old_path != new_path and os.path.exists(old_path):
                        os.remove(old_path)
                    
                    # Actualizar el campo imagen con la nueva ruta
                    self.imagen.name = f'productos/{producto_id}/{new_filename}'
                    super(ImagenProducto, self).save(update_fields=['imagen'])
                    
            except Exception as e:
                print(f"Error procesando imagen {self.pk}: {e}")
