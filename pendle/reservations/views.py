import hashlib
from datetime import datetime

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction

from pendle.catalog.models import Catalog
from pendle.institution.forms import ScanCustomerForm
from pendle.assets.models import Asset
from pendle.assets.forms import ScanAssetForm
from pendle.reservations.models import Transaction
from pendle.reservations.forms import TransactionForm
from pendle.utils.views import JsonResponse, serialize_model, serialize_models, reference_model, reference_models


def generate_transaction_key(request):
    session_key = request.session.session_key
    timestamp = datetime.now().isoformat()
    return hashlib.new('sha1', session_key + timestamp).hexdigest()

def serialize_reservation(reservation, asset=True, transaction=True, customer=True):
    pass

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
    if request.method == 'POST':
        form = TransactionForm(request.POST, auto_id='transaction-%s')
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.staff_member = request.user
            transaction.save()
            now = transaction.timestamp
            periods = transaction.catalog.periods.all()

            assets_in_ids = request.POST.getlist('asset_in')
            assets_in = Asset.objects.in_bulk(assets_in_ids)
            for asset_id, asset in assets_in.iteritems():
                reservation = asset.get_current_reservation()
                if reservation:
                    reservation.transaction_in = transaction
                    reservation.save()
                else:
                    print 'No current reservation'

            assets_out_ids = request.POST.getlist('asset_out')
            assets_out = Asset.objects.in_bulk(assets_out_ids)
            for asset_id, asset in assets_out.iteritems():
                duration = asset.get_reservation_duration()
                due_date = duration and duration.get_due_date(now, periods)
                try:
                    transaction.reservations_out.create(asset=asset, due_date=due_date)
                except Exception:
                    raise

            print 'Redirecting...'
            return redirect('reservations:receipt', transaction.pk)
        else:
            print 'Transaction failed'

    return redirect('reservations:scan')

@staff_member_required
def receipt(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    return render_to_response("reservations/receipt.html", {
        'title': "Receipt for %s" % transaction,
        'transaction': transaction, 'catalog': transaction.catalog
        }, context_instance=RequestContext(request))

