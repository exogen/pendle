from django.utils.encoding import force_unicode

from pendle.utils.html import change_link, changelist_link

def value_or_empty(model, attr):
    field, model_, direct, m2m = model._meta.get_field_by_name(attr)
    def column(obj):
        value = attr.__get__(obj)
        if value is not None:
            return force_unicode(value)
        else:
            return ""
    column.short_description = force_unicode(field.verbose_name)
    return column

def related_link(model, attr, **kwargs):
    field, model_, direct, m2m = model._meta.get_field_by_name(attr)
    print model, attr, field, direct, m2m
    def column(obj):
        related_obj = getattr(obj, attr)
        if related_obj is not None:
            return "%s %s" % (change_link(related_obj), related_obj)
        else:
            return ""
    column.allow_tags = True
    column.short_description = force_unicode(field.verbose_name)
    for key, value in kwargs.items():
        setattr(column, key, value)
    return column

def count_link(model, attr, **kwargs):
    field, model_, direct, m2m = model._meta.get_field_by_name(attr)
    print model, attr, field, direct, m2m
    def column(obj):
        if model is related.parent_model:
            related_model = related.model
            accessor = field.name
        else:
            related_model = related.parent_model
            accessor = related.get_accessor_name()
        query = {accessor: obj}
        count = getattr(obj, attr).filter(**query).count()
        if count:
            link = changelist_link(related_model, "", query)
            return '<p class="count">%s %s</p>' % (link, count)
        else:
            return ""
    column.allow_tags = True
    column.short_description = force_unicode(field.verbose_name)
    for key, value in kwargs.items():
        setattr(column, key, value)
    return column

