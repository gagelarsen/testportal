from datetime import date, timedelta

from django.db.models import Case, CharField, DateField, IntegerField, OuterRef, Q, Subquery, Value, When
from django.shortcuts import get_object_or_404, render

from testportal.models import Suite, TestCase, TestResult


def suite_report_view(request, name):
    suite = get_object_or_404(Suite, name=name)

    number_of_days_get = request.GET.get('num_days', 30)
    try:
        number_of_days = int(number_of_days_get)
    except (TypeError, ValueError):
        number_of_days = 30
    number_of_days = max(1, min(number_of_days, 365))

    today = date.today()
    start_day = today - timedelta(days=number_of_days - 1)

    suite_cases = suite.test_cases.all()
    total_cases = suite_cases.count()

    results_in_period = TestResult.objects.filter(
        test_case__suite=suite,
        result_date__gte=start_day,
        result_date__lte=today,
    )

    total_runs = results_in_period.count()
    tested_cases = results_in_period.values('test_case_id').distinct().count()
    untested_cases = max(total_cases - tested_cases, 0)

    status_choices = TestCase._meta.get_field('status').choices
    type_choices = TestCase._meta.get_field('test_type').choices
    result_choices = TestResult._meta.get_field('result').choices

    status_counts = {
        choice[0]: suite_cases.filter(status=choice[0]).count()
        for choice in status_choices
    }
    type_counts = {
        choice[0]: suite_cases.filter(test_type=choice[0]).count()
        for choice in type_choices
    }
    result_counts = {
        choice[0]: results_in_period.filter(result=choice[0]).count()
        for choice in result_choices
    }

    bug_linked_runs = results_in_period.exclude(bug_id__isnull=True).exclude(bug_id='').count()

    pass_count = result_counts.get('pass', 0)
    fail_count = result_counts.get('fail', 0)
    issue_count = result_counts.get('issue', 0)
    false_negative_count = result_counts.get('false-negative', 0)
    skipped_count = result_counts.get('skipped', 0)
    under_construction_result_count = result_counts.get('under-construction', 0)
    in_documentation_result_count = result_counts.get('in-documentation', 0)

    active_status_count = status_counts.get('active', 0)
    needs_review_status_count = status_counts.get('needs-review', 0)
    under_construction_status_count = status_counts.get('under-construction', 0)
    broken_status_count = status_counts.get('broken', 0)

    automated_type_count = type_counts.get('automated', 0)
    manual_type_count = type_counts.get('manual', 0)

    pass_rate = round((pass_count / total_runs) * 100, 1) if total_runs else 0
    action_rate = round(((issue_count + false_negative_count) / total_runs) * 100, 1) if total_runs else 0

    latest_results_for_case = TestResult.objects.filter(
        test_case=OuterRef('pk'),
        result_date__gte=start_day,
        result_date__lte=today,
    ).order_by('-result_date', '-id')

    attention_cases = list(
        suite_cases.annotate(
            latest_result=Subquery(
                latest_results_for_case.values('result')[:1],
                output_field=CharField(),
            ),
            latest_bug_id=Subquery(
                latest_results_for_case.values('bug_id')[:1],
                output_field=CharField(),
            ),
            latest_result_date=Subquery(
                latest_results_for_case.values('result_date')[:1],
                output_field=DateField(),
            ),
        )
        .annotate(
            issue_latest=Case(When(latest_result='issue', then=Value(1)), default=Value(0), output_field=IntegerField()),
            false_negative_latest=Case(
                When(latest_result='false-negative', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
            fail_latest=Case(When(latest_result='fail', then=Value(1)), default=Value(0), output_field=IntegerField()),
            bug_latest=Case(
                When(Q(latest_bug_id__isnull=False) & ~Q(latest_bug_id=''), then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        .filter(
            Q(issue_latest=1)
            | Q(false_negative_latest=1)
            | Q(fail_latest=1)
            | Q(bug_latest=1)
        )
        .order_by('-issue_latest', '-false_negative_latest', '-bug_latest', '-fail_latest', 'name')[:15]
    )

    context = {
        'suites': Suite.objects.filter(active=True),
        'suite': suite,
        'number_of_days': number_of_days,
        'start_day': start_day,
        'end_day': today,
        'total_cases': total_cases,
        'tested_cases': tested_cases,
        'untested_cases': untested_cases,
        'total_runs': total_runs,
        'bug_linked_runs': bug_linked_runs,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'issue_count': issue_count,
        'false_negative_count': false_negative_count,
        'skipped_count': skipped_count,
        'under_construction_result_count': under_construction_result_count,
        'in_documentation_result_count': in_documentation_result_count,
        'pass_rate': pass_rate,
        'action_rate': action_rate,
        'status_counts': status_counts,
        'type_counts': type_counts,
        'result_counts': result_counts,
        'active_status_count': active_status_count,
        'needs_review_status_count': needs_review_status_count,
        'under_construction_status_count': under_construction_status_count,
        'broken_status_count': broken_status_count,
        'automated_type_count': automated_type_count,
        'manual_type_count': manual_type_count,
        'attention_cases': attention_cases,
    }

    return render(request, 'testportal/suite_report_view.html', context)
