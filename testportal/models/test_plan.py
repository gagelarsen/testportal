from django.db import models

from .suite import Suite


class TestPlan(models.Model):

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Test Plans'

    name = models.CharField(max_length=256)
    suite = models.ForeignKey(Suite, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    developers = models.TextField(blank=True, null=True)
    features_to_test = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.suite})'
