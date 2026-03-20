import json

from django.db import DatabaseError, IntegrityError, transaction
from django.http import JsonResponse
from django.core import serializers
from rest_framework import generics

from testportal.models import TestCategory, TestSubcategory, Suite, TestCase

from testportal_api.serializers import TestCaseSerializer


class TestCaseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer


def upload_multiple_test_cases(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is supported for this endpoint."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication is required to upload test cases."}, status=401)

    json_text = request.POST.get('json', None)
    if json_text is None:
        return JsonResponse({"error": "Missing required form field: json"}, status=400)

    try:
        json_data = json.loads(json_text)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Unable to decode json..."}, status=400)

    if not isinstance(json_data, dict):
        return JsonResponse({"error": "Invalid payload. Expected a JSON object."}, status=400)

    cases_payload = json_data.get('test_cases', None)
    if not isinstance(cases_payload, list):
        return JsonResponse({"error": "Invalid payload. Expected test_cases to be a list."}, status=400)

    if len(cases_payload) == 0:
        return JsonResponse({"error": "No test_cases were provided."}, status=400)

    required_fields = {'name', 'test_case_id', 'steps', 'status', 'suite', 'test_type', 'category', 'subcategory'}
    for index, case in enumerate(cases_payload):
        if not isinstance(case, dict):
            return JsonResponse({"error": f"Invalid test case at index {index}. Expected object."}, status=400)
        missing = sorted(required_fields - set(case.keys()))
        if missing:
            return JsonResponse({
                "error": f"Missing required fields at index {index}: {', '.join(missing)}"
            }, status=400)

    suite_names = {case['suite'] for case in cases_payload}
    category_names = {case['category'] for case in cases_payload}
    subcategory_names = {case['subcategory'] for case in cases_payload}

    suites_by_name = {suite.name: suite for suite in Suite.objects.filter(name__in=suite_names)}
    categories_by_name = {
        category.category: category
        for category in TestCategory.objects.filter(category__in=category_names)
    }
    subcategories_by_name = {
        subcategory.subcategory: subcategory
        for subcategory in TestSubcategory.objects.filter(subcategory__in=subcategory_names)
    }

    test_cases = []
    for index, case in enumerate(cases_payload):
        suite = suites_by_name.get(case['suite'])
        if suite is None:
            return JsonResponse({
                "error": f"Unknown suite at index {index}: {case['suite']}"
            }, status=400)

        category = categories_by_name.get(case['category'])
        if category is None:
            return JsonResponse({
                "error": f"Unknown category at index {index}: {case['category']}"
            }, status=400)

        subcategory = subcategories_by_name.get(case['subcategory'])
        if subcategory is None:
            return JsonResponse({
                "error": f"Unknown subcategory at index {index}: {case['subcategory']}"
            }, status=400)

        test_cases.append(
            TestCase(
                name=case['name'],
                test_case_id=case['test_case_id'],
                steps=case['steps'],
                status=case['status'],
                suite=suite,
                test_type=case['test_type'],
                category=category,
                subcategory=subcategory,
            )
        )

    try:
        with transaction.atomic():
            TestCase.objects.bulk_create(test_cases)
    except IntegrityError:
        return JsonResponse({
            "error": "Unable to upload test cases due to conflicting values (possibly duplicate suite + test_case_id)."
        }, status=409)
    except DatabaseError:
        return JsonResponse({"error": "Unable to save uploaded test cases."}, status=400)

    instances = serializers.serialize('json', test_cases)
    return JsonResponse({"instances": instances}, status=201)


def delete_test_case(request, pk):
    if request.method not in ["POST", "DELETE"]:
        return JsonResponse({"error": "Only POST and DELETE are supported for this endpoint."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication is required to delete a test case."}, status=401)

    try:
        test_case = TestCase.objects.get(id=pk)
    except TestCase.DoesNotExist:
        return JsonResponse({"error": "Unable to find test case to delete."}, status=404)

    try:
        test_case.delete()
    except DatabaseError:
        return JsonResponse({"error": "Unable to delete testcase... See system administrator."}, status=400)

    return JsonResponse({
        "message": 'Successfully deleted test case',
    }, status=200) 