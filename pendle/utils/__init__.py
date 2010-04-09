import inspect
from datetime import datetime


def current_year():
    return datetime.now().year

def add(list_, short_description=None, position=None, **kwargs):
    """
    A helper to add a method to `list_` (usually `ModelAdmin.list_display`),
    where the method's name is added, and items may have attributes like
    `short_description` and `boolean`.
    
    `position` is the index at which to insert the item. By default, items
    are appended.
    
    Example:
    
    class ExampleAdmin(admin.ModelAdmin):
        list_display = ['__str__']
        
        @add(list_display, "in progress?", boolean=True)
        def in_progress(self, object):
            return not object.is_complete
    
        @add(list_display, mark_safe('&#x2713;'), 0, allow_tags=True)
        def checkbox(self, object):
            return '<input type="checkbox" value="%s"/>' % object.pk
    
    """
    if short_description is not None:
        kwargs['short_description'] = short_description
    def decorate(f):
        if isinstance(f, basestring):
            list_.append(f)
        else:
            num_args = len(inspect.getargspec(f)[0])
            func_value = f if num_args == 1 else f.__name__
            for key, value in kwargs.iteritems():
                setattr(f, key, value)
            if position is None:
                list_.append(func_value)
            else:
                list_.insert(position, func_value)
            return f
    return decorate

