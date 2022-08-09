from django.shortcuts import render

from testportal.models import Suite, TestCase


def test_case_detail_view(request, test_case_id):
    context = {
        test_case_id: test_case_id,
    }

    test_case = TestCase.objects.get(id=test_case_id)
    tags = test_case.tags.all()
    recent_results = test_case.results.all().order_by('-result_date')[:5]  # Most recent 5
    context['referrer'] = request.META.get('HTTP_REFERER', None) # pass `next` parameter received from previous page to the context 

    valid_times = [r.duration for r in recent_results if r.duration != None and r.result == 'pass']
    average_time = 0
    if len(valid_times) > 0:
        average_time = sum(valid_times) / len(valid_times)
    context['average_test_time'] = average_time

    context['test_case'] = test_case
    context['tags'] = tags
    context['recent_results'] = recent_results
    context['suites'] = Suite.objects.all().filter(active=True)

    return render(request, 'testportal/test_case_detail_view.html', context)