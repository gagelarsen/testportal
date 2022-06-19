from rest_framework import serializers
from testportal.models import TestCase  

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ('id', 'name', 'test_case_id', 'notes', 'steps', 'status','suite', 
                  'test_type', 'tags', 'category', 'subcategory', 'needs_review',
                  'under_construction')
