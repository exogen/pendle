from django import template


register = template.Library()

@register.inclusion_tag("assets/includes/availability.html")
def show_availability(asset):
    available = asset.reservable and asset.catalog.online
    reservation = asset.get_current_reservation()
    if reservation is None:
        current_customer = None
    else:
        available = False
        current_customer = reservation.transaction_out.customer
    return {'asset': asset,
            'available': available,
            'reservation': reservation,
            'current_customer': current_customer}

