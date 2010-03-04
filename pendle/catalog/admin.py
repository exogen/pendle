from django.contrib import admin

from pendle.catalog.models import (ReservationDuration, FinePolicy,
                                   Requirements, Catalog, Period)
from pendle.catalog.forms import InlinePeriodForm
from pendle.utils import add
from pendle.utils.admin import related_list, count_link


class ReservationDurationAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    list_select_related = True

    @add(list_display)
    def default_for_catalogs(self, duration):
        return u", ".join(map(unicode, duration.catalogs.all()))

    @add(list_display)
    def used_by_categories(self, duration):
        return u", ".join(map(unicode, duration.categories.all()))


class FinePolicyAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', related_list(FinePolicy, 'categories')]
    list_select_related = True
    
    fieldsets = [(None, {'fields': ['per_day', 'per_period',
                                    'per_hour', 'flat_fee'],
                         'classes': ['wide']})]

class RequirementsAdmin(admin.ModelAdmin):
    filter_horizontal = ['departments', 'courses', 'training']


class PeriodInline(admin.TabularInline):
    model = Period
    form = InlinePeriodForm
    extra = 0


class CatalogAdmin(admin.ModelAdmin):
    list_display = ['name', 'online', count_link(Catalog, 'assets')]
    list_filter = ['online']
    inlines = [PeriodInline]
    fieldsets = [
        (None, {'fields': ['name', 'online']}),
        ("Policies", {'fields': ['default_reservation_duration',
                                 'default_fine_policy',
                                 'default_requirements'],
                      'classes': ['wide']}),
        ("Receipts", {'fields': ['receipt_prologue', 'receipt_epilogue',
                                 'receipt_signature'],
                      'classes': ['wide']})]


admin.site.register(ReservationDuration, ReservationDurationAdmin)
admin.site.register(FinePolicy, FinePolicyAdmin)
admin.site.register(Requirements, RequirementsAdmin)
admin.site.register(Catalog, CatalogAdmin)

