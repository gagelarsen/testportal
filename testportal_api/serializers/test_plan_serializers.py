from rest_framework import serializers
from testportal.models import TestPlan

class TestPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPlan
        fields = ('id', 'name', 'suite', 'description', 'developers', 
                  'features_to_test', 'notes')
