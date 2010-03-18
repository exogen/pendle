# -*- coding: utf-8 -*-
from django.utils.encoding import force_unicode


def truncate(text, max_length, tail=u'…'):
    text = force_unicode(text)
    if max_length is not None and len(text) > max_length:
        text = text[:max_length] + tail
    return text

