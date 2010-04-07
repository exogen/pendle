try:
    import simplejson
except ImportError:
    from django.utils import simplejson

def JsonResponse(data, **kwargs):
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        **kwargs)

