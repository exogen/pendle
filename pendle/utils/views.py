from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder


def JsonResponse(data, **kwargs):
    if not isinstance(data, basestring):
        data = simplejson.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(data, mimetype='application/json', **kwargs)

def default_serializer(instance, **kwargs):
    return serialize('python', [instance], **kwargs)[0]

def serialize_model(instance, serializer=default_serializer, **kwargs):
    return serialize_models([instance], serializer=serializer, **kwargs)

def serialize_models(queryset, serializer=default_serializer, **kwargs):
    instances = {}
    for instance in queryset:
        if instance.pk not in instances:
            instances[instance.pk] = serializer(instance, **kwargs)
    return instances

def reference_models(type, queryset):
    return {'type': type, 'ids': [instance.pk for instance in queryset]}

def reference_model(type, instance):
    return {'type': type, 'id': instance.pk}

