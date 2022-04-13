from rest_framework import generics

from testportal.models import Suite

from testportal_api.serializers import SuiteSerializer


class SuiteList(generics.ListCreateAPIView):
    queryset = Suite.objects.all()
    serializer_class = SuiteSerializer


class SuiteDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = Suite.objects.all()
   serializer_class = SuiteSerializer