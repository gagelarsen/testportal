from rest_framework import serializers
from testportal.models import TestCategory

class TestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCategory
        fields = ('id', 'category')
