from django.shortcuts import render, get_object_or_404

from testportal.models import (
    Suite,
    Tag,
    TestCase,
    TestCategory,
    TestPlan,
    TestSubcategory,
)


def test_case_detail_view(request, test_case_id):
    context = {
        'test_case_id': test_case_id,
    }

    test_case = get_object_or_404(TestCase.objects.prefetch_related('tags'), id=test_case_id)
    selected_tags = test_case.tags.all()
    recent_results = test_case.results.select_related('user').order_by('-result_date')[:5]  # Most recent 5
    timing_results = list(
        test_case.results.select_related('user')
        .filter(duration__isnull=False)
        .exclude(duration=0)
        .order_by('-result_date')[:50]
    )
    timing_results = sorted(timing_results, key=lambda result: result.result_date)
    context['referrer'] = request.META.get('HTTP_REFERER', None)

    valid_times = [result.duration for result in timing_results if result.duration is not None]
    average_time = 0
    if len(valid_times) > 0:
        average_time = sum(valid_times) / len(valid_times)
    context['average_test_time'] = average_time

    context['test_case'] = test_case
    context['selected_tags'] = selected_tags
    context['tags'] = Tag.objects.all()
    context['categories'] = TestCategory.objects.all()
    context['subcategories'] = TestSubcategory.objects.all()
    context['test_plans'] = TestPlan.objects.filter(suite=test_case.suite)
    context['recent_results'] = recent_results
    context['timing_results'] = timing_results
    context['suites'] = Suite.objects.filter(active=True)

    return render(request, 'testportal/test_case_detail_view.html', context)