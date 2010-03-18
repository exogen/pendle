from django.shortcuts import render_to_response
from django.template import RequestContext

from pendle.assets.models import Asset
from pendle.assets.forms import SearchAssetsForm


def add_bundled_asset(request):
    search_form = SearchAssetsForm()
    return render_to_response("assets/includes/add_bundled_asset.html", {
        'opts': Asset._meta,
        'search_form': search_form}, context_instance=RequestContext(request))
