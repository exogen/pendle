from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.formats import number_format
from django.utils.translation import ugettext as _
from adminbrowse import link_to_change
from adminbrowse.related import (ChangeLink, ChangeListLink,
                                 ChangeListTemplateColumn)

from pendle.reservations.models import Transaction, Reservation
from pendle.reservations.forms import TransactionForm
from pendle.assets.models import Asset
from pendle.catalog.models import Catalog
from pendle.utils import add
from pendle.utils.admin import PendleModelAdmin


class CheckinInline(admin.TabularInline):
    model = Reservation
    fk_name = 'transaction_in'
    verbose_name = "asset"
    verbose_name_plural = "checked in"
    extra = 0
    readonly_fields = ['asset', 'transaction_out', 'due_date']
    can_delete = False


class CheckoutInline(admin.TabularInline):
    model = Reservation
    fk_name = 'transaction_out'
    verbose_name = "asset"
    verbose_name_plural = "checked out"
    exclude = ['transaction_in']
    extra = 0


class TransactionAssetsLink(ChangeListLink):
    def __init__(self, model, name, short_description=None, text=len,
                 default="", template_name=None, extra_context=None):
        ChangeListTemplateColumn.__init__(self, short_description,
                                          template_name or self.template_name,
                                          extra_context)
        self.field_name = name
        self.to_model = Asset
        if name == 'assets_in':
            self.reverse_name = 'reservations__transaction_in'
        elif name == 'assets_out':
            self.reverse_name = 'reservations__transaction_out'
        else:
            raise ValueError(name)
        if self.short_description is None:
            self.short_description = name.replace('_', ' ')
        self.rel_name = 'id'
        self.text = text
        self.default = default

    def get_title(self, obj, value):
        if self.field_name == 'assets_in':
            return _("List assets checked in with this transaction")
        else:
            return _("List assets checked out with this transaction")


class TransactionAdmin(PendleModelAdmin):
    #form = TransactionForm
    inlines = [CheckinInline, CheckoutInline]
    list_display = ['__unicode__', 'timestamp',
                    link_to_change(Transaction, 'customer'),
                    link_to_change(Transaction, 'staff_member'),
                    TransactionAssetsLink(Transaction, 'assets_in'),
                    TransactionAssetsLink(Transaction, 'assets_out')]
    list_filter = ['timestamp', 'staff_member']
    date_hierarchy = 'timestamp'
    search_fields = ['customer__username', 'customer__first_name',
                     'customer__last_name']
    readonly_fields = ['timestamp']
    select_related_fields = ['customer', 'staff_member']
    fieldsets = [
        (None, {'fields': ['catalog', 'customer', 'staff_member',
                           'timestamp']}),
        ("Notes", {'fields': ['staff_notes'], 'classes': ['collapse']})]

    #@add(list_display, "assets in", allow_tags=True)
    def list_assets_in(self, transaction):
        query = {'reservations__transaction_in': transaction}
        assets = Asset.objects.filter(**query)
        asset_count = assets.count()
        if asset_count:
            link = changelist_link(Asset, "", query,
                title="Find assets checked in during this transaction")
            return '<p class="count">%s %s</p>' % (link,
                                                   number_format(asset_count))
        else:
            return ""

    #@add(list_display, "assets out", allow_tags=True)
    def list_assets_out(self, transaction):
        query = {'reservations__transaction_out': transaction}
        assets = Asset.objects.filter(**query)
        asset_count = assets.count()
        if asset_count:
            link = changelist_link(Asset, "", query,
                title="Find assets checked out during this transaction")
            return '<p class="count">%s %s</p>' % (link,
                                                   number_format(asset_count))
        else:
            return ""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'catalog':
            kwargs['initial'] = Catalog.objects.get_or_default()
        elif db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(TransactionAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.staff_member = request.user
        super(TransactionAdmin, self).save_model(request, obj, form, change)

    class Media:
        css = {'all': ('adminbrowse/css/adminbrowse.css',)}

class ReservationCustomerLink(ChangeLink):
    def __init__(self, *args, **kwargs):
        super(ReservationCustomerLink, self).__init__(*args, **kwargs)
        self.admin_order_field = 'transaction_out__customer__last_name'

    def __call__(self, obj):
        obj = obj.transaction_out
        return super(ReservationCustomerLink, self).__call__(obj)

class ReservationAdmin(PendleModelAdmin):
    list_display = ['__unicode__', 'asset',
                    ReservationCustomerLink(Transaction, 'customer'),
                    link_to_change(Reservation, 'transaction_out'),
                    link_to_change(Reservation, 'transaction_in'), 'due_date',
                    'is_on_time']
    list_filter = ['due_date']
    ordering = ['transaction_out']
    search_fields = ['asset__barcode', 'asset__product__title',
                     'transaction_out__customer__username',
                     'transaction_out__customer__first_name',
                     'transaction_out__customer__last_name']
    fieldsets = [
        (None, {'fields': ['asset', 'transaction_out', 'transaction_in',
                           'due_date'],
                'classes': ['wide']})]

    class Media:
        css = {'all': ('adminbrowse/css/adminbrowse.css',)}

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Reservation, ReservationAdmin)

