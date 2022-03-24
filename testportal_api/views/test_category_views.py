from rest_framework import generics

from testportal.models import TestCategory

from testportal_api.serializers import TestCategorySerializer


class TestCategoryList(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializer


class TestCategoryDetail(generics.RetrieveDestroyAPIView):
   queryset = TestCategory.objects.all()
   serializer_class = TestCategorySerializer
