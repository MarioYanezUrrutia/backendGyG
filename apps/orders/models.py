from django.db import models
from apps.core.models import BaseModel, Producto, Cliente, UserProfile
import datetime

# ============= MODELOS DE PEDIDOS Y DESPACHO =============
class EstadoPedido(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    CONFIRMADO = 'CONFIRMADO', 'Confirmado'
    PREPARANDO = 'PREPARANDO', 'Preparando'
    EN_CAMINO = 'EN_CAMINO', 'En Camino'
    ENTREGADO = 'ENTREGADO', 'Entregado'
    CANCELADO = 'CANCELADO', 'Cancelado'

class Pedido(BaseModel):
    pedido_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    numero_pedido = models.CharField(max_length=20, unique=True)
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoPedido.choices,
        default=EstadoPedido.PENDIENTE
    )
    # Datos de entrega
    direccion_entrega = models.TextField()
    comuna = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    # Contacto
    telefono_contacto = models.CharField(max_length=15)
    email_contacto = models.EmailField()
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Notas
    notas_cliente = models.TextField(null=True, blank=True)
    notas_internas = models.TextField(null=True, blank=True)

    metodo_pago = models.CharField(max_length=50, default='tarjeta transbank')

    # Fechas
    fecha_estimada_entrega = models.DateField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'pedidos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Pedido {self.numero_pedido}"

    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido único
            fecha = datetime.datetime.now().strftime('%Y%m%d')
            ultimo = Pedido.objects.filter(numero_pedido__startswith=f'PED-{fecha}').count()
            self.numero_pedido = f'PED-{fecha}-{ultimo + 1:04d}'
        super().save(*args, **kwargs)

class DetallePedido(BaseModel):
    detalle_pedido_id = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    nombre_producto = models.CharField(max_length=200)  # Por si se borra el producto
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.BigIntegerField(null=True, blank=True)
    subtotal = models.BigIntegerField(null=True, blank=True)
    
    # ⭐ NUEVOS CAMPOS
    # Acabado seleccionado
    acabado = models.ForeignKey(
        'core.Acabado', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='detalles_pedido'
    )
    nombre_acabado = models.CharField(max_length=100, null=True, blank=True)  # Guardamos el nombre por si se borra
    costo_acabado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Terminación seleccionada
    terminacion = models.ForeignKey(
        'core.Terminacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detalles_pedido'
    )
    nombre_terminacion = models.CharField(max_length=100, null=True, blank=True)
    costo_terminacion = models.BigIntegerField(null=True, blank=True, default=0)
    
    # Tiempo de producción seleccionado
    tiempo_produccion = models.ForeignKey(
        'core.TiempoProduccion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detalles_pedido'
    )
    nombre_tiempo_produccion = models.CharField(max_length=100, null=True, blank=True)
    dias_produccion = models.PositiveIntegerField(null=True, blank=True)
    costo_tiempo_produccion = models.BigIntegerField(null=True, blank=True, default=0)
    
    # Datos adicionales de personalización (si aplica)
    personalizacion_texto = models.TextField(null=True, blank=True, help_text="Texto personalizado del cliente")
    archivo_cara1 = models.CharField(max_length=500, null=True, blank=True, help_text="Ruta del archivo cara 1")
    archivo_cara2 = models.CharField(max_length=500, null=True, blank=True, help_text="Ruta del archivo cara 2")
    notas_producto = models.TextField(null=True, blank=True, help_text="Notas específicas de este producto")
    
    class Meta:
        db_table = 'detalles_pedido'

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto}"

    def save(self, *args, **kwargs):
        # Calcular subtotal incluyendo acabado, terminación y tiempo de producción
        # self.subtotal = (self.cantidad * self.precio_unitario) + self.costo_acabado + self.costo_terminacion + self.costo_tiempo_produccion
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

class SeguimientoDespacho(BaseModel):
    seguimiento_id = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='seguimientos')
    estado = models.CharField(max_length=20, choices=EstadoPedido.choices)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 'seguimiento_despacho'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Seguimiento {self.pedido.numero_pedido} - {self.estado}"
    
class TamanoPredefinido(BaseModel):
    """Tamaños preestablecidos para productos personalizables"""
    tamano_id = models.AutoField(primary_key=True)
    nombre_tamano = models.CharField(max_length=100)  # ej: "A4", "Póster 50x70"
    ancho_cm = models.PositiveIntegerField()
    alto_cm = models.PositiveIntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='tamanos_predefinidos')
    es_predeterminado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'tamanos_predefinidos'

