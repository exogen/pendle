from pendle.utils.urls import admin_url


def hyperlink(url, text, **attrs):
    attrs = [' %s="%s"' % (key, value) for key, value in attrs.iteritems()]
    return '<a href="%s"%s>%s</a>' % (url, ''.join(attrs), text)

def related_link(obj, **attrs):
    if obj is None:
        return ""
    attrs.setdefault('title', "Go to %s" % obj._meta.verbose_name)
    attrs.setdefault('class', 'related-link')
    url = admin_url('change', obj, args=[obj.pk])
    return hyperlink(url, "", **attrs)

