from datetime import datetime, timedelta, date

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.template.defaultfilters import register

from testportal.models import Suite, TestResult, Tag, TestCategory, \
     TestSubcategory, TestPlan


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key,None)


@ register.filter
def format_result(value):
    return value.replace('-', ' ').title()


def dashboard_view(request, name):
    context = {
        'name': name,
        }

    User = get_user_model()

    suite = Suite.objects.get(name=name)
    test_cases = suite.test_cases.all().order_by('category', 'subcategory', 'name')
    users = User.objects.all().values('username', 'id')
    statuses = TestResult.STATUS

    number_of_days_get = request.GET.get('num_days', 10)
    try:
        number_of_days = int(number_of_days_get)
    except:
        number_of_days = 30

    today = date.today()
    date_list = [today - timedelta(days=i) 
                 for i in range(number_of_days)
                 if len(TestResult.objects.filter(result_date=today - timedelta(days=i), test_case__suite=suite)) > 0]

    # Dict of Lists "test-name": [d1, d2, d3, d4, d5]

    dashboard_data = [
        {
            'test_case': test_case,
            'test_results': test_case.results_for_dates(date_list)
        } for test_case in test_cases
    ]

    context.update({
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