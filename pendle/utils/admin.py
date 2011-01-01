from django.contrib import admin
from adminbrowse import ChangeListModelFieldColumn, AutoBrowseModelAdmin

from pendle.utils.text import format_dollars

class PendleModelAdmin(AutoBrowseModelAdmin):
    select_related_fields = ()
    select_related_depth = None

    def queryset(self, request):
        queryset = super(PendleModelAdmin, self).queryset(request)
        if self.select_related_fields:
            return queryset.select_related(*self.select_related_fields)
        elif self.select_related_depth is not None:
            return queryset.select_related(depth=self.select_related_depth)
        else:
            return queryset

class DollarAmountColumn(ChangeListModelFieldColumn):
    def __call__(self, obj):
        value = getattr(obj, self.field_name)
        if value is not None:
            return format_dollars(value)
        else:
            return default

dollars_field = DollarAmountColumn

