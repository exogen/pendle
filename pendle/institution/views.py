from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from pendle.institution.forms import ScanCustomerForm
from pendle.fines.models import Fine
from pendle.utils.views import JsonResponse
from pendle.utils.models import search_query


def scan_customer(request, transaction_key):
    transaction_data = request.session.get(transaction_key, {})
    context = {'transaction': transaction_data}
    customer_form = ScanCustomerForm(request.POST, auto_id='customer-%s')
    if customer_form.is_valid():
        customer = customer_form.cleaned_data['customer']
        context['customer'] = customer
        context['fines'] = Fine.objects.get_amount_due(customer)
    return JsonResponse({
        'html': render_to_string("institution/includes/scan_customer.html",
            context)})

def browse_customers(request, transaction_key):
    query_str = request.GET.get('query', "").strip()
    if query_str:
        query = search_query(query_str, ['first_name', 'last_name',
                                         'username', 'email',
                                         'profile__id_number'])
        customers = User.objects.filter(query)
    else:
        customers = User.objects.all()
    return render_to_response("institution/includes/browse_customers.html",
        {'customers': customers, 'query': query_str})

