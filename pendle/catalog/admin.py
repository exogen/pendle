from django.contrib import admin
from adminbrowse import related_list, link_to_changelist

from pendle.catalog.models import (ReservationDuration, FinePolicy,
                                   Requirements, Catalog, Period)
from pendle.catalog.forms import InlinePeriodForm
from pendle.utils import add
from pendle.utils.admin import PendleModelAdmin


class ReservationDurationAdmin(admin.ModelAdmin):
    list_display = ['__unicode__',
                    related_list(ReservationDuration, 'catalogs'),
                    related_list(ReservationDuration, 'categories')]

class FinePolicyAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', related_list(FinePolicy, 'categories')]
    fieldsets = [(None, {'fields': ['per_day', 'per_period',
                                    'per_hour', 'flat_fee'],
                         'classes': ['wide']})]

class RequirementsAdmin(admin.ModelAdmin):
    filter_horizontal = ['departments', 'courses', 'training']

class PeriodInline(admin.TabularInline):
    model = Period
    form = InlinePeriodForm
    extra = 0

class CatalogAdmin(PendleModelAdmin):
    list_display = ['name', 'online', link_to_changelist(Catalog, 'assets')]
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

