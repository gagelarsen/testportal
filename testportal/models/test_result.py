from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from model_utils import Choices

from .test_case import TestCase


class TestResult(models.Model):

    STATUS = Choices(
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('false-negative', 'False Negative'),
        ('issue', 'Issue'),
        ('skipped', 'Skipped'),
        ('under-construction', 'Under Construction'),
        ('in-documentation', 'In Documentation'),
    )
    
    class Meta:
        ordering = ('result_date',)
        verbose_name_plural = 'Test Results'
        unique_together = ('result_date', 'test_case')

    result = models.CharField(
        max_length=128, choices=STATUS,
        default=STATUS.skipped
    )
    note = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='results')
    result_date = models.DateField(default=datetime.now)
    duration = models.FloatField(null=True, blank=True)
    bug_id = models.CharField(max_length=32, null=True, blank=True)
