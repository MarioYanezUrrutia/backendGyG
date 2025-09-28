from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

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
    documento_identidad = models.CharField(max_length=15, unique=True)
    dv = models.CharField(max_length=1, verbose_name="Dígito Verificador")
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

class Cliente(BaseModel):
    cliente_id = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, unique=True)
    ultima_interaccion = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return f'Cliente: {self.nombre_cliente or self.telefono}'

class Categoria(BaseModel):
    categoria_id = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=30)
    es_popular = models.BooleanField(default=False)
    codigo_popular = models.IntegerField(default=0, null=True, blank=True)
    def productos_destacados(self, limit=4):
        return Producto.objects.filter(
            subcategoria__categoria=self,
            activo=True,
            es_destacado=True
        )[:limit]
    class Meta:
        db_table = 'categorias'
    def __str__(self):
        return self.nombre_categoria

class Subcategoria(BaseModel):
    subcategoria_id = models.AutoField(primary_key=True)
    nombre_subcategoria = models.CharField(max_length=30)
    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = 'subcategorias'
    def __str__(self):
        return self.nombre_subcategoria

class UnidadMedida(BaseModel):
    unidad_medida_id = models.AutoField(primary_key=True)
    nombre_unidad_medida = models.CharField(max_length=20)
    class Meta:
        db_table = 'unidades_medida'
    def __str__(self):
        return self.nombre_unidad_medida

class Proveedor(BaseModel):
    proveedor_id = models.AutoField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=30)
    class Meta:
        db_table = 'proveedores'
    def __str__(self):
        return self.nombre_proveedor
    
class Marca(BaseModel):
    marca_id = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=30)
    class Meta:
        db_table = 'marcas'
    def __str__(self):
        return self.nombre_marca

class Iva(BaseModel):
    iva_id = models.AutoField(primary_key=True)
    valor_iva = models.DecimalField(max_digits=10, decimal_places=2)
    pais = models.ForeignKey(Pais, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = 'ivas'

def producto_imagen_path(instance, filename):
    # Extraemos el ID del producto
    producto_id = instance.producto.producto_id if instance.producto else None
    
    # Si tenemos un ID de producto, lo usamos para crear la carpeta
    if producto_id:
        # No usamos la extensión original, siempre usaremos PNG
        # El nombre será simplemente [imagen_id]_[producto_id].png
        if instance.pk:  # Si ya tenemos un ID de imagen
            new_filename = f"{instance.pk}_{producto_id}.png"
        else:
            # Para nuevas imágenes, usamos un placeholder temporal
            # que será actualizado después en el método save()
            new_filename = f"temp_{producto_id}.png"
        
        # Usamos posix path (forward slash) para asegurar consistencia
        return f'productos/{producto_id}/{new_filename}'
    
    # Si no hay producto_id, guardamos en una carpeta temporal
    return f'productos/temp/{filename}'

class Producto(BaseModel):
    producto_id = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=50)
    detalle_producto = models.TextField(null=True, blank=True)
    caracteristicas = models.TextField(null=True, blank=True)
    marca = models.ForeignKey(Marca, null=True, blank=True, on_delete=models.SET_NULL)
    modelo = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    es_oferta = models.BooleanField(default=False, null=True, blank=True)
    precio_oferta = models.IntegerField(default=0, null=True, blank=True)
    es_destacado = models.BooleanField(default=False)
    medida = models.CharField(max_length=100, null=True, blank=True)
    unidad_medida = models.ForeignKey(UnidadMedida, null=True, blank=True, on_delete=models.SET_NULL)
    subcategoria = models.ForeignKey(Subcategoria, null=True, blank=True, on_delete=models.SET_NULL)
    unidad_por_mayor = models.IntegerField(default=0, null=True, blank=True)
    valor_unidad_por_mayor = models.IntegerField(default=0, null=True, blank=True)
    precio_neto = models.IntegerField(default=0, null=True, blank=True)
    precio_venta = models.IntegerField(default=0, null=True, blank=True)
    iva = models.BooleanField(default=True, null=True, blank=True)
    impuesto_10pc = models.BooleanField(default=False, null=True, blank=True)
    es_insumo = models.BooleanField(default=False, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, null=True, blank=True, on_delete=models.SET_NULL)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    #Atributo en el cual donde debería ir el producto en bodega
    ubicacion_estante_bodega = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = 'productos'

    def get_absolute_url(self):
        """Retorna la URL del detalle del producto"""
        return reverse('productos:detalle_producto', args=[str(self.producto_id)])
    
    def __str__(self):
        return self.nombre_producto

