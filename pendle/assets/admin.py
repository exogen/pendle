from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.utils.encoding import force_unicode

from pendle.assets.models import (ProductType, PolicyCategory, Manufacturer,
                                  Product, Asset)
from pendle.utils import add
from pendle.utils.urls import admin_url
from pendle.utils.html import hyperlink, related_link


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    list_select_related = True

    @add(list_display, "phone number", admin_order_field='phone_number')
    def list_phone_number(self, manufacturer):
        return manufacturer.phone_number or ""
    
    @add(list_display, "URL", allow_tags=True, admin_order_field='url')
    def list_url(self, manufacturer):
        if manufacturer.url:
            return hyperlink(manufacturer.url, manufacturer.url,
                             target='_blank', title="Open URL in a new window",
                             **{'class': 'external'})
        else:
            return ""

    @add(list_display, "products", allow_tags=True)
    def list_products(self, manufacturer):
        product_count = manufacturer.products.count()
        if product_count:        
            url = admin_url('changelist', Product, manufacturer=manufacturer)
            link = hyperlink(url, "", title="Browse products", **{'class': 'related-link'})
            return '<p class="related">%s %s</p>' % (link, product_count)
        else:
            return ""

    @add(list_display, "assets", allow_tags=True)
    def list_assets(self, manufacturer):
        asset_count = Asset.objects.filter(product__manufacturer=manufacturer).count()
        if asset_count:
            url = admin_url('changelist', Asset,
                            product__manufacturer=manufacturer)
            link = hyperlink(url, "", title="Browse assets", **{'class': 'related-link'})
            return '<p class="related">%s %s</p>' % (link, asset_count)
        else:
            return ""


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    list_display_links = ['__unicode__']
    list_filter = ['date_added', 'product_type']
    search_fields = ['title', 'manufacturer__name', 'description',
                     'model_name']
    ordering = ['-date_added']
    
    @add(list_display, "manufacturer", allow_tags=True,
         admin_order_field='manufacturer__name')
    def list_manufacturer(self, product):
        if product.manufacturer:
            return "%s %s" % (related_link(product.manufacturer),
                              product.manufacturer)
        else:
            return ""

    @add(list_display, "product type", allow_tags=True,
         admin_order_field='product_type__name')
    def list_product_type(self, product):
        return product.product_type or ""

    @add(list_display, "model", admin_order_field='model_name')
    def list_model_name(self, product):
        return product.model_name

    @add(list_display, "model year", admin_order_field='model_year')
    def list_model_year(self, product):
        return product.model_year or ""

    @add(list_display, "assets", allow_tags=True)
    def list_assets(self, product):
        asset_count = product.assets.count()
        if asset_count:        
            url = admin_url('changelist', Asset, product=product)
            link = hyperlink(url, "", title="Browse assets", **{'class': 'related-link'})
            return '<p class="related">%s %s</p>' % (asset_count, link)
        else:
            return ""


class AssetAdmin(admin.ModelAdmin):
    list_display = ['barcode']
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

    @add(list_display, "product", allow_tags=True,
         admin_order_field='product__title')
    def list_product(self, asset):
        product_text = force_unicode(asset.product)
        if len(product_text) > self.product_text_length:
            product_text = product_text[:self.product_text_length] + '&hellip;'
        return "%s %s" % (related_link(asset.product), product_text)

    @add(list_display, "catalog", allow_tags=True,
         admin_order_field='catalog__name')
    def list_catalog(self, asset):
        return "%s %s" % (related_link(asset.catalog), asset.catalog)

    @add(list_display, "bundle", allow_tags=True,
         admin_order_field='bundle__barcode')
    def list_bundle(self, asset):
        bundled_assets = Asset.objects.filter(bundle=asset).count()
        if bundled_assets:
            text = "%d bundled" % bundled_assets
            icon = _boolean_icon(True)
            value = '<p class="related bundle">%s %s</p>' % (text, icon)
        elif asset.bundle:
            link = related_link(asset.bundle)
            value = '<p class="related">%s %s</p>' % (link, asset.bundle)
        else:
            value = ""
        return value


admin.site.register(ProductType)
admin.site.register(PolicyCategory)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Asset, AssetAdmin)
