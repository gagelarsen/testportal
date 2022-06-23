from rest_framework import generics

from testportal.models import Product

from testportal_api.serializers import ProductSerializer


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = Product.objects.all()
   serializer_class = ProductSerializer
