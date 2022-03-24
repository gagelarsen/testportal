from rest_framework import serializers
from testportal.models import TestType  


class TestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestType
        fields = ('id', 'test_type')