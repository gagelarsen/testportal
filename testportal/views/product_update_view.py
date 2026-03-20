from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from testportal.models import Suite, Product


PRODUCT_FIELDS = [
    'name', 'version',
]


class ProductFormContextMixin:
    fields = PRODUCT_FIELDS

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


class ProductUpdateView(LoginRequiredMixin, ProductFormContextMixin, UpdateView):
    model = Product


class ProductCreateView(LoginRequiredMixin, ProductFormContextMixin, CreateView):
    model = Product