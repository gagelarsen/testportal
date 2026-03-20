from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, BugVerification


BUG_VERIFICATION_FIELDS = [
    'bug_id', 'summary', 'products', 'reported_date', 'fixed_date',
    'verified_date', 'category', 'test',
]


class BugVerificationFormContextMixin:
    fields = BUG_VERIFICATION_FIELDS

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


class BugVerificationUpdateView(LoginRequiredMixin, BugVerificationFormContextMixin, UpdateView):
    model = BugVerification


class BugVerificationCreateView(LoginRequiredMixin, BugVerificationFormContextMixin, CreateView):
    model = BugVerification