from django.db import models
from django.utils import timezone


class Suite(models.Model):

    class SuiteObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(active=True)

    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()  # Default Manager
    suiteobjects = SuiteObjects()  # Custome Manager

    def __str__(self):
        return f'{self.name}'