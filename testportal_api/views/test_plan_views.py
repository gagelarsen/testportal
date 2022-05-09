from rest_framework import generics
from django.template.defaultfilters import register, stringfilter

import markdown as md

from testportal.models import TestPlan

from testportal_api.serializers import TestPlanSerializer


@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])


class TestPlanList(generics.ListCreateAPIView):
    queryset = TestPlan.objects.all()
    serializer_class = TestPlanSerializer


class TestPlanDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = TestPlan.objects.all()
   serializer_class = TestPlanSerializer