from django.utils.encoding import force_unicode

from pendle.utils.urls import admin_url


def hyperlink(url, text, attrs=(), **kwargs):
    attrs = dict(attrs)
    attrs.update(kwargs)
    attr_list = [' %s="%s"' % (name, attrs[name]) for name in attrs]
    return '<a href="%s"%s>%s</a>' % (url, ''.join(attr_list), text)

def change_link(obj, text="", attrs=(), **kwargs):
    if obj is not None:
        attrs = dict(attrs)
        attrs.update(kwargs)
        verbose_name = force_unicode(obj._meta.verbose_name)
        attrs.setdefault('title', "Go to %s" % verbose_name)
        attrs.setdefault('class', 'related')
        url = admin_url('change', obj, args=[obj.pk])
        return hyperlink(url, text, attrs)

def changelist_link(model, text="", params=(), attrs=(), **kwargs):
    attrs = dict(attrs)
    attrs.update(kwargs)
    verbose_name_plural = force_unicode(model._meta.verbose_name_plural)
    attrs.setdefault('title', "Find %s" % verbose_name_plural)
    attrs.setdefault('class', 'related')
    url = admin_url('changelist', model, params=params)
    return hyperlink(url, text, attrs)

