from collections import Counter
from django.shortcuts import render

from testportal.models import Suite, TestPlan


def test_plan_detail_view(request, test_plan_id):
    context = {
        test_plan_id: test_plan_id,
    }

    test_plan = TestPlan.objects.get(id=test_plan_id)
    suites = Suite.objects.all().values('name', 'id')
    test_cases = [
        {'test_case': test_case, 'result': test_case.get_last_result()} 
        for test_case in
        test_plan.test_cases.all()
    ]

    context['test_plan'] = test_plan
    context['suites'] = suites
    context['test_cases'] = test_cases
    
    type_counts = Counter([x['test_case'].test_type for x in test_cases])
    status_counts = Counter([x['test_case'].status for x in test_cases])
    result_counts = Counter([x['result'].result if x['result'] != None else None for x in test_cases])
    category_counts = Counter([x['test_case'].category for x in test_cases])

    context.update({
        'status_counts_keys': status_counts.keys(),
        'result_counts_keys': result_counts.keys(),
        'category_counts_keys': category_counts.keys(),
        'status_counts_values': status_counts.values(),
        'result_counts_values': result_counts.values(),
        'category_counts_values': category_counts.values(),
    })
    return render(request, 'testportal/test_plan_detail_view.html', context)