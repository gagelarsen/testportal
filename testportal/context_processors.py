from testportal.access import can_manage_categories


def access_flags(request):
    return {
        'can_manage_categories': can_manage_categories(request.user),
    }
