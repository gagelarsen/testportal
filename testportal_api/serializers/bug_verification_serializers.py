from rest_framework import serializers
from testportal.models import BugVerification 


class BugVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugVerification
        fields = ('id', 'bug_id', 'summary', 'products', 'reported_date',
                  'fixed_date', 'verified_date', 'category', 'test',)
        depth = 2
