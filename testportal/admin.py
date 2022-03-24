from django.contrib import admin
from . import models


@admin.register(models.Suite)
class SuiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'active')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'id')


@admin.register(models.TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'status', 'suite', 'test_type')


@admin.register(models.TestStatus)
class TestStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'id')


@admin.register(models.TestType)
class TestTypeAdmin(admin.ModelAdmin):
    list_display = ('test_type', 'id')
