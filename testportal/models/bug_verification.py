"""
Bug Verification Django Model

Notes:
  When adding fields you need to update the following locations:
      - testportal_api/serializers/bug_verification_serializers.py
      - testportal/views/bug_verification_update_view.py
"""
from datetime import datetime

from django.db import models
from model_utils import Choices

from testportal.models.product import Product
from testportal.models.test_subcategory import TestSubcategory


class BugVerification(models.Model):

    TEST = Choices(
        ('gui', 'GUI Test'),
        ('nongui', 'Non-GUI Test'),
        ('none', 'No Test'),
    )

    class Meta:
        ordering = ('verified_date', 'fixed_date', 'reported_date', 'bug_id')

    bug_id = models.IntegerField(unique=True)
    summary = models.CharField(max_length=512)
    products = models.ManyToManyField(Product, blank=True)
    reported_date = models.DateField(default=datetime.now)
    fixed_date = models.DateField(default=datetime.now)
    verified_date = models.DateField(default=datetime.now)
    category = models.ForeignKey(TestSubcategory, on_delete=models.PROTECT, related_name='bug_verifications')
    test = models.CharField(
        max_length=128, choices=TEST,
        default=TEST.nongui
    )

    objects = models.Manager()  # Default Manager

    def __str__(self):
        return f'{self.bug_id}'
