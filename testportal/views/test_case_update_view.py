from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, TestCase


TEST_CASE_FIELDS = [
    'name', 'test_case_id', 'notes', 'steps', 'suite',
    'tags', 'category', 'subcategory', 'test_plan',
    'status', 'test_type'
]


class TestCaseFormContextMixin:
    fields = TEST_CASE_FIELDS

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


class TestCaseUpdateView(LoginRequiredMixin, TestCaseFormContextMixin, UpdateView):
    model = TestCase


class TestCaseCreateView(LoginRequiredMixin, TestCaseFormContextMixin, CreateView):
    model = TestCase