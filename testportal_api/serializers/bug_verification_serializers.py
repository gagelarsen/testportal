from rest_framework import serializers
from testportal.models import BugVerification 
from testportal.models import Product, TestSubcategory


class BugVerificationSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        required=False,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=TestSubcategory.objects.all(),
    )

    class Meta:
        model = BugVerification
        fields = ('id', 'bug_id', 'summary', 'products', 'reported_date',
                  'fixed_date', 'verified_date', 'category', 'test',)
