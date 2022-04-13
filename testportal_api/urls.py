from django.urls import path
from .views import SuiteList, SuiteDetail, TagDetail, TagList, TestCaseDetail, \
    upload_multiple_test_cases, TestCategoryDetail, TestCategoryList, TestSubcategoryDetail, \
    TestSubcategoryList, TestPlanDetail, TestPlanList, TestResultDetail, TestResultList, \
    upload_test_results

app_name = 'testportal_api'

urlpatterns = [
    path('suites/<int:pk>/', SuiteDetail.as_view(), name='suite_detailcreate'),
    path('suites/', SuiteList.as_view(), name='suite_listcreate'),
    path('test-cases/<int:pk>/', TestCaseDetail.as_view(), name='testcase_detailcreate'),
    path('tags/<int:pk>/', TagDetail.as_view(), name='tag_detailcreate'),
    path('tags/', TagList.as_view(), name='tag_listcreate'),
    path('test-categories/<int:pk>/', TestCategoryDetail.as_view(), name='test_category_detailcreate'),
    path('test-categories/', TestCategoryList.as_view(), name='test_categories_listcreate'),
    path('test-subcategories/<int:pk>/', TestSubcategoryDetail.as_view(), name='test_subcategory_detailcreate'),
    path('test-subcategories/', TestSubcategoryList.as_view(), name='test_subcategories_listcreate'),
    path('test-plans/<int:pk>/', TestPlanDetail.as_view(), name='test_plans_detailcreate'),
    path('test-plans/', TestPlanList.as_view(), name='test_plans_listcreate'),
    path('test-results/<int:pk>/', TestResultDetail.as_view(), name='test_results_detailcreate'),
    path('test-results/', TestResultList.as_view(), name='test_results_listcreate'),
    path('upload/test-cases/', upload_multiple_test_cases, name='testcase_upload'),
    path('upload/test-results/<int:pk>', upload_test_results, name='testresult_upload'),
]