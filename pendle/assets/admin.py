# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.utils.encoding import force_unicode, smart_unicode
from django.utils.formats import number_format
from django.db import models

from listinline import ListInline
from adminbrowse import (ChangeListColumn, ChangeListTemplateColumn,
                         link_to_change, link_to_changelist, template_column)
from autocomplete.views import autocomplete, AutocompleteSettings
from autocomplete.admin import AutocompleteAdmin

from pendle.assets.models import (ProductType, PolicyCategory, Manufacturer,
                                  Product, Asset)
from pendle.utils import add
from pendle.utils.admin import PendleModelAdmin


class ProductAutocomplete(AutocompleteSettings):
    search_fields = ('title', '^manufacturer__name')

class AssetAutocomplete(AutocompleteSettings):
    search_fields = ('^barcode',)
    limit = 15

class BundleColumn(ChangeListColumn):
    allow_tags = True
    bundle_link = link_to_change(Asset, 'bundle')
    bundled_link = link_to_changelist(Asset, 'bundled_assets',
        text=lambda bundled: "%d bundled" % len(bundled))

    def __init__(self, short_description, default=""):
        ChangeListColumn.__init__(self, short_description, 'bundle__barcode')
        self.default = default

    def __call__(self, obj):
        if obj.bundle:
            return self.bundle_link(obj)
        elif obj.bundled_assets.all():
            return self.bundled_link(obj)
        else:
            return self.default

class AvailabilityColumn(ChangeListTemplateColumn):
    template_name = "assets/includes/availability.html"

    def get_context(self, obj):
        context = super(AvailabilityColumn, self).get_context(obj)
        available = obj.reservable and obj.catalog.online
        reservation = obj.get_current_reservation()
        if reservation is None:
            current_customer = None
        else:
            available = False
            current_customer = reservation.transaction_out.customer
        context.update({'asset': obj,
                        'available': available,
                        'reservation': reservation,
                        'current_customer': current_customer})
        return context

class ProductTypeAdmin(PendleModelAdmin):
    list_display = ['__unicode__',
                    link_to_changelist(ProductType, 'products')]

    #@add(list_display, "assets", allow_tags=True)
    def list_assets(self, product_type):
        query = {'product__product_type': product_type}
        assets = Asset.objects.filter(**query)
        asset_count = assets.count()
        if asset_count:
            link = changelist_link(Asset, "", query,
                                   title="Find assets with this product type")
            return '<p class="count">%s %s</p>' % (link,
                                                   number_format(asset_count))
        else:
            return ""

class PolicyCategoryAdmin(PendleModelAdmin):
    list_display = ['__unicode__', 'fine_policy', 'reservation_duration',
                    'requirements', link_to_changelist(PolicyCategory,
                                                       'assets')]

class ManufacturerAdmin(PendleModelAdmin):
    list_display = ['name', 'phone_number', link_to_changelist(Manufacturer,
                                                               'products')]
    search_fields = ['name', 'url']

    #@add(list_display, "assets", allow_tags=True)
    def list_assets(self, manufacturer):
        query = {'product__manufacturer': manufacturer}
        assets = Asset.objects.filter(**query)
        asset_count = assets.count()
        if asset_count:
            link = changelist_link(Asset, "", query,
                                   title="Find assets with this manufacturer")
            return '<p class="count">%s %s</p>' % (link,
                                                   number_format(asset_count))
        else:
            return ""

class AssetInline(admin.TabularInline):
    model = Asset
    fields = ['barcode', 'condition', 'purchase_date', 'catalog']
    extra = 0

class ProductAdmin(PendleModelAdmin):
    inlines = [AssetInline]
    list_display = ['title', 'manufacturer', 'product_type', 'model_name',
                    'model_year', link_to_changelist(Product, 'assets')]
    list_filter = ['date_added', 'product_type']
    search_fields = ['title', 'manufacturer__name', 'description',
                     'model_name']
    ordering = ['-date_added']
    select_related_fields = ['manufacturer', 'product_type']
    fieldsets = [(None, {'fields': ['manufacturer', 'product_type',
                                    'title', 'description',
                                    ('model_name', 'model_year')]})]

class BundledInline(ListInline):
    model = Asset
    fields = ['product', 'bundle_order']
    readonly_fields = ['product']
    ordering = ['bundle_order']
    verbose_name = "asset"
    verbose_name_plural = "bundled assets"
    can_remove = True
    extra = 0

class AssetAdmin(AutocompleteAdmin, PendleModelAdmin):
    inlines = [BundledInline]
    list_display = ['barcode', 'product', BundleColumn("bundle"),
                    AvailabilityColumn("available?")]
    list_filter = ['catalog', 'date_added', 'policy_category', 'condition',
                   'new_barcode']
    search_fields = ['barcode', 'product__manufacturer__name',
                     'product__title', 'product__description',
                     'product__model_name', 'product__model_year']
    ordering = ['barcode']
    select_related_fields = ['catalog', 'product', 'bundle']
    save_as = True
    fieldsets = [
        (None, {'fields': ('catalog', 'product', ('barcode', 'new_barcode'),
                           'bundle')}),
        ("Status", {'fields': ('condition', 'condition_details',
                               'staff_notes')}),
        ("Details", {'fields': ('serial_number', 'color')}),
        ("Purchase information", {
            'classes': ('collapse', 'wide'),
            'fields': ('purchase_date', 'purchase_vendor',
                       'purchase_order', 'warranty_details')}),
        ("Policies", {
            'classes': ('collapse', 'wide'),
            'fields': ('policy_category', 'reservation_duration',
                       'fine_policy', 'requirements', 'reservable')})]

admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(PolicyCategory, PolicyCategoryAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Asset, AssetAdmin)
autocomplete.register(Asset.bundle, AssetAutocomplete)
