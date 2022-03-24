from rest_framework import generics

from testportal.models import TestPlan

from testportal_api.serializers import TestPlanSerializer


class TestPlanList(generics.ListCreateAPIView):
    queryset = TestPlan.objects.all()
    serializer_class = TestPlanSerializer


class TestPlanDetail(generics.RetrieveDestroyAPIView):
   queryset = TestPlan.objects.all()
   serializer_class = TestPlanSerializer