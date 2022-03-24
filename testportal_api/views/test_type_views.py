from rest_framework import generics

from testportal.models import TestType

from testportal_api.serializers import TestTypeSerializer


class TestTypeList(generics.ListCreateAPIView):
    queryset = TestType.objects.all()
    serializer_class = TestTypeSerializer


class TestTypeDetail(generics.RetrieveDestroyAPIView):
   queryset = TestType.objects.all()
   serializer_class = TestTypeSerializer
