from rest_framework import serializers
from testportal_app.models import TestStatus


class TestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestStatus
        fields = ('id', 'status')