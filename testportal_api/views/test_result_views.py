from datetime import datetime
import xml.etree.ElementTree as ET

from django.http import JsonResponse
from django.db import DatabaseError, IntegrityError

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
    except Suite.DoesNotExist:
        return JsonResponse({"error": "Unable to find suite to delete results from..."}, status=404)

    try:
        dt = datetime.strptime(f'{month}-{day}-{year}', '%m-%d-%Y').date()
    except ValueError:
        return JsonResponse({"error": "Unable to parse date from url..."}, status=400)

    try:
        TestResult.objects.all().filter(test_case__suite=suite, result_date=dt).delete()
    except DatabaseError:
        return JsonResponse({"error": "Unable to process result deletion..."}, status=400)


    return JsonResponse({
        "message": 'Successfully deleted results',
    }, status=201)


def upload_test_results(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is supported for this endpoint."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication is required to upload test results."}, status=401)

    form_files = request.FILES
    result_date = request.POST.get('upload-results-date', None)

    if len(form_files) == 0:
        return JsonResponse({"error": "File was not uploaded correctly... See system administrator."}, status=400)
    if len(form_files) > 1:
        return JsonResponse({"error": "Cannot process multiple files. Please select only one to upload."}, status=400)

    if not result_date:
        return JsonResponse({"error": "Missing required upload date (upload-results-date)."}, status=400)

    try:
        parsed_result_date = datetime.strptime(result_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({"error": "Invalid upload-results-date format. Expected YYYY-MM-DD."}, status=400)

    file_to_upload = next(iter(form_files.values()), None)
    if file_to_upload is None:
        return JsonResponse({"error": "No upload file provided."}, status=400)

    results = {
        '0': 'pass',
        '1': 'pass',
        '2': 'fail',
        '3': 'skipped',
    }

    try:
        test_info = _parse_result_file(file_to_upload)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    try:
        suite = Suite.objects.get(id=pk)
    except Suite.DoesNotExist:
        return JsonResponse({"error": "Unable to find suite for uploaded results."}, status=404)

    suite_cases = {x.name: x for x in TestCase.objects.filter(suite=suite)}
    deprecated_names = {name for name, tc in suite_cases.items() if tc.status == 'depricated'}
    missing_cases = []
    test_results = {}

    for result in test_info.get('test_cases', []):
        name = result.get('name')
        status = result.get('status')
        duration_seconds = result.get('duration_seconds')

        if not name:
            continue

        test_case = suite_cases.get(name, None)
        if test_case is None:
            # If it's not in our suite at all, report it as unrecognised
            missing_cases.append(f'{name}')
            continue

        # Silently skip deprecated cases — no result created, not flagged as missing
        if test_case.status == 'depricated':
            continue

        test_results[name] = TestResult(
            user=request.user,
            test_case=test_case,
            result_date=parsed_result_date,
            duration=duration_seconds,
            result=results.get(status, 'fail')
        )

    # Exclude deprecated cases from the missing-results warning
    missing_results = list(set(suite_cases.keys()) - set(test_results.keys()) - deprecated_names)

    try:
        TestResult.objects.bulk_create(test_results.values())
    except IntegrityError:
        return JsonResponse({
            "error": "Unable to upload results due to conflicting existing rows (result_date + test_case)."
        }, status=409)
    except DatabaseError:
        return JsonResponse({"error": "Unable to save uploaded test results."}, status=400)

    return JsonResponse({
        "message": 'Successfully uploaded results',
        "missing_results": missing_results,
        "missing_cases": missing_cases
    }, status=201)


def _parse_test_case_info(node):
    all_test_info = []
    for child in node:
        test_info = {}
        for prp in child:
            if prp.tag != 'Prp':
                continue
            prp_name = prp.attrib.get('name')
            prp_value = prp.attrib.get('value')
            if prp_name in ['status', 'duration', 'name'] and prp_value is not None:
                if prp_name == 'duration':
                    prp_name = 'duration_seconds'
                    try:
                        prp_value = float(prp_value) / 1000
                    except (TypeError, ValueError):
                        prp_value = None
                test_info[prp_name] = prp_value
        all_test_info.append(test_info)
    return all_test_info


def _parse_result_file(summary_file):
    try:
        tree = ET.parse(summary_file)
        root = tree.getroot()
        project_node = root[0][0][0]
    except (ET.ParseError, IndexError, TypeError):
        raise ValueError('Unable to parse uploaded result file format.')

    test_info = {}

    for child in project_node:
        # Parse Test Data
        if child.tag == 'Node' and child.attrib.get('name', 'none') == 'tests':
            test_info['test_cases'] = _parse_test_case_info(child)
        # Parse Project Info
        elif child.tag == 'Prp':
            prp_name = child.attrib.get('name')
            prp_value = child.attrib.get('value')

            if prp_name is None or prp_value is None:
                continue

            if prp_name in ['incompletedtests', 'warningtests', 'failedtests']:
                try:
                    prp_value = int(prp_value)
                except ValueError:
                    continue
            if prp_name == 'duration':
                prp_name = 'duration_hrs'
                try:
                    prp_value = float(prp_value) / 1000 / 60 / 60
                except ValueError:
                    continue

            test_info[prp_name] = prp_value

    if 'test_cases' not in test_info:
        test_info['test_cases'] = []
    
    return test_info


def copy_result_to_latest(request, result_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication is required to copy test results."}, status=401)

    try:
        result = TestResult.objects.get(id=result_id)
    except TestResult.DoesNotExist:
        return JsonResponse({"error": f"Unable to find the result with id: {result_id}..."}, status=404)

    test_case = result.test_case

    results = TestResult.objects.all().filter(test_case=test_case).order_by('-result_date')
    latest_result = results.first()
    if latest_result is None:
        return JsonResponse({"error": f"No results available for this test case: {result.test_case.name} ({len(results)})..."}, status=404)


    if result.id == latest_result.id:
        return JsonResponse({"error": "This is the most recent result."}, status=418)

    latest_result.note = f"{result.note or ''}(Copied)"
    latest_result.user = request.user
    latest_result.test_case = result.test_case
    latest_result.duration = result.duration
    latest_result.bug_id = result.bug_id if result.bug_id else ''
    latest_result.result = result.result
    

    try:
        latest_result.save()
    except DatabaseError:
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
