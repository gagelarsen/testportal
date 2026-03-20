from django.shortcuts import render

from testportal.models import Suite


def suite_list_view(request):
    context = {}

    suites = Suite.objects.values('id', 'name', 'active').order_by('name')

    context['suites'] = suites

    return render(request, 'testportal/suite_list_view.html', context)