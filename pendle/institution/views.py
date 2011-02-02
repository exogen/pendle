from collections import defaultdict

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.core.serializers import serialize

from pendle.institution.forms import ScanCustomerForm, ScanNewCustomerForm, ScanNewProfileForm
from pendle.reservations.models import Reservation
from pendle.fines.models import Fine
from pendle.utils.models import search_query
from pendle.utils.views import JsonResponse, serialize_model, serialize_models, reference_model, reference_models

def serialize_user(user, fines=True, reservations=True):
    from pendle.assets.views import serialize_asset

    objects = defaultdict(dict)

    fields = ['username', 'first_name', 'last_name', 'groups', 'email']
    reference = reference_model('auth:user', user)
    result = serialize_model(user, fields=fields)[user.pk]

    departments = user.departments.all()
    result['departments'] = reference_models('institution:department', departments)
    objects['institution:department'].update(serialize_models(departments, fields=['name']))

    if fines:
        result['fines'] = max(0, Fine.objects.get_amount_due(user))

    if reservations:
        reservations = Reservation.objects.checked_out(transaction_out__customer=user).select_related()
        result['reservations'] = reference_models('reservations:reservation', reservations)

        serialized_reservations = serialize_models(reservations)

        transactions = []
        for reservation in reservations:
            transaction = reservation.transaction_out
            transactions.append(transaction)
            serialized_reservation = serialized_reservations[reservation.pk]
            serialized_reservation['transaction'] = reference_model('reservations:transaction', transaction)
            asset, reservation_objects = serialize_asset(reservation.asset, bundled=True)
            serialized_reservation['asset'] = asset
            for type, type_objects in reservation_objects.items():
                objects[type].update(type_objects)
            serialized_reservation['overdue'] = reservation.is_overdue()

        serialized_transactions = serialize_models(transactions)

        for transaction in transactions:
            serialized_transactions[transaction.pk]['customer'] = reference

        objects['reservations:transaction'].update(serialized_transactions)
        objects['reservations:reservation'].update(serialized_reservations)

    objects['auth:user'].update({user.pk: result})
    return reference, objects

def scan_customer(request, transaction_key):
    transaction_data = request.session.get(transaction_key, {})
    customer_form = ScanCustomerForm(request.GET, auto_id='customer-%s')
    if customer_form.is_valid():
        customer = customer_form.cleaned_data['customer']
        result, objects = serialize_user(customer)
        response = {'result': result, 'objects': objects}
        return JsonResponse(response)
    else:
        query = customer_form.data['query']
        if query.isdigit():
            id_number = query
        else:
            id_number = ''
        new_form = ScanNewCustomerForm(auto_id='new-customer-%s',
            initial={'username': query})
        profile_form = ScanNewProfileForm(auto_id='new_customer-%s',
            initial={'id_number': id_number})
        message = render_to_string("institution/includes/scan_customer_add.html", {
            'transaction_key': transaction_key,
            'customer_form': new_form,
            'profile_form': profile_form,
            'query': query,
            }, context_instance=RequestContext(request))
        response = {'result': None, 'message': message}
        return JsonResponse(response, status=404)

def scan_customer_add(request, transaction_key):
    customer_form = ScanNewCustomerForm(auto_id='new-customer-%s')
    profile_form = ScanNewProfileForm(auto_id='new-customer-%s')
    if request.method == 'POST':
        customer_form = ScanNewCustomerForm(request.POST, auto_id='new-customer-%s')
        if customer_form.is_valid():
            customer = customer_form.save()
            profile = customer.get_profile()
            profile_form = ScanNewProfileForm(request.POST, auto_id='new_customer-%s',
                instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                department = profile_form.cleaned_data['department']
                if department:
                    customer.departments.add(department)
            result, objects = serialize_user(customer)
            response = {'result': result, 'objects': objects}
            return JsonResponse(response)
    return JsonResponse({'result': None, 'message': "Error"})

def browse_customers(request, transaction_key):
    query_str = request.GET.get('query', "").strip()
    response = {'query': query_str}
    if query_str:
        query = search_query(query_str, ['first_name', 'last_name',
                                         'username', 'email',
                                         'profile__id_number'])
        customers = User.objects.filter(query)
    else:
        customers = User.objects.all()
    results = []
    for customer in customers:
        results.append({'value': customer.username,
                        'username': customer.username,
                        'fullName': customer.get_full_name(),
                        'idNumber': customer.get_profile().id_number})
    return JsonResponse({
        'query': query_str,
        'container': '#customers tbody',
        'results': results,
        'template': render_to_string("institution/includes/browse_customer.html")})

