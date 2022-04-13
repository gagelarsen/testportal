from rest_framework import serializers
from testportal.models import TestResult

class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ('id', 'result', 'test_case', 'result_date', 'user', 'note', 'duration')
