from rest_framework import generics

from testportal.models import TestStatus

from testportal_api.serializers import TestStatusSerializer


class TestStatusList(generics.ListCreateAPIView):
    queryset = TestStatus.objects.all()
    serializer_class = TestStatusSerializer


class TestStatusDetail(generics.RetrieveDestroyAPIView):
   queryset = TestStatus.objects.all()
   serializer_class = TestStatusSerializer
