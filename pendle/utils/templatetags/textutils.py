from django import template

from utils.text import format_dollars, truncate


register = template.Library()

register.filter('dollars', format_dollars)

@register.filter('truncate')
def truncate_filter(value, arg):
    args = unicode(arg).split(',', 1)
    if args:
        args[0] = int(args[0])
    else:
        args.append(80)
    return truncate(value, *args)
