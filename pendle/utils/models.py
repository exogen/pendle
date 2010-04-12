from django.db.models import Q


def search_filter(field_name):
    if field_name.startswith('^'):
        return '%s__istartswith' % field_name[1:]
    elif field_name.startswith('='):
        return '%s__iexact' % field_name[1:]
    elif field_name.startswith('@'):
        return '%s__search' % field_name[1:]
    else:
        return '%s__icontains' % field_name

def search_query(terms, fields):
    if isinstance(terms, basestring):
        terms = terms.split()
    if isinstance(fields, basestring):
        fields = [fields]
    
    query = Q()
    for term in terms:
        term_query = Q()
        for field in fields:
            term_query |= Q(**{search_filter(field): term})
        query &= term_query
    return query

