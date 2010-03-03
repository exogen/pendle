from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.utils.encoding import force_unicode
from django.utils.formats import number_format

from pendle.assets.models import (ProductType, PolicyCategory, Manufacturer,
                                  Product, Asset)
from pendle.utils import add
from pendle.utils.urls import admin_url
from pendle.utils.html import hyperlink, change_link, changelist_link
from pendle.utils.admin import value_or_empty, related_link, count_link


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    list_select_related = True

    @add(list_display, "URL", allow_tags=True, admin_order_field='url')
    def list_url(self, manufacturer):
        if manufacturer.url:
            return hyperlink(manufacturer.url, manufacturer.url,
                             {'class': 'external'}, target='_blank',
                             title="Open URL in a new window")
        else:
            return ""

    add(list_display)(value_or_empty(Manufacturer, 'phone_number'))
    add(list_display)(count_link(Manufacturer, 'products'))

    @add(list_display, "assets", allow_tags=True)
    def list_assets(self, manufacturer):
        assets = Asset.objects.filter(product__manufacturer=manufacturer)
        asset_count = assets.count()
        if asset_count:
            link = changelist_link(Asset, "",
                                   {'product__manufacturer': manufacturer},
                                   title="Find assets with this manufacturer")
            return '<p class="count">%s %s</p>' % (link,
                                                   number_format(asset_count))
        else:
            return ""


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', related_link(Product, 'manufacturer'),
                    related_link(Product, 'product_type'), 'model_name',
                    value_or_empty(Product, 'model_year'),
                    count_link(Product, 'assets')]
    list_display_links = ['__unicode__']
    list_filter = ['date_added', 'product_type']
    search_fields = ['title', 'manufacturer__name', 'description',
                     'model_name']
    ordering = ['-date_added']
    

class AssetAdmin(admin.ModelAdmin):
    list_display = ['barcode', related_link(Asset, 'product')]
    list_filter = ['catalog', 'date_added', 'policy_category', 'condition',
                   'new_barcode']
    list_select_related = True
    ordering = ['barcode']
    save_as = True
    save_on_top = True
    fieldsets = (
        (None, {'fields': ('catalog', 'product', 'barcode', 'bundle')}),
        ("Status", {'fields': ('condition', 'condition_details',
                               'staff_notes', 'new_barcode')}),
        ("Details", {'fields': ('serial_number', 'color',
                                'warranty_details')}),
        ("Policies", {
            'classes': ('collapse', 'wide'),
            'fields': ('policy_category', 'reservation_duration',
                       'fine_policy', 'requirements', 'reservable')}),
        ("Purchase information", {
            'classes': ('collapse', 'wide'),
            'fields': ('purchase_date', 'purchase_vendor',
                       'purchase_order')}))
    product_text_length = 75

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


admin.site.register(ProductType)
admin.site.register(PolicyCategory)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Asset, AssetAdmin)
