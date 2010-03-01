from django.contrib.sites.models import Site

def site(request):
    """A context processor to add the current site to the context."""
    try:
        current_site = Site.objects.get_current()
    except Site.DoesNotExist:
        current_site = None
    return {'site': current_site}

