from django.urls import path
from django.views.generic import TemplateView

app_name = 'testportal_app'

urlpatterns = [
    path('', TemplateView.as_view(template_name='testportal_app/index.html')),
]