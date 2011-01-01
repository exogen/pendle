from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from pendle.catalog.models import Catalog
from pendle.assets.models import Manufacturer, ProductType, Asset
from pendle.assets.forms import ScanAssetForm
from pendle.utils.views import JsonResponse
from pendle.utils.models import search_query


def add_bundled_asset(request):
    search_form = SearchAssetsForm()
    return render_to_response("assets/includes/add_bundled_asset.html", {
        'opts': Asset._meta,
        'search_form': search_form}, context_instance=RequestContext(request))


def scan_asset(request, transaction_key):
    asset_form = ScanAssetForm(request.POST)
    context = {'asset_form': asset_form}
    if asset_form.is_valid():
        context['asset'] = asset_form.cleaned_data['asset']
    else:
        print asset_form.errors
    return JsonResponse({
        'html': render_to_string("assets/includes/scan_asset.html",
            context, context_instance=RequestContext(request))})

def browse_assets(request, transaction_key):
    catalog_id = request.GET.get('catalog')
    catalog = Catalog.objects.get(id=catalog_id)
    filter_by = request.GET.get('filter')
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
    assets = assets.filter(catalog=catalog_id).order_by('barcode')
    if filter_by == 'manufacturer':
        manufacturer_id = request.GET.get('manufacturer')
        if manufacturer_id:
            context['manufacturer'] = Manufacturer.objects.get(
                id=manufacturer_id)
            context['assets'] = assets.filter(
                product__manufacturer=manufacturer_id)
        else:
            context['manufacturers'] = sorted(Manufacturer.objects.all(),
                                              key=lowercase_str)
    elif filter_by == 'type':
        type_id = request.GET.get('type')
        if type_id:
            context['product_type'] = ProductType.objects.get(id=type_id)
            context['assets'] = assets.filter(product__product_type=type_id)
        else:
            context['product_types'] = sorted(ProductType.objects.all(),
                                              key=lowercase_str)
    else:
        context['assets'] = assets
    return render_to_response("assets/includes/browse_assets.html", context)

def lowercase_str(x):
    return unicode(x).lower()

