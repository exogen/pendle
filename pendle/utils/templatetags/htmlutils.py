from urllib import urlencode

from django import template


register = template.Library()

@register.filter
def urldata(value):
    return urlencode(value)

