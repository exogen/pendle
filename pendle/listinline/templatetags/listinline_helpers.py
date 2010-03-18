from django import template
from django.contrib.admin.helpers import AdminField

from listinline import REMOVAL_FIELD_NAME


register = template.Library()

@register.inclusion_tag("listinline/removal_field.html")
def removal_field(admin_form, field=REMOVAL_FIELD_NAME, is_first=False):
    return {'removal_field': AdminField(admin_form.form, field, is_first)}

