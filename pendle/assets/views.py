from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from pendle.assets.models import Asset
from pendle.assets.forms import ScanAssetForm
from pendle.utils.views import JsonResponse


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

