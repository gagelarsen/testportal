import uuid

from django.db import models
from model_utils import Choices

from .suite import Suite
from .tag import Tag
from .test_category import TestCategory
from .test_plan import TestPlan
from .test_subcategory import TestSubcategory


STATUS = Choices(
    ('active', 'Test is active'),
    ('depricated', 'Test is depricated'),
    ('broken', 'Test is broken'),
    ('under_construction', 'Test is under construction'),
    ('design', 'Test is in design')
)

TEST_TYPE = Choices(
    ('manual', 'Manual Test'),
    ('automated', 'Automated Test'),
)


class TestCase(models.Model):
    
    class Meta:
        ordering = ('name', 'suite', 'test_type')
        verbose_name_plural = 'Test Cases'

    name = models.CharField(max_length=128)
    steps = models.TextField()
    suite = models.ForeignKey(Suite, on_delete=models.PROTECT, related_name='test_cases')
    tags = models.ManyToManyField(Tag)
    category = models.ForeignKey(TestCategory, on_delete=models.PROTECT, related_name='test_cases')
    subcategory = models.ForeignKey(TestSubcategory, on_delete=models.PROTECT)
    test_plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=128, choices=STATUS,
        default=STATUS.design
    )
    test_type = models.CharField(
        max_length=128, choices=TEST_TYPE,
        default=TEST_TYPE.automated
    )
