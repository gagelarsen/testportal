from rest_framework import generics

from testportal_app.models import TestCase

from testportal_api.serializers import TestCaseSerializer


class TestCaseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer