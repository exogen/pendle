# -*- coding: utf-8 -*-
from django.utils.encoding import force_unicode
from django.utils.formats import number_format


def truncate(text, max_length, tail=u'…'):
    text = force_unicode(text)
    if max_length is not None and len(text) > max_length:
        text = text[:max_length] + tail
    return text

def format_dollars(n):
    text = number_format(n, 2)
    if text.endswith('.00'):
        text = text[:-3]
    if text.startswith('-'):
        text = '-$' + text[1:]
    else:
        text = '$' + text
    return text

