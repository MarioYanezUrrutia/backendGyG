from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProductFile
from apps.core.models import Producto
from .serializers import ProductFileSerializer, ProductoAdminSerializer

class ProductoAdminViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoAdminSerializer

    @action(detail=True, methods=["post"])
    def upload_file(self, request, pk=None):
        producto = self.get_object()
        file_serializer = ProductFileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save(producto=producto)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductFileViewSet(viewsets.ModelViewSet):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer

