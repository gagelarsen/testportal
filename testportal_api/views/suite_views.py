from django.db import DatabaseError, IntegrityError, transaction
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
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is supported for this endpoint."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication is required to duplicate a suite."}, status=401)

    new_name = request.POST.get('new_name', '')
    new_name = new_name.strip()
    if not new_name:
        return JsonResponse({"error": "No name specified for duplicated suite."}, status=400)

    try:
        old_suite = Suite.objects.get(id=suite_id)
    except Suite.DoesNotExist:
        return JsonResponse({"error": "Specified suite not found..."}, status=404)

    if Suite.objects.filter(name=new_name).exists():
        return JsonResponse({"error": "Suite with specified name already exists."}, status=400)

    try:
        with transaction.atomic():
            new_suite = Suite.objects.create(
                name=new_name,
                active=old_suite.active,
                description=old_suite.description,
                product=old_suite.product,
            )

            test_cases = [
                TestCase(
                    name=case.name,
                    test_case_id=case.test_case_id,
                    notes=case.notes,
                    steps=case.steps,
                    suite=new_suite,
                    category=case.category,
                    subcategory=case.subcategory,
                    test_plan=None,
                    status=case.status,
                    test_type=case.test_type,
                )
                for case in TestCase.objects.filter(suite=old_suite)
            ]
            TestCase.objects.bulk_create(test_cases)
    except IntegrityError:
        return JsonResponse({
            "error": "Unable to duplicate suite due to conflicting values."
        }, status=409)
    except DatabaseError:
        return JsonResponse({
            "error": "Unable to duplicate suite... See system administrator."
        }, status=400)

    return JsonResponse({"message": "Suite duplicated successfully!"}, status=201)