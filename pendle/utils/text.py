from django.utils.encoding import force_unicode


def truncate(text, max_length, tail='&hellip;'):
    text = force_unicode(text)
    if len(text) > max_length:
        text = text[:max_length] + tail
    return text

