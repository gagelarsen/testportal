from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, TestPlan


TEST_PLAN_FIELDS = [
    'name', 'suite', 'description', 'developers',
    'features_to_test', 'notes',
]


class TestPlanFormContextMixin:
    fields = TEST_PLAN_FIELDS

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


class TestPlanUpdateView(LoginRequiredMixin, TestPlanFormContextMixin, UpdateView):
    model = TestPlan


class TestPlanCreateView(LoginRequiredMixin, TestPlanFormContextMixin, CreateView):
    model = TestPlan