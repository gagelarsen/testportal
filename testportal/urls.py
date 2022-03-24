from django.urls import path
from django.views.generic import TemplateView

app_name = 'testportal'

urlpatterns = [
    path('', TemplateView.as_view(template_name='testportal/index.html')),
]