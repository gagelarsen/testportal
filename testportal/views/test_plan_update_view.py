from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, TestPlan


class TestPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = TestPlan

    fields = [
        'name', 'suite', 'description', 'developers', 
        'features_to_test', 'notes',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestPlanUpdateView, self).get_context_data(**kwargs)
        context['suites'] = Suite.objects.all().filter(active=True)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'


class TestPlanCreateView(LoginRequiredMixin, CreateView):
    model = TestPlan

    fields = [
        'name', 'suite', 'description', 'developers', 
        'features_to_test', 'notes',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestPlanCreateView, self).get_context_data(**kwargs)
        context['suites'] = Suite.objects.all().filter(active=True)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'