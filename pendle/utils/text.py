# -*- coding: utf-8 -*-
from django.utils.encoding import force_unicode


def truncate(text, max_length, tail=u'…'):
    text = force_unicode(text)
    if max_length is not None and len(text) > max_length:
        text = text[:max_length] + tail
    return text

def format_dollars(n):
    return "%s$%0.*f" % ('-' if n < 0 else '',
                         0 if int(n) == n else 2, abs(n))

