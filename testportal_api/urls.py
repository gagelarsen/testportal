from django.urls import path
from .views import SuiteList, SuiteDetail, TagDetail, TagList, TestCaseDetail, \
    TestCategoryDetail, TestCategoryList, TestSubcategoryDetail, TestSubcategoryList, \
    TestPlanDetail, TestPlanList, TestResultDetail, TestResultList

app_name = 'testportal_api'

urlpatterns = [
    path('suites/<int:pk>/', SuiteDetail.as_view(), name='suite_detailcreate'),
    path('suites/', SuiteList.as_view(), name='suite_listcreate'),
    path('test_cases/<int:pk>/', TestCaseDetail.as_view(), name='testcase_detailcreate'),
    path('tags/<int:pk>/', TagDetail.as_view(), name='tag_detailcreate'),
    path('tags/', TagList.as_view(), name='tag_listcreate'),
    path('test_categories/<int:pk>/', TestCategoryDetail.as_view(), name='test_category_detailcreate'),
    path('test_categories/', TestCategoryList.as_view(), name='test_categories_listcreate'),
    path('test_subcategories/<int:pk>/', TestSubcategoryDetail.as_view(), name='test_subcategory_detailcreate'),
    path('test_subcategories/', TestSubcategoryList.as_view(), name='test_subcategories_listcreate'),
    path('test_plans/<int:pk>/', TestPlanDetail.as_view(), name='test_plans_detailcreate'),
    path('test_plans/', TestPlanList.as_view(), name='test_plans_listcreate'),
    path('test_results/<int:pk>/', TestResultDetail.as_view(), name='test_results_detailcreate'),
    path('test_results/', TestResultList.as_view(), name='test_results_listcreate'),
]