from urllib import urlencode

from django import template


register = template.Library()

@register.filter
def urlparams(value):
    return urlencode(value)

