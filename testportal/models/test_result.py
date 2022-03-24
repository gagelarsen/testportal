from django.db import models
from model_utils import Choices

from .test_case import TestCase


class TestResult(models.Model):

    STATUS = Choices(
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('false_negative', 'False Negative'),
        ('issue', 'Issue'),
        ('skipped', 'Skipped'),
    )
    
    class Meta:
        ordering = ('result_date',)
        verbose_name_plural = 'Test Results'

    result = models.CharField(
        max_length=128, choices=STATUS,
        default=STATUS.skipped
    )
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    result_date = models.DateField(auto_now_add=True)