class ImagenProducto(BaseModel):
    imagen_producto_id = models.AutoField(primary_key=True)
    imagen = models.ImageField(upload_to=producto_imagen_path, null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, related_name='imagenes')
    
    class Meta:
        db_table = 'imagenes_productos'
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre_producto}" if self.producto else "Imagen sin producto asociado"
    
    def save(self, *args, **kwargs):
        # Para nuevas instancias, primero guardamos para obtener un ID
        is_new = not self.pk
        super(ImagenProducto, self).save(*args, **kwargs)
        
        # Si es una instancia nueva o tenemos una imagen
        if self.imagen:
            from PIL import Image
            import os
            from django.conf import settings
            import io
            from django.core.files.base import ContentFile
            
            # Procesamos la imagen
            try:
                # Obtenemos la ruta completa de la imagen en el sistema de archivos
                img_path = os.path.join(settings.MEDIA_ROOT, self.imagen.name)
                
                # Verificamos si el archivo existe
                if os.path.exists(img_path):
                    # Abrimos la imagen
                    img = Image.open(img_path)
                    
                    # Redimensionar para tamaños adecuados
                    max_size = (800, 600)  # Tamaño adecuado para visualización
                    img.thumbnail(max_size, Image.LANCZOS)
                    
                    # Si la imagen no es PNG, la convertimos
                    if img.format != 'PNG':
                        # Creamos un buffer para la imagen convertida
                        buffer = io.BytesIO()
                        # Guardamos en formato PNG
                        img.save(buffer, format='PNG')
                        # Volvemos al inicio del buffer
                        buffer.seek(0)
                        
                        # Construimos el nuevo nombre de archivo
                        producto_id = self.producto.producto_id if self.producto else 0
                        new_filename = f"{self.pk}_{producto_id}.png"
                        
                        # Construimos la ruta de directorio (asegurando forward slashes)
                        dir_path = f"productos/{producto_id}"
                        
                        # Eliminamos el archivo anterior
                        self.imagen.delete(save=False)
                        
                        # Guardamos la nueva imagen
                        self.imagen.save(
                            f"{dir_path}/{new_filename}",
                            ContentFile(buffer.getvalue()),
                            save=False
                        )
                        
                        # Aseguramos que la ruta usa forward slashes
                        self.imagen.name = self.imagen.name.replace('\\', '/')
                        
                        # Guardamos solo el campo de imagen actualizado
                        super(ImagenProducto, self).save(update_fields=['imagen'])
                    elif is_new or 'temp_' in self.imagen.name:
                        # Si es una imagen nueva o tiene nombre temporal pero ya es PNG
                        # Solo renombramos para asegurar el formato correcto
                        producto_id = self.producto.producto_id if self.producto else 0
                        new_filename = f"{self.pk}_{producto_id}.png"
                        
                        # Construimos la ruta de directorio
                        dir_path = f"productos/{producto_id}"
                        
                        # Creamos un buffer para la imagen
                        buffer = io.BytesIO()
                        img.save(buffer, format='PNG')
                        buffer.seek(0)
                        
                        # Eliminamos el archivo anterior
                        self.imagen.delete(save=False)
                        
                        # Guardamos con el nuevo nombre
                        self.imagen.save(
                            f"{dir_path}/{new_filename}",
                            ContentFile(buffer.getvalue()),
                            save=False
                        )
                        
                        # Aseguramos que la ruta usa forward slashes
                        self.imagen.name = self.imagen.name.replace('\\', '/')
                        
                        # Guardamos solo el campo de imagen actualizado
                        super(ImagenProducto, self).save(update_fields=['imagen'])
            except Exception as e:
                print(f"Error procesando imagen: {e}")
    
class Carrusel(BaseModel):
    carrusel_id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100, null=True, blank=True)
    imagen = models.ImageField(upload_to='carruseles/', null=True, blank=True)
    texto_boton = models.CharField(max_length=30, null=True, blank=True, default='Ver más')
    descripcion = models.TextField(null=True, blank=True)
    link_boton = models.URLField(null=True, blank=True)

    color_fondo = models.CharField(max_length=20, null=True, blank=True, default='#2563eb')  # Azul por defecto

    class Meta:
        db_table = 'carruseles'

    def __str__(self):
        return self.titulo

# models.py (agregar estos modelos al final del archivo)

class Pedido(BaseModel):
    pedido_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    user_profile = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado')
    ])
    total = models.IntegerField(default=0)
    direccion_entrega = models.ForeignKey('Direccion', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'pedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido #{self.pedido_id} - {self.cliente}"

class DetallePedido(BaseModel):
    detalle_pedido_id = models.AutoField(primary_key=True)
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.IntegerField(default=0)
    subtotal = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'detalles_pedido'
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def __str__(self):
        return f"Detalle #{self.detalle_pedido_id} - Pedido #{self.pedido.pedido_id}"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente antes de guardar
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

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