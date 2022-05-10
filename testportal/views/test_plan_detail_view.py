from django.shortcuts import render

from testportal.models import Suite, TestPlan


def test_plan_detail_view(request, test_plan_id):
    context = {
        test_plan_id: test_plan_id,
    }

    test_plan = TestPlan.objects.get(id=test_plan_id)
    suites = Suite.objects.all().values('name', 'id')
    test_cases = test_plan.test_cases.all()

    context['test_plan'] = test_plan
    context['suites'] = suites
    context['test_cases'] = test_cases

    return render(request, 'testportal/test_plan_detail_view.html', context)