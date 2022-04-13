import json

from django.http import JsonResponse
from django.core import serializers
from rest_framework import generics

from testportal.models import TestCategory, TestSubcategory, Suite, TestCase

from testportal_api.serializers import TestCaseSerializer


class TestCaseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer

def upload_multiple_test_cases(request):
    # request should be ajax and method should be POST.
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        # get data
        json_text = request.POST.get('json', '{}')

        try:
            json_data = json.loads(json_text)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Unable to decode json..."}, status=400)
        try:
            test_cases = [
                TestCase(
                    name=case['name'],
                    test_case_id=case['test_case_id'],
                    steps=case['steps'],
                    status=case['status'],
                    suite=Suite.objects.get(name=case['suite']),
                    test_type=case['test_type'],
                    category=TestCategory.objects.get(category=case['category']),
                    subcategory=TestSubcategory.objects.get(subcategory=case['subcategory']),
                )
                for case in json_data['test_cases']
            ]
            TestCase.objects.bulk_create(test_cases)
        except Exception as e:
            print(type(e))
            return JsonResponse({"error": str(e)}, status=400)

        instances = serializers.serialize('json', test_cases)
        return JsonResponse({"instances": instances}, status=201) 
    # some error occured
    return JsonResponse({"error": "Unable to process respsone... See system administrator."}, status=400)