from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from utils.views import JsonResponse


def scan_customer(request, transaction_key):
    return render_to_response("institution/includes/scan_customer.html")

