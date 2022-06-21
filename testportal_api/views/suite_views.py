import json

from django.http import JsonResponse
from rest_framework import generics

from testportal.models import Suite, TestCase

from testportal_api.serializers import SuiteSerializer


class SuiteList(generics.ListCreateAPIView):
    queryset = Suite.objects.all()
    serializer_class = SuiteSerializer


class SuiteDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = Suite.objects.all()
   serializer_class = SuiteSerializer

   
def duplicate_suite(request, suite_id):
    # request should be ajax and method should be POST.
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        new_name = request.POST.get('new_name', None)
        if new_name is None:
            return JsonResponse({"error": "No name specified for duplciated suite."}, status=400)
        try:
            old_suite = Suite.objects.get(id=suite_id)
        except Exception as e:
            return JsonResponse({"error": "Specified suite not found...",
                                 "exception": e}, status=404)

        if Suite.objects.filter(name=new_name).exists():
            return JsonResponse({"error": "Suite with specified name already exists."}, status=400); 

        try:
            new_suite = Suite(
                name=new_name,
                active=old_suite.active,
                description=old_suite.description,
            )
            new_suite.save()
        except Exception as e:
            return JsonResponse({"error": "Unable to duplicate suite... See system administrator.",
                                 "exception": e}, status=400);
        try:
            test_cases = [
                TestCase(
                    name=case.name,
                    test_case_id=case.test_case_id,
                    steps=case.steps,
                    status=case.status,
                    suite=new_suite,
                    test_type=case.test_type,
                    category=case.category,
                    subcategory=case.subcategory,
                )
                for case in TestCase.objects.all().filter(suite=old_suite)
            ]
            TestCase.objects.bulk_create(test_cases)
            return JsonResponse({"message": "suite duplicated successfully!"}, status=201)

        except Exception as e:
            new_suite.delete()
            return JsonResponse({"error": "Unable to duplicate tests for new suite... aborting duplication. See system administrator.",
                                 "exception": e}, status=400)

    return JsonResponse({"error": "Unable to process respsone... See system administrator."}, status=400)