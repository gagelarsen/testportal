from rest_framework import serializers
from testportal_app.models import TestType  


class TestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestType
        fields = ('id', 'test_type')