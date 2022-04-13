from django.db import models
from django.utils import timezone


class Suite(models.Model):

    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    objects = models.Manager()  # Default Manager

    def __str__(self):
        return f'{self.name}'
