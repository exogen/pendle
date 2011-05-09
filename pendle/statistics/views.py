from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Count

from pendle.catalog.models import Catalog
from pendle.assets.models import Product, Asset
from pendle.reservations.models import Reservation, Transaction

def home(request):
    catalog = Catalog.objects.get_or_default()
    most_reserved = Product.objects.annotate(
        reservation_count=Count('assets__reservations')
    ).order_by('-reservation_count').select_related()[:50]
    oldest = Asset.objects.filter(
        purchase_date__isnull=False).order_by(
        'purchase_date').select_related()[:50]
    return render_to_response('statistics/home.html', {
        'title': "Statistics",
        'catalog': catalog,
        'most_reserved': most_reserved,
        'oldest': oldest
        }, context_instance=RequestContext(request))

