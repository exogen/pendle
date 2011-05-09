from collections import defaultdict
from datetime import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core import serializers

from pendle.catalog.models import Catalog
from pendle.assets.models import Manufacturer, ProductType, Asset
from pendle.assets.forms import ScanAssetForm
from pendle.utils.models import search_query
from pendle.utils.views import JsonResponse, serialize_model, serialize_models, reference_model, reference_models
from pendle.institution.views import serialize_user


def add_bundled_asset(request):
    search_form = SearchAssetsForm()
    return render_to_response("assets/includes/add_bundled_asset.html", {
        'opts': Asset._meta,
        'search_form': search_form}, context_instance=RequestContext(request))

def serialize_asset(asset, bundled=False, reservation=False, customer=False):
    objects = defaultdict(dict)

    reference = reference_model('assets:asset', asset)
    result = serialize_model(asset)[asset.pk]

    result['condition'] = asset.get_condition_display()

    result['product'] = reference_model('assets:product', asset.product)
    serialized_product = serialize_model(asset.product)
    if asset.product.manufacturer:
        serialized_product['manufacturer'] = reference_model('assets:manufacturer', asset.product.manufacturer)
        objects['assets:manufacturer'] = serialize_model(asset.product.manufacturer)
    objects['assets:product'].update(serialized_product)

    result['available'] = asset.is_available()
    due_date = asset.get_due_date()
    if due_date:
        result['due_date'] = due_date.strftime('%m/%d/%Y %I:%M %p')

    if bundled:
        bundled = asset.bundled_assets.all().order_by('bundle_order')
        result['bundled'] = reference_models('assets:asset', bundled)
        for bundled_asset in bundled:
            bundled_result, bundled_objects = serialize_asset(bundled_asset,
                bundled=False, reservation=reservation, customer=customer)
            for type, type_objects in bundled_objects.items():
                objects[type].update(type_objects)

    if reservation:
        reservation = asset.get_current_reservation()
        if reservation:
            result['reservation'] = reference_model('reservations:reservation', reservation)
            serialized_reservation = serialize_model(reservation)
            serialized_reservation[reservation.pk]['transaction'] = reference_model(
                'reservations:transaction', reservation.transaction_out)
            serialized_transaction = serialize_model(reservation.transaction_out)
            if customer:
                customer, customer_objects = serialize_user(reservation.transaction_out.customer,
                    fines=True, reservations=False)
                serialized_transaction[reservation.transaction_out.pk]['customer'] = customer
                for type, type_objects in customer_objects.items():
                    objects[type].update(type_objects)
            objects['reservations:transaction'].update(serialized_transaction)
            objects['reservations:reservation'].update(serialized_reservation)

    objects['assets:asset'].update({asset.pk: result})
    return reference, objects

def scan_asset(request, transaction_key):
    asset_form = ScanAssetForm(request.GET)
    if asset_form.is_valid():
        asset = asset_form.cleaned_data['asset']
        objects = {}
        result, objects = serialize_asset(asset, bundled=True, reservation=True, customer=True)
        response = {'result': result, 'objects': objects}
        return JsonResponse(response)
    else:
        query = asset_form.data['query']
        message = render_to_string("assets/includes/scan_asset_add.html", {
            'transaction_key': transaction_key,
            'query': query,
            }, context_instance=RequestContext(request))
        response = {'result': None, 'message': message}
        return JsonResponse(response, status=404)

def browse_assets(request, transaction_key):
    catalog_id = request.GET.get('catalog')
    catalog = Catalog.objects.get_or_default(catalog_id)
    filter_by = request.GET.get('filter', 'none')
    query_str = request.GET.get('query', "").strip()
    if not query_str and not filter_by:
        filter_by = 'manufacturer'
    context = {'transaction_key': transaction_key, 'filter': filter_by,
               'query': query_str, 'catalog': catalog, 'assets': None}
    if query_str:
        query = search_query(query_str, ['barcode', 'product__title',
                                         'product__manufacturer__name'])
        assets = Asset.objects.filter(query)
    else:
        assets = Asset.objects.all()
    assets = assets.filter(catalog=catalog).order_by('barcode')
    if filter_by == 'manufacturer':
        manufacturer_id = request.GET.get('manufacturer')
        if manufacturer_id:
            context['manufacturer'] = Manufacturer.objects.get(
                id=manufacturer_id)
            assets = assets.filter(product__manufacturer=manufacturer_id)
        else:
            context['manufacturers'] = sorted(Manufacturer.objects.all(),
                                              key=lowercase_str)
    elif filter_by == 'type':
        type_id = request.GET.get('type')
        if type_id:
            context['product_type'] = ProductType.objects.get(id=type_id)
            assets = assets.filter(product__product_type=type_id)
        else:
            context['product_types'] = sorted(ProductType.objects.all(),
                                              key=lowercase_str)
    return JsonResponse({
        'query': query_str,
        'results': [{'value': asset.barcode,
                     'barcode': asset.barcode,
                     'manufacturer': {'name': asset.product.manufacturer and
                                              asset.product.manufacturer.name},
                     'product': {'title': asset.product.title}}
                     for asset in assets]})

def lowercase_str(x):
    return unicode(x).lower()

