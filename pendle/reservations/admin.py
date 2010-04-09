from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.formats import number_format

from pendle.reservations.models import Transaction, Reservation
from pendle.reservations.forms import TransactionForm
from pendle.assets.models import Asset
from pendle.catalog.models import Catalog
from pendle.utils import add
from pendle.utils.html import change_link, changelist_link
from pendle.utils.admin import related_link, count_link


class CheckinInline(admin.TabularInline):
    model = Reservation
    fk_name = 'transaction_in'
    verbose_name = "asset"
    verbose_name_plural = "checked in"
    extra = 0


class CheckoutInline(CheckinInline):
    fk_name = 'transaction_out'
    verbose_name = "asset"
    verbose_name_plural = "checked out"
    exclude = ['transaction_in']


class TransactionAdmin(admin.ModelAdmin):
    #form = TransactionForm
    inlines = [CheckoutInline]
    list_display = ['__unicode__',
                    related_link(Transaction, 'customer',
                                 admin_order_field='customer__last_name'),
                    related_link(Transaction, 'staff_member',
                                 admin_order_field='staff_member__last_name'),
                    'timestamp']
    list_filter = ['timestamp', 'staff_member']
    date_hierarchy = 'timestamp'
    search_fields = ['customer__username', 'customer__first_name',
                     'customer__last_name']
    readonly_fields = ['staff_member', 'timestamp']
    fieldsets = [
        (None, {'fields': ['catalog', 'customer', 'staff_member',
                           'timestamp']}),
        ("Notes", {'fields': ['staff_notes'], 'classes': ['collapse']})]

    @add(list_display, "assets in", allow_tags=True)
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

    @add(list_display, "assets out", allow_tags=True)
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
        return super(TransactionAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def render_change_form(self, request, context, add=False, *args, **kwargs):
        if add:
            context['adminform'].form.instance.staff_member = request.user
        return super(TransactionAdmin, self).render_change_form(
            request, context, add, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.staff_member = request.user
        obj.save()


class ReservationAdmin(admin.ModelAdmin):
    list_display = ['asset', related_link(Reservation, 'transaction_out'),
                    related_link(Reservation, 'transaction_in'), 'due_date']
    list_filter = ['due_date']
    search_fields = ['asset__barcode', 'asset__product__title',
                     'transaction_out__customer__username',
                     'transaction_out__customer__first_name',
                     'transaction_out__customer__last_name']
    fieldsets = [
        (None, {'fields': ['asset', 'transaction_out', 'transaction_in',
                           'due_date'],
                'classes': ['wide']})]

    @add(list_display, "customer", 1, allow_tags=True,
         admin_order_field='transaction_out__customer')
    def list_customer(self, reservation):
        return related_link(Transaction, 'customer')(reservation.transaction_out)

    @add(list_display, "on time", boolean=True)
    def list_on_time(self, reservation):
        if reservation.transaction_in:
            return_time = reservation.transaction_in.timestamp
            if reservation.due_date:
                return reservation.due_date >= return_time
        elif reservation.due_date:
            if reservation.due_date < datetime.now():
                return False
        return True

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Reservation, ReservationAdmin)
