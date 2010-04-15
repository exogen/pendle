from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

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
    filter_by = request.GET.get('filter', 'manufacturer')
    query_str = request.GET.get('query', "").strip()
    if query_str:
        query = search_query(query_str, ['barcode', 'product__title',
                                         'product__manufacturer__name'])
        assets = Asset.objects.filter(query)
    else:
        assets = Asset.objects.all()
    assets = assets.filter(catalog=catalog_id).order_by('barcode')[:15]
    manufacturers = sorted(Manufacturer.objects.all(), key=lowercase_str)
    product_types = sorted(ProductType.objects.all(), key=lowercase_str)
    return render_to_response("assets/includes/browse_assets.html",
        {'assets': assets, 'manufacturers': manufacturers,
         'product_types': product_types, 'query': query_str,
         'filter': filter_by, 'transaction_key': transaction_key})

def lowercase_str(x):
    return unicode(x).lower()
