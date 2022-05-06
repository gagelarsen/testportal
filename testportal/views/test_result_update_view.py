from django.views.generic.edit import UpdateView, CreateView

from testportal.models.test_result import TestResult


class TestResultUpdateView(UpdateView):
    model = TestResult

    fields = [
        'result',
        'note',
        'user',
        'test_case',
        'result_date',
        'duration',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestResultUpdateView, self).get_context_data(**kwargs)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'

class TestResultCreateView(CreateView):
    model = TestResult

    fields = [
        'result',
        'note',
        'user',
        'test_case',
        'result_date',
        'duration',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestResultCreateView, self).get_context_data(**kwargs)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'