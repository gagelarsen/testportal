"""
Product Django Model

Notes:
  When adding fields you need to update the following locations:
      - testportal_api/serializers/product_serializers.py
      - testportal/views/product_update_view.py
"""
from django.db import models


class Product(models.Model):

    class Meta:
        ordering = ('name', 'version')
        unique_together = ('name', 'version')

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)

    objects = models.Manager()  # Default Manager

    def __str__(self):
        return f'{self.name}'
