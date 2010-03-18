from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django import forms
from django.utils.encoding import force_unicode
from django.utils.formats import number_format

from listinline import ListInline

from pendle.assets.models import (ProductType, PolicyCategory, Manufacturer,
                                  Product, Asset)
from pendle.utils import add
from pendle.utils.urls import admin_url
from pendle.utils.html import hyperlink, change_link, changelist_link
from pendle.utils.admin import field_value, related_link, count_link
from pendle.utils.text import truncate


class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', count_link(ProductType, 'products')]

    @add(list_display, "assets", allow_tags=True)
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

class PolicyCategoryAdmin(admin.ModelAdmin):
    list_display = ['__unicode__',
                    field_value(PolicyCategory, 'fine_policy'),
                    field_value(PolicyCategory, 'reservation_duration'),
                    field_value(PolicyCategory, 'requirements'),
                    count_link(PolicyCategory, 'assets')]


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    list_select_related = True
    search_fields = ['name', 'url']

    @add(list_display, "URL", allow_tags=True, admin_order_field='url')
    def list_url(self, manufacturer):
        if manufacturer.url:
            return hyperlink(manufacturer.url, manufacturer.url,
                             {'class': 'external'}, target='_blank',
                             title="Open URL in a new window")
        else:
            return ""

    add(list_display)(field_value(Manufacturer, 'phone_number'))
    add(list_display)(count_link(Manufacturer, 'products'))

    @add(list_display, "assets", allow_tags=True)
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


class ProductAdmin(admin.ModelAdmin):
    inlines = [AssetInline]
    list_display = [related_link(Product, 'manufacturer'),
                    related_link(Product, 'product_type'), 'model_name',
                    field_value(Product, 'model_year'),
                    count_link(Product, 'assets')]
    list_filter = ['date_added', 'product_type']
    search_fields = ['title', 'manufacturer__name', 'description',
                     'model_name']
    ordering = ['-date_added']
    fieldsets = [(None, {'fields': ['manufacturer', 'product_type',
                                    'title', 'description',
                                    ('model_name', 'model_year')]})]
    
    @add(list_display, "product", 0, allow_tags=True)
    def list_product(self, product):
        return truncate(product, 60)


class BundledInline(ListInline):
    model = Asset
    fields = ['product', 'bundle_order']
    readonly_fields = ['product']
    ordering = ['bundle_order']
    verbose_name = "asset"
    verbose_name_plural = "bundled assets"
    can_remove = True
    extra = 0


class AssetAdmin(admin.ModelAdmin):
    inlines = [BundledInline]
    list_display = ['barcode', related_link(Asset, 'product')]
    list_filter = ['catalog', 'date_added', 'policy_category', 'condition',
                   'new_barcode']
    list_select_related = True
    search_fields = ['barcode', 'product__manufacturer__name',
                     'product__title', 'product__description',
                     'product__model_name', 'product__model_year']
    ordering = ['barcode']
    save_as = True
    save_on_top = True
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

    @add(list_display, "bundle", allow_tags=True,
         admin_order_field='bundle__barcode')
    def list_bundle(self, asset):
        bundled_assets = Asset.objects.filter(bundle=asset).count()
        if bundled_assets:
            text = "%s bundled" % number_format(bundled_assets)
            link = changelist_link(Asset, "", {'bundle': asset},
                                   title="Find bundled assets")
            value = '<p class="bundled">%s %s</p>' % (link, text)
        elif asset.bundle:
            link = change_link(asset.bundle, title="Go to bundle")
            value = '<p class="bundle">%s %s</p>' % (link, asset.bundle)
        else:
            value = ""
        return value


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(PolicyCategory, PolicyCategoryAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Asset, AssetAdmin)
