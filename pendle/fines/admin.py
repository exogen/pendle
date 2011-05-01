from django.contrib import admin
from django.db import models
from adminbrowse import link_to_change
from autocomplete.views import autocomplete, AutocompleteSettings
from autocomplete.admin import AutocompleteAdmin

from pendle.fines.models import Fine, FinePayment
from pendle.fines.widgets import DollarsInput
from pendle.utils.text import format_dollars
from pendle.utils.admin import PendleModelAdmin


class CustomerAutocomplete(AutocompleteSettings):
    limit = 15
    search_fields = ('^username', '^first_name', '^last_name', '^profile__id_number')

class FineAdmin(AutocompleteAdmin, PendleModelAdmin):
    formfield_overrides = {
        models.DecimalField: {'widget': DollarsInput, 'localize': True}}
    list_display = ['amount_dollars', link_to_change(Fine, 'customer'),
                    'date_issued']
    list_filter = ['date_issued']
    select_related_fields = ['customer']

    def amount_dollars(self, obj):
        return format_dollars(obj.amount)
    amount_dollars.short_description = "amount"
    amount_dollars.admin_order_field = 'amount'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(FineAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

class FinePaymentAdmin(AutocompleteAdmin, PendleModelAdmin):
    formfield_overrides = {
        models.DecimalField: {'widget': DollarsInput, 'localize': True}}
    list_display = ['amount_dollars', link_to_change(FinePayment, 'customer'),
                    'date_received']
    list_filter = ['date_received']
    select_related_fields = ['customer']

    def amount_dollars(self, obj):
        return format_dollars(obj.amount)
    amount_dollars.short_description = "amount"
    amount_dollars.admin_order_field = 'amount'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(FinePaymentAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


admin.site.register(Fine, FineAdmin)
admin.site.register(FinePayment, FinePaymentAdmin)
autocomplete.register(Fine.customer, CustomerAutocomplete)
autocomplete.register(FinePayment.customer, CustomerAutocomplete)
