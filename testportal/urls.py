from django.urls import path
from django.views.generic import RedirectView

from testportal.views import dashboard_view, suite_detail_view, suite_list_view, \
    test_plan_list_view, test_plan_detail_view, test_case_detail_view

app_name = 'testportal'

urlpatterns = [
    path('', RedirectView.as_view(url='/suites/')),
    path('test-cases/<int:test_case_id>/', test_case_detail_view, name='test_case_detail_view'),
    path('test-plans/', test_plan_list_view, name='test_plan_list_view'),
    path('test-plans/<int:test_plan_id>/', test_plan_detail_view, name='test_plan_list_view'),
    path('suites/', suite_list_view, name='suite_list_view'),
    path('suites/<str:name>/', suite_detail_view, name='suite_detail_view'),
    path('suites/<str:name>/dashboard/', dashboard_view, name='dashboard_view'),
]