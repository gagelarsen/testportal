from django.shortcuts import render

from testportal.models import Suite


def suite_detail_view(request, name):
    context = {
        name: name,
    }

    suite = Suite.objects.get(name=name)
    test_cases = suite.test_cases.all()
    
    context['suite'] = suite
    context['test_cases'] = test_cases

    return render(request, 'testportal/suite_detail_view.html', context)