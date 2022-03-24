from django.db import models


class Tag(models.Model):
    
    class Meta:
        ordering = ('tag',)
        verbose_name_plural = 'Tags'

    tag = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.tag}'
