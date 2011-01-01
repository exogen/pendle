import hashlib
from datetime import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required

from pendle.catalog.models import Catalog
from pendle.institution.forms import ScanCustomerForm
from pendle.assets.forms import ScanAssetForm


def generate_transaction_key(request):
    session_key = request.session.session_key
    timestamp = datetime.now().isoformat()
    return hashlib.new('sha1', session_key + timestamp).hexdigest()

@staff_member_required
def scan(request):
    catalog = Catalog.objects.get_or_default()
    customer_form = ScanCustomerForm(auto_id='customer-%s')
    asset_form = ScanAssetForm(auto_id='asset-%s',
                               initial={'catalog': catalog.pk})
    transaction_key = generate_transaction_key(request)
    return render_to_response("reservations/scan.html", {
        'title': "New transaction",
        'catalog': catalog,
        'customer_form': customer_form,
        'asset_form': asset_form,
        'transaction_key': transaction_key,
        'media': customer_form.media + asset_form.media,
        }, context_instance=RequestContext(request))

@staff_member_required
def new_transaction(request, transaction_key):
    pass

