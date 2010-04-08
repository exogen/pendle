from django.http import HttpResponse
from django.utils import simplejson

def JsonResponse(data, **kwargs):
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        **kwargs)

