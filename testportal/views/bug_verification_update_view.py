from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, BugVerification


class BugVerificationUpdateView(LoginRequiredMixin, UpdateView):
    model = BugVerification

    fields = [
        'bug_id', 'summary', 'products', 'reported_date', 'fixed_date',
        'verified_date', 'category', 'test',
    ]

    def get_context_data(self, **kwargs):
        context = super(BugVerificationUpdateView, self).get_context_data(**kwargs)
        context['suites'] = Suite.objects.all().filter(active=True)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'


class BugVerificationCreateView(LoginRequiredMixin, CreateView):
    model = BugVerification

    fields = [
        'bug_id', 'summary', 'products', 'reported_date', 'fixed_date',
        'verified_date', 'category', 'test',
    ]

    def get_context_data(self, **kwargs):
        context = super(BugVerificationCreateView, self).get_context_data(**kwargs)
        context['suites'] = Suite.objects.all().filter(active=True)
        context['referrer'] = self.request.META.get('HTTP_REFERER') # pass `next` parameter received from previous page to the context 
        return context

    def get_success_url(self):
        referrer = self.request.POST['referrer']
        if str(referrer) not in ['', 'None']:
            return referrer
        return '/'