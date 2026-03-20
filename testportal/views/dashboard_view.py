from datetime import timedelta, date
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import register

from testportal.models import Suite, TestResult, Tag, TestCategory, \
     TestSubcategory, TestPlan


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)


@register.filter
def format_result(value):
    return value.replace('-', ' ').title()


def dashboard_view(request, name):
    context = {
        'name': name,
    }

    user_model = get_user_model()

    suites = Suite.objects.filter(active=True)
    suite = get_object_or_404(Suite, name=name)
    test_cases = list(
        suite.test_cases.select_related('category', 'subcategory')
        .order_by('category', 'subcategory', 'name')
    )
    users = user_model.objects.all().values('username', 'id')
    statuses = TestResult.STATUS

    number_of_days_get = request.GET.get('num_days', 10)
    try:
        number_of_days = int(number_of_days_get)
    except (TypeError, ValueError):
        number_of_days = 30

    number_of_days = max(1, min(number_of_days, 365))

    today = date.today()
    start_date = today - timedelta(days=number_of_days - 1)
    result_dates = set(
        TestResult.objects.filter(
            test_case__suite=suite,
            result_date__gte=start_date,
            result_date__lte=today,
        ).values_list('result_date', flat=True)
    )

    date_list = [
        today - timedelta(days=i)
        for i in range(number_of_days)
        if (today - timedelta(days=i)) in result_dates
    ]

    results_by_test_case = defaultdict(dict)
    if date_list:
        suite_results = TestResult.objects.filter(
            test_case__suite=suite,
            result_date__in=date_list,
        ).select_related('test_case', 'user')

        for result in suite_results:
            results_by_test_case[result.test_case_id][result.result_date] = result

    # Dict of Lists "test-name": [d1, d2, d3, d4, d5]

    dashboard_data = [
        {
            'test_case': test_case,
            'test_results': results_by_test_case.get(test_case.id, {})
        } for test_case in test_cases
    ]

    context.update({
        'suites': suites,
        'suite': suite,
        'test_cases': test_cases,
        'users': users,
        'statuses': statuses,
        'dashboard_data': dashboard_data,
        'date_list': date_list,
        'tags': Tag.objects.all(),
        'categories': TestCategory.objects.all(),
        'subcategories': TestSubcategory.objects.all(),
        'test_plans': TestPlan.objects.all(),
        'number_of_days': number_of_days,
    })

    return render(request, 'testportal/dashboard_view.html', context)