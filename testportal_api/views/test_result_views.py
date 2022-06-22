from datetime import datetime
import xml.etree.ElementTree as ET

from django.http import JsonResponse

from rest_framework import generics

from testportal.models import TestResult, TestCase, Suite
from testportal_api.serializers import TestResultSerializer


class TestResultList(generics.ListCreateAPIView):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer


class TestResultDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = TestResult.objects.all()
   serializer_class = TestResultSerializer


def delete_test_results_for_date_and_suite(request, suite, month, day, year):
    try:
        suite = Suite.objects.get(name=suite)
    except Exception as e:
        return JsonResponse({"error": "Unable to find suite to delete results from..."}, status=404)

    try:
        dt = datetime.strptime(f'{month}-{day}-{year}', '%m-%d-%Y').date()
    except Exception as e:
        return JsonResponse({"error": "Unable to parse date from url..."}, status=400)

    try:
        TestResult.objects.all().filter(test_case__suite=suite, result_date=dt).delete()
    except:
        return JsonResponse({"error": "Unable to process result deletion..."}, status=400)


    return JsonResponse({
        "message": 'Successfully deleted results',
    }, status=201)

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
            '3': 'skipped',
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

def copy_result_to_latest(request, result_id):
    try:
        result = TestResult.objects.get(id=result_id)
    except Exception as e:
        return JsonResponse({"error": f"Unable to find the result with id: {result_id}..."}, status=404)

    test_case = result.test_case

    try:
        results = TestResult.objects.all().filter(test_case=test_case).order_by('-result_date')
        latest_result = results[0]
    except:
        return JsonResponse({"error": f"No results availabe for this test case: {result.test_case.name} ({len(results)})..."}, status=404)


    if result.id == latest_result.id:
        return JsonResponse({"error": "This is the most recenet result."}, status=418)

    latest_result.note = str(result.note) + "(Copied)"
    latest_result.user = request.user
    latest_result.test_case = result.test_case
    latest_result.duration = result.duration
    latest_result.bug_id = result.bug_id if result.bug_id else ''
    latest_result.result = result.result
    

    try:
        latest_result.save()
    except:
        return JsonResponse({"error": "Unable to save result copy..."}, status=400)


    return JsonResponse({
        "message": f'Successfully copied result {result.id} -> {latest_result.id}',
        "updated_result_id": latest_result.id,
        "updated_result_status": latest_result.result,
        "updated_result_status_text": latest_result.result.replace('-', ' ').title(),
        "updated_result_bug_id": latest_result.bug_id,
        "updated_result_note": latest_result.note,
        "updated_result_user": latest_result.user.username,
    }, status=201)
