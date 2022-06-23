from django.urls import path
from django.views.generic import RedirectView

from testportal.views import dashboard_view, suite_detail_view, suite_list_view, \
    test_plan_list_view, test_plan_detail_view, test_case_detail_view
from testportal.views.test_result_update_view import TestResultUpdateView, TestResultCreateView
from testportal.views.test_case_update_view import TestCaseUpdateView, TestCaseCreateView
from testportal.views.test_plan_update_view import TestPlanUpdateView, TestPlanCreateView
from testportal.views.bug_verifications import bug_verifications_general_view
from testportal.views.bug_verification_update_view import BugVerificationCreateView, BugVerificationUpdateView
from testportal.views.product_update_view import ProductCreateView, ProductUpdateView

app_name = 'testportal'

urlpatterns = [
    path('test-cases/create', TestCaseCreateView.as_view(), name='test_case_create_view'),
    path('test-cases/<int:test_case_id>/', test_case_detail_view, name='test_case_detail_view'),
    path('test-cases/<int:pk>/update', TestCaseUpdateView.as_view(), name='test_case_update_view'),
    path('test-plans/', test_plan_list_view, name='test_plan_list_view'),
    path('test-plans/<int:test_plan_id>/', test_plan_detail_view, name='test_plan_list_view'),
    path('test-plans/<int:pk>/update', TestPlanUpdateView.as_view(), name='test_plan_update'),
    path('test-plans/create', TestPlanCreateView.as_view(), name='test_plan_create'),
    path('test-results/<int:pk>', TestResultUpdateView.as_view(), name='test_result_update'),
    path('test-results/create', TestResultCreateView.as_view(), name='test_result_create'),
    path('suites/', suite_list_view, name='suite_list_view'),
    path('suites/<str:name>/', suite_detail_view, name='suite_detail_view'),
    path('suites/<str:name>/dashboard/', dashboard_view, name='dashboard_view'),
    path('bug-verifications', bug_verifications_general_view, name='bug_verifications_general_view'),
    path('', RedirectView.as_view(url='/suites/')),
    path('bug-verifications/<int:pk>/update', BugVerificationUpdateView.as_view(), name='bug_verification_update'),
    path('bug-verifications/create', BugVerificationCreateView.as_view(), name='bug_verification_create'),
    path('products/<int:pk>/update', ProductUpdateView.as_view(), name='product_update'),
    path('products/create', ProductCreateView.as_view(), name='product_create'),
]