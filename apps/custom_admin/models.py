from django.db import models
from apps.core.models import Producto

class ProductFile(models.Model):
    product_file_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="archivos_adjuntos")
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to="product_files/")
    tipo_archivo = models.CharField(max_length=50, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "archivos_de_productos"

    def __str__(self):
        return f"{self.nombre_archivo} ({self.producto.nombre})"

