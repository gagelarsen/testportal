from django.db import models
from django.utils import timezone


from testportal.models import Product


class Suite(models.Model):

    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)

    objects = models.Manager()  # Default Manager

    def __str__(self):
        return f'{self.name}'
