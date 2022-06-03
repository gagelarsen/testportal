from django.shortcuts import render

from testportal.models import TestCase


def test_case_detail_view(request, test_case_id):
    context = {
        test_case_id: test_case_id,
    }

    test_case = TestCase.objects.get(id=test_case_id)
    tags = test_case.tags.all()
    recent_results = test_case.results.all().order_by('-result_date')[:5]  # Most recent 5
    context['referrer'] = request.META.get('HTTP_REFERER', None) # pass `next` parameter received from previous page to the context 

    context['test_case'] = test_case
    context['tags'] = tags
    context['recent_results'] = recent_results

    return render(request, 'testportal/test_case_detail_view.html', context)