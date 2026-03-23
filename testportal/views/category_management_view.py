from django.db.models.deletion import ProtectedError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from testportal.access import can_manage_categories
from testportal.models import Suite, TestCategory, TestSubcategory


def category_management_view(request):
    if not can_manage_categories(request.user):
        raise PermissionDenied

    error_message = ''
    success_message = ''

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        if action == 'add-category':
            category_name = (request.POST.get('category') or '').strip()
            if category_name:
                _, created = TestCategory.objects.get_or_create(category=category_name)
                success_message = 'Category added.' if created else 'Category already exists.'

        elif action == 'delete-category':
            category_id = request.POST.get('category_id')
            if category_id:
                try:
                    TestCategory.objects.get(id=category_id).delete()
                    success_message = 'Category removed.'
                except TestCategory.DoesNotExist:
                    pass
                except ProtectedError:
                    error_message = 'Cannot remove category because test cases still reference it.'

        elif action == 'add-subcategory':
            subcategory_name = (request.POST.get('subcategory') or '').strip()
            if subcategory_name:
                _, created = TestSubcategory.objects.get_or_create(subcategory=subcategory_name)
                success_message = 'Subcategory added.' if created else 'Subcategory already exists.'

        elif action == 'delete-subcategory':
            subcategory_id = request.POST.get('subcategory_id')
            if subcategory_id:
                try:
                    TestSubcategory.objects.get(id=subcategory_id).delete()
                    success_message = 'Subcategory removed.'
                except TestSubcategory.DoesNotExist:
                    pass
                except ProtectedError:
                    error_message = 'Cannot remove subcategory because test cases still reference it.'

    context = {
        'suites': Suite.objects.filter(active=True),
        'categories': TestCategory.objects.all(),
        'subcategories': TestSubcategory.objects.all(),
        'error_message': error_message,
        'success_message': success_message,
    }
    return render(request, 'testportal/category_management_view.html', context)
