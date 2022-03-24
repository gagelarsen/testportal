from django.db import models


class TestType(models.Model):
    
    class Meta:
        ordering = ('test_type',)
        verbose_name_plural = 'Test Types'

    test_type = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.test_type}'
