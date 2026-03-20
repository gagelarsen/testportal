import re
from datetime import date, timedelta

from django.shortcuts import render

from testportal.models import BugVerification, Product, Suite, TestSubcategory


def _parse_or_default_date(value, default_date, errors, label):
    if value is None:
        return default_date
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f'Invalid {label} date specified: {value}. Using default value instead.')
        return default_date


def bug_verifications_general_view(request):
    context = {
        'suites': Suite.objects.filter(active=True)
    }
    errors = []

    default_start = date.today() - timedelta(days=30 * 5)
    default_end = date.today()

    start_day_date = _parse_or_default_date(request.GET.get('start_day', None), default_start, errors, 'start')
    end_day_date = _parse_or_default_date(request.GET.get('end_day', None), default_end, errors, 'end')

    product = request.GET.get('product', None)
    category = request.GET.get('category', None)

    context['selected_product'] = None
    context['selected_category'] = None

    bug_verifications = BugVerification.objects.filter(
        fixed_date__gte=start_day_date, fixed_date__lte=end_day_date
    )

    if product is not None:
        p = re.match(r'(.+)-([^-]+)$', product)
        if p:
            product_name, product_version = p.groups()
            try:
                prod = Product.objects.get(name=product_name, version=product_version)
                context['selected_product'] = prod
                bug_verifications = bug_verifications.filter(products=prod)
            except Product.DoesNotExist:
                errors.append(f'No matching product exists for {product}')
        else:
            errors.append(f'Invalid product specified: {product}')
    
    if category is not None:
        try:
            c = TestSubcategory.objects.get(subcategory=category)
            context['selected_category'] = c
            bug_verifications = bug_verifications.filter(category=c)
        except TestSubcategory.DoesNotExist:
            errors.append(f'No matching category exists for {category}')

    context['bug_verifications'] = bug_verifications
    context['products'] = Product.objects.all()
    context['categories'] = TestSubcategory.objects.all()
    context['start_day'] = start_day_date.strftime('%Y-%m-%d')
    context['end_day'] = end_day_date.strftime('%Y-%m-%d')
    context['errors'] = errors

    return render(request, 'testportal/bug_verifications_general_view.html', context)


def bug_verification_report(request, name, version):
    context = {
        'name': name,
        'version': version,
        'suites': Suite.objects.filter(active=True)
    }
    errors = []
    verification_dict = {}

    default_start = date.today() - timedelta(days=30 * 5)
    default_end = date.today()

    start_day_date = _parse_or_default_date(request.GET.get('start_day', None), default_start, errors, 'start')
    context['start_date'] = start_day_date.strftime('%Y-%m-%d')

    end_day_date = _parse_or_default_date(request.GET.get('end_day', None), default_end, errors, 'end')
    context['end_date'] = end_day_date.strftime('%Y-%m-%d')

    context['product'] = None

    try:
        product = Product.objects.get(name=name, version=version)
        context['product'] = product
    except Product.DoesNotExist:
        errors.append(f'Product ({name}-{version}) does not exist...')

    if not errors:
        verifications = BugVerification.objects.filter(
            products=product, fixed_date__gte=start_day_date, fixed_date__lte=end_day_date
        )

        for verification in verifications:
            if verification.category not in verification_dict:
                verification_dict[verification.category] = []
            verification_dict[verification.category].append(verification)

    context['verifications'] = verification_dict
    context['errors'] = errors

    return render(request, 'testportal/bug_verification_report.html', context)