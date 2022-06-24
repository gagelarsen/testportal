import re
from datetime import date, timedelta

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from testportal.models import BugVerification, TestCategory, Product, Suite


def bug_verifications_general_view(request):
    context = {
        'suites': Suite.objects.filter(active=True)
    }
    errors = []

    start_day = request.GET.get('start_day', None)
    if start_day is None:
        start_day = (date.today() - timedelta(days=30*5)).strftime('%Y-%m-%d')

    end_day = request.GET.get('end_day', None)
    if end_day is None:
        end_day = date.today().strftime('%Y-%m-%d')

    product = request.GET.get('product', None)
    category = request.GET.get('category', None)

    context['selected_product'] = None
    context['selected_category'] = None

    bug_verifications = BugVerification.objects.all().filter(
        fixed_date__gte=start_day, fixed_date__lte=end_day
    )

    if product is not None:
        p = re.match('(.+)-(.+)', product)
        if p:
            try:
                errors.append(p.groups())
                prod = Product.objects.get(name=p.groups()[0], version=p.groups()[1])
                context['selected_product'] = prod
                bug_verifications = bug_verifications.filter(products=prod)
            except ObjectDoesNotExist:
                errors.append(f'No matching product exists for {product}')
        else:
            errors.append(f'Invalid product specified: {product}')
    
    if category is not None:
        try:
            c = TestCategory.objects.get(category=category)
            context['selected_category'] = c
            bug_verifications = bug_verifications.filter(category=c)
        except ObjectDoesNotExist:
            errors.append(f'No matching category exists for {category}')

    context['bug_verifications'] = bug_verifications
    context['products'] = Product.objects.all()
    context['categories'] = TestCategory.objects.all()
    context['start_day'] = start_day
    context['end_day'] = end_day
    context['errors'] = errors

    return render(request, 'testportal/bug_verifications_general_view.html', context)


def bug_verification_report(request, name, version):
    context = {
        'name': name,
        'version': version,
        'suites': Suite.objects.filter(active=True)
    }
    errors = []
    verifcation_dict = {}

    start_day = request.GET.get('start_day', None)
    if start_day is None:
        start_day = (date.today() - timedelta(days=30*5)).strftime('%Y-%m-%d')
    context['start_date'] = start_day

    end_day = request.GET.get('end_day', None)
    if end_day is None:
        end_day = date.today().strftime('%Y-%m-%d')
    context['end_date'] = end_day


    try:
        product = Product.objects.get(name=name, version=version)
        context['product'] = product
    except ObjectDoesNotExist as e:
        errors.append(f'Product ({product}) does not exist...')

    if len(errors) <= 0:
        verifications = BugVerification.objects.filter(
            products=product, fixed_date__gte=start_day, fixed_date__lte=end_day
        )

        for verification in verifications:
            if verification.category not in verifcation_dict:
                verifcation_dict[verification.category] = []
            verifcation_dict[verification.category].append(verification)

    context['verifications'] = verifcation_dict

    return render(request, 'testportal/bug_verification_report.html', context)