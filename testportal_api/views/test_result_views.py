from datetime import datetime
import xml.etree.ElementTree as ET

from django.http import JsonResponse
from django.core import serializers

from rest_framework import generics

from testportal.models import TestResult, TestCase, Suite
from testportal_api.serializers import TestResultSerializer


class TestResultList(generics.ListCreateAPIView):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer


class TestResultDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = TestResult.objects.all()
   serializer_class = TestResultSerializer


def upload_test_results(request, pk):
    # request should be ajax and method should be POST.
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        # get data
        form_files = request.FILES
        result_date = request.POST.get('upload-results-date', None)
        
        if len(form_files) == 0:
            return JsonResponse({"error": "File was not uploaded correctly... See system administrator."}, status=400)
        if len(form_files) > 1:
            return JsonResponse({"error": "Cannot process multiple files. Please select only one to upload."}, status=400)

        file_to_upload = None
        for _, v in form_files.items():
            file_to_upload = v

        results = {
            '0': 'pass',
            '1': 'pass',
            '2': 'fail',
        }

        test_info = _parse_result_file(file_to_upload)

        suite = Suite.objects.get(id=pk)
        suite_cases = {x.name: x for x in TestCase.objects.filter(suite=suite)}
        missing_cases = []
        test_results = {}

        for result in test_info['test_cases']:
            name = result['name']
            test_case = suite_cases.get(name, None)
            if test_case is None:
                missing_cases.append(f'{name}')
                continue
            test_results[name] = TestResult(
                user=request.user,
                test_case=test_case,
                result_date=result_date,
                duration=result['duration_seconds'],
                result=results.get(result['status'], 'fail')
            )

        missing_results = list(set(suite_cases.keys()) - set(test_results.keys()))

        for case in missing_results:
            test_results[case] = TestResult(
                user=request.user,
                test_case=suite_cases[case],
                result_date=result_date,
                duration=0,
                result='skipped'
            )

        TestResult.objects.bulk_create(test_results.values())

        return JsonResponse({
            "message": 'Successfully uploaded results',
            "missing_results": missing_results,
            "missing_cases": missing_cases
        }, status=201) 

    # some error occured
    return JsonResponse({"error": "Unable to process respsone... See system administrator."}, status=400)


def _parse_test_case_info(node):
    all_test_info = []
    for child in node:
        test_info = {}
        for prp in child:
            if prp.tag != 'Prp':
                continue
            if prp.attrib['name'] in ['status', 'duration', 'name']:
                prp_name = prp.attrib['name']
                prp_value = prp.attrib['value']
                if prp_name == 'duration':
                    prp_name = 'duration_seconds'
                    prp_value = float(prp_value) / 1000
                test_info[prp_name] = prp_value
        all_test_info.append(test_info)
    return all_test_info

def _parse_result_file(summary_file):
    tree = ET.parse(summary_file)
    root = tree.getroot()

    project_node = root[0][0][0]

    test_info = {}

    for child in project_node:
        # Parse Test Data
        if child.tag == 'Node' and child.attrib.get('name', 'none') == 'tests':
            test_info['test_cases'] = _parse_test_case_info(child)
        # Parse Project Info
        elif child.tag == 'Prp':
            prp_name = child.attrib['name']
            prp_value = child.attrib['value']

            if prp_name == 'incompletedtests':
                prp_value = int(prp_value)
            if prp_name == 'warningtests':
                prp_value = int(prp_value)
            if prp_name == 'failedtests':
                prp_value = int(prp_value)
            if prp_name == 'duration':
                prp_name = 'duration_hrs'
                prp_value = float(prp_value) / 1000 / 60 / 60

            test_info[prp_name] = prp_value
    
    return test_info
