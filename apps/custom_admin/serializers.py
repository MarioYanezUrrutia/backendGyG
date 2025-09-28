from rest_framework import serializers
from .models import ProductFile
from apps.core.models import Producto

class ProductFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
        fields = '__all__'

class ProductoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


