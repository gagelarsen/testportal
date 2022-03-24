from rest_framework import generics

from testportal.models import TestSubcategory

from testportal_api.serializers import TestSubcategorySerializer


class TestSubcategoryList(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestSubcategory.objects.all()
    serializer_class = TestSubcategorySerializer


class TestSubcategoryDetail(generics.RetrieveDestroyAPIView):
   queryset = TestSubcategory.objects.all()
   serializer_class = TestSubcategorySerializer
