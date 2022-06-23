from rest_framework import serializers
from testportal.models import Product 


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'version')