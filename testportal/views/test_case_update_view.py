from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models.test_result import TestCase


class TestCaseUpdateView(LoginRequiredMixin, UpdateView):
    model = TestCase

    fields = [
        'name', 'test_case_id', 'steps', 'suite',
        'tags', 'category', 'subcategory', 'test_plan',
        'status', 'test_type',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestCaseUpdateView, self).get_context_data(**kwargs)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'


class TestCaseCreateView(CreateView):
    model = TestCase

    fields = [
        'name', 'test_case_id', 'steps', 'suite',
        'tags', 'category', 'subcategory', 'test_plan',
        'status', 'test_type',
    ]

    def get_context_data(self, **kwargs):
        context = super(TestCaseCreateView, self).get_context_data(**kwargs)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'