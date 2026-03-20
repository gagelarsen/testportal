from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, TestResult


TEST_RESULT_FIELDS = [
    'result',
    'note',
    'user',
    'test_case',
    'result_date',
    'duration',
    'bug_id',
]


class TestResultFormContextMixin:
    fields = TEST_RESULT_FIELDS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suites'] = Suite.objects.filter(active=True)
        context['referrer'] = self.request.META.get('HTTP_REFERER')
        return context

    def get_success_url(self):
        referrer = self.request.POST.get('referrer')
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'


class TestResultUpdateView(LoginRequiredMixin, TestResultFormContextMixin, UpdateView):
    model = TestResult


class TestResultCreateView(LoginRequiredMixin, TestResultFormContextMixin, CreateView):
    model = TestResult