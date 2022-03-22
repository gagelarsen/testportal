from django.db import models


class TestStatus(models.Model):
    
    class Meta:
        ordering = ('status',)
        verbose_name_plural = 'Test Statuses'

    status = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.status}'