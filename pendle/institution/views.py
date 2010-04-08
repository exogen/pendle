from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.models import User

from institution.models import find_user
from utils.views import JsonResponse


def scan_customer(request, transaction_key):
    transaction_data = request.session.get(transaction_key, {})
    query = request.GET.get('query')
    try:
        customer = find_user(query)
    except User.DoesNotExist:
        response = {'customer': None}
    else:
        response = {'customer': customer}
    response['html'] = render_to_string(
        "institution/includes/scan_customer.html", response,
        context_instance=RequestContext(request))
    return JsonResponse(response)

