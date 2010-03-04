from django.utils.encoding import force_unicode
from django.utils.formats import number_format

from pendle.utils.html import change_link, changelist_link


def value_or_empty(model, attr):
    field, model_, direct, m2m = model._meta.get_field_by_name(attr)
    def column(obj):
        value = getattr(obj, attr)
        if value is not None:
            return force_unicode(value)
        else:
            return ""
    column.short_description = force_unicode(field.verbose_name)
    column.admin_order_field = attr
    return column

def related_list(model, attr, short_description=None, **kwargs):
    field, model_, direct, m2m = model._meta.get_field_by_name(attr)
    if m2m and direct:
        related = field.related
    else:
        field, related = field.field, field
    def column(obj):
        query_set = getattr(obj, attr).all()
        return ", ".join(map(force_unicode, query_set))
    column.allow_tags = True
    if short_description is None:
        short_description = field.verbose_name if direct else attr
    column.short_description = force_unicode(short_description)
    for key, value in kwargs.items():
        setattr(column, key, value)
    return column

def related_link(model, attr, **kwargs):
    field, model_, direct, m2m = model._meta.get_field_by_name(attr)
    def column(obj):
        related_obj = getattr(obj, attr)
        if related_obj is not None:
            return "%s %s" % (change_link(related_obj), related_obj)
        else:
            return ""
    column.allow_tags = True
    column.short_description = force_unicode(field.verbose_name)
    column.admin_order_field = field.name
    for key, value in kwargs.items():
        setattr(column, key, value)
    return column

def count_link(model, attr, short_description=None, **kwargs):
    field, model_, direct, m2m = model._meta.get_field_by_name(attr)
    if m2m and direct:
        related = field.related
    else:
        field, related = field.field, field
    def column(obj):
        if model is related.parent_model:
            related_model = related.model
            field_name = field.name
        else:
            related_model = related.parent_model
            field_name = related.get_accessor_name()
        query = {'%s__%s__exact' % (field_name,
                                    related_model._meta.pk.column): obj.pk}
        count = getattr(obj, attr).filter(**query).count()
        if count:
            if m2m:
                verbose_name = force_unicode(model._meta.verbose_name)
            else:
                verbose_name = force_unicode(field.verbose_name)
            title = "Find %s with this %s" % (
                force_unicode(related_model._meta.verbose_name_plural),
                verbose_name)
            link = changelist_link(related_model, "", query, title=title)
            return '<p class="count">%s %s</p>' % (link, number_format(count))
        else:
            return ""
    column.allow_tags = True
    if short_description is None:
        short_description = field.verbose_name if direct else attr
    column.short_description = force_unicode(short_description)
    for key, value in kwargs.items():
        setattr(column, key, value)
    return column

