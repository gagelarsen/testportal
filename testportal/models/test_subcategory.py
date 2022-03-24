from django.db import models


class TestSubcategory(models.Model):

    class Meta:
        ordering = ('subcategory',)
        verbose_name_plural = 'Test Subcategories'

    subcategory = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.subcategory}'
