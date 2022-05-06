from datetime import datetime, timedelta
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
    ('under-construction', 'Test is under construction'),
    ('design', 'Test is in design'),
)

TEST_TYPE = Choices(
    ('manual', 'Manual Test'),
    ('automated', 'Automated Test'),
)


class TestCase(models.Model):
    
    class Meta:
        ordering = ('test_case_id', 'name', 'suite', 'test_type')
        verbose_name_plural = 'Test Cases'
        unique_together = ('suite', 'test_case_id')

    name = models.CharField(max_length=128)
    test_case_id = models.CharField(max_length=64, blank=True, null=True)
    steps = models.TextField()
    suite = models.ForeignKey(Suite, on_delete=models.PROTECT, related_name='test_cases')
    tags = models.ManyToManyField(Tag, blank=True)
    category = models.ForeignKey(TestCategory, on_delete=models.PROTECT, related_name='test_cases')
    subcategory = models.ForeignKey(TestSubcategory, on_delete=models.PROTECT)
    test_plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, null=True, blank=True, related_name='test_cases')
    status = models.CharField(
        max_length=128, choices=STATUS,
        default=STATUS.design
    )
    test_type = models.CharField(
        max_length=128, choices=TEST_TYPE,
        default=TEST_TYPE.automated
    )

    def results_for_n_days(self, n):
        today = datetime.today()
        date_list = [today - timedelta(days=i) for i in range(n)]
        results = {d.result_date: d for d in self.results.all().filter(
            result_date__lte=today, result_date__gte=date_list[-1]
        )}
        return results

    def results_for_dates(self, date_list):
        results = {d.result_date: d for d in self.results.all().filter(
            result_date__in=date_list,
        )}
        return results

    def __str__(self):
        return f'{self.name} - ({self.suite})'
