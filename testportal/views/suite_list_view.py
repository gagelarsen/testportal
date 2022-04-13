from django.shortcuts import render

from testportal.models import Suite


def suite_list_view(request):
    context = {}

    suites = Suite.objects.all().values('id', 'name', 'active')

    context['suites'] = suites

    return render(request, 'testportal/suite_list_view.html', context)