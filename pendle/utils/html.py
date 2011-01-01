def hyperlink(url, text, attrs=(), **kwargs):
    attrs = dict(attrs)
    attrs.update(kwargs)
    attr_list = [' %s="%s"' % (name, attrs[name]) for name in attrs]
    return '<a href="%s"%s>%s</a>' % (url, ''.join(attr_list), text)

