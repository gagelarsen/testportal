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
    list_filter = ('status', 'suite', 'test_type')


@admin.register(models.TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category',)


@admin.register(models.TestSubcategory)
class TestSubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'subcategory',)


@admin.register(models.TestPlan)
class TestPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','suite')
    list_filter = ('suite',)


@admin.register(models.TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'result', 'result_date', 'test_case')
