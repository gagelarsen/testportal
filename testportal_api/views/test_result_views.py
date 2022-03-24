from rest_framework import generics

from testportal.models import TestResult

from testportal_api.serializers import TestResultSerializer


class TestResultList(generics.ListCreateAPIView):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer


class TestResultDetail(generics.RetrieveDestroyAPIView):
   queryset = TestResult.objects.all()
   serializer_class = TestResultSerializer