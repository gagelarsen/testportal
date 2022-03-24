import uuid

from django.db import models

from .suite import Suite
from .test_status import TestStatus
from .test_type import TestType
from .tag import Tag


class TestCase(models.Model):
    
    class Meta:
        ordering = ('name', 'suite', 'test_type')
        verbose_name_plural = 'Test Cases'

    name = models.CharField(max_length=128)
    steps = models.TextField()
    status = models.ForeignKey(TestStatus, on_delete=models.PROTECT)
    suite = models.ForeignKey(Suite, on_delete=models.PROTECT, related_name='test_cases')
    test_type = models.ForeignKey(TestType, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag)
