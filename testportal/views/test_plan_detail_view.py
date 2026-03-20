from collections import Counter
from django.shortcuts import render, get_object_or_404

from testportal.models import Suite, TestPlan, TestResult


def test_plan_detail_view(request, test_plan_id):
    context = {
        'test_plan_id': test_plan_id,
    }

    test_plan = get_object_or_404(TestPlan, id=test_plan_id)
    suites = Suite.objects.values('name', 'id')

    plan_test_cases = list(
        test_plan.test_cases.select_related('category', 'subcategory').all()
    )
    test_case_ids = [test_case.id for test_case in plan_test_cases]

    results_by_test_case = {test_case_id: [] for test_case_id in test_case_ids}
    latest_result_by_test_case = {}

    if test_case_ids:
        plan_results = TestResult.objects.filter(test_case_id__in=test_case_ids).select_related('user').order_by(
            'test_case_id', '-result_date'
        )
        for result in plan_results:
            case_results = results_by_test_case[result.test_case_id]
            if len(case_results) < 5:
                case_results.append(result)
            if result.test_case_id not in latest_result_by_test_case:
                latest_result_by_test_case[result.test_case_id] = result

    test_cases = []
    for test_case in plan_test_cases:
        recent_results = results_by_test_case.get(test_case.id, [])
        valid_times = [r.duration for r in recent_results if r.duration is not None and r.result == 'pass']
        average_time = 0
        if len(valid_times) > 0:
            average_time = sum(valid_times) / len(valid_times)
        test_cases.append(
            {
                'test_case': test_case, 
                'result': latest_result_by_test_case.get(test_case.id),
                'duration': average_time
            }
        )

    context['test_plan'] = test_plan
    context['suites'] = suites
    context['test_cases'] = test_cases
    
    type_counts = Counter([x['test_case'].test_type for x in test_cases])
    status_counts = Counter([x['test_case'].status for x in test_cases])
    result_counts = Counter([x['result'].result if x['result'] is not None else None for x in test_cases])
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