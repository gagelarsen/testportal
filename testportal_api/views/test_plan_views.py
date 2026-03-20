from rest_framework import generics

from testportal.models import TestPlan

from testportal_api.serializers import TestPlanSerializer


class TestPlanList(generics.ListCreateAPIView):
    queryset = TestPlan.objects.select_related('suite').all()
    serializer_class = TestPlanSerializer


class TestPlanDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestPlan.objects.select_related('suite').all()
    serializer_class = TestPlanSerializer