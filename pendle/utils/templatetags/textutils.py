from django import template

from utils.text import format_dollars


register = template.Library()

register.filter('dollars', format_dollars)

