from rest_framework import serializers
from testportal_app.models import Suite 


class SuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suite
        fields = ('id', 'name', 'active', 'test_cases')
        depth = 2