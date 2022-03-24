from django.db import models


class TestCategory(models.Model):

    class Meta:
        ordering = ('category',)
        verbose_name_plural = 'Test Categories'

    category = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.category}'
