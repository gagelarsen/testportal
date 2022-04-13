from django.shortcuts import render

from testportal.models import Suite, TestPlan


def test_plan_list_view(request):
    context = {}

    test_plans = TestPlan.objects.all()
    suites = Suite.objects.all().values('name', 'id')

    context['test_plans'] = test_plans
    context['suites'] = suites

    return render(request, 'testportal/test_plan_list_view.html', context)