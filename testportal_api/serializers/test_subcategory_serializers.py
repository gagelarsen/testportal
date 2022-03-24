from rest_framework import serializers
from testportal.models import TestSubcategory

class TestSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSubcategory
        fields = ('id', 'subccategory')
