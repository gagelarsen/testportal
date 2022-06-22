from django.shortcuts import render


def bug_verifications_general_view(request):
    context = {}
    return render(request, 'testportal/bug_verifications_general_view.html', context)