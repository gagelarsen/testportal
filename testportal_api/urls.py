from django.urls import path
from .views import SuiteList, SuiteDetail, TagDetail, TagList, TestCaseDetail, \
    TestStatusDetail, TestStatusList, TestTypeDetail, TestTypeList

app_name = 'testportal_api'

urlpatterns = [
    path('suites/<int:pk>/', SuiteDetail.as_view(), name='suite_detailcreate'),
    path('suites/', SuiteList.as_view(), name='suite_listcreate'),
    path('testcases/<int:pk>/', TestCaseDetail.as_view(), name='testcase_detailcreate'),
    path('tags/<int:pk>/', TagDetail.as_view(), name='tag_detailcreate'),
    path('tags/', TagList.as_view(), name='tag_listcreate'),
    path('test_statuses/<int:pk>/', TestStatusDetail.as_view(), name='teststatus_detailcreate'),
    path('test_statuses/', TestStatusList.as_view(), name='teststatus_listcreate'),
    path('test_types/<int:pk>/', TestTypeDetail.as_view(), name='testtype_detailcreate'),
    path('test_types/', TestTypeList.as_view(), name='testtype_listcreate'),
]