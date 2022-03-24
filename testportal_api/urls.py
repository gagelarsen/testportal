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
]