from urllib import urlencode

from django.core.urlresolvers import reverse
from django.db.models import Model


def admin_url(short_name, model_or_instance, args=(), **params):
    app_label = model_or_instance._meta.app_label
    module_name = model_or_instance._meta.module_name
    view_name = 'admin:%s_%s_%s' % (app_label, module_name, short_name)
    url = reverse(view_name, args=args)
    if params:
        for key in params:
            value = params[key]
            if isinstance(value, Model):
                params[key] = value.pk
        query_params = urlencode(params)
        url += '?' + query_params
    return url

