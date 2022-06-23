from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, TestResult


class TestResultUpdateView(LoginRequiredMixin, UpdateView):
    model = TestResult

    fields = [
        'result',
        'note',
        'user',
        'test_case',
        'result_date',
        'duration',
        'bug_id',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestResultUpdateView, self).get_context_data(**kwargs)
        context['suites'] = Suite.objects.all().filter(active=True)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'

class TestResultCreateView(LoginRequiredMixin, CreateView):
    model = TestResult

    fields = [
        'result',
        'note',
        'user',
        'test_case',
        'result_date',
        'duration',
        'bug_id',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestResultCreateView, self).get_context_data(**kwargs)
        context['suites'] = Suite.objects.all().filter(active=True)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'