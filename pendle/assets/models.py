from datetime import datetime

from django.db import models

from pendle.catalog.models import (FinePolicy, ReservationDuration,
                                   Requirements, Catalog)
from pendle.utils.text import truncate


class ProductType(models.Model):
    name = models.CharField(max_length=75, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class PolicyCategory(models.Model):
    name = models.CharField(max_length=75, unique=True)
    fine_policy = models.ForeignKey(FinePolicy, null=True, blank=True,
        related_name='categories',
        help_text="Determines how late fees are calculated for assets in "
                  "this category, if not specified by the asset")
    reservation_duration = models.ForeignKey(ReservationDuration, null=True,
        blank=True, related_name='categories',
        help_text="Determines when assets in this category are due, if not "
                  "specified by the asset")
    requirements = models.ForeignKey(Requirements, null=True, blank=True,
        related_name='categories',
        help_text="Determines who is allowed to reserve assets in this "
                  "category, if not specified by the asset")

    class Meta:
        ordering = ['name']
        verbose_name_plural = "policy categories"

    def __unicode__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=75, unique=True)
    url = models.URLField("URL", verify_exists=False, null=True, blank=True)
    phone_number = models.CharField(max_length=24, null=True, blank=True)
    staff_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name


class Product(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, null=True, blank=True,
                                     related_name='products')
    product_type = models.ForeignKey(ProductType, verbose_name="type",
        null=True, blank=True, related_name='products',
        help_text="Categorize this product to group it with like items and "
                  "enable additional fields.")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    model_name = models.CharField("model", max_length=200, blank=True)
    model_year = models.PositiveSmallIntegerField(null=True, blank=True)
    legacy_id = models.IntegerField("legacy ID", null=True, blank=True,
                                    editable=False)
    date_added = models.DateTimeField(default=datetime.now, editable=False)
    #pictures = generic.GenericRelation(Picture, related_name='products')
    #attachments = generic.GenericRelation(Attachment, related_name='products')

    class Meta:
        unique_together = [('manufacturer', 'title', 'model_name',
                            'model_year')]
        ordering = ['manufacturer', 'title']
    
    def __unicode__(self):
        return truncate(self.title, 75)


class Asset(models.Model):
    CONDITION_CHOICES = (('unopened', "Unopened"),
                         ('like_new', "Like new"),
                         ('worn', "Worn"),
                         ('unreliable', "Unreliable"),
                         ('needs_service', "Needs service"),
                         ('destroyed', "Destroyed"))
    catalog = models.ForeignKey(Catalog, related_name='assets', default=1)
    product = models.ForeignKey(Product, related_name='assets')
    bundle = models.ForeignKey('self', null=True, blank=True,
        related_name='bundle_assets',
        help_text="The bundle in which this asset is included.")
    bundle_order = models.IntegerField(blank=True, null=True)
    barcode = models.CharField(max_length=75)
    new_barcode = models.BooleanField("needs new barcode printed",
                                      default=True)
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES,
        default='like_new',
        help_text="Select the closest description of the asset's condition.")
    condition_details = models.TextField(blank=True)
    #pictures = generic.GenericRelation(Picture, related_name='assets')
    #attachments = generic.GenericRelation(Attachment, related_name='assets')
    serial_number = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=20, blank=True)
    date_added = models.DateTimeField(default=datetime.now, editable=False)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_vendor = models.CharField(max_length=200, blank=True,
        help_text="The name or URL of the supplier.")
    purchase_order = models.CharField("purchase order number", max_length=200,
                                      blank=True)
    warranty_details = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)
    policy_category = models.ForeignKey(PolicyCategory, null=True,
        blank=True, related_name='assets',
        help_text="Use this to apply policies to a group of assets.")
    reservation_duration = models.ForeignKey(ReservationDuration, null=True,
        blank=True, related_name='assets',
        help_text="Determines when a reservation is due.<br/>Leave blank to "
                  "use the policy category or catalog default.")
    fine_policy = models.ForeignKey(FinePolicy, null=True, blank=True,
        related_name='assets',
        help_text="Determines how late fees are calculated.<br/>Leave blank "
                  "to use the policy category or catalog default.")
    requirements = models.ForeignKey(Requirements, null=True, blank=True,
        related_name='assets',
        help_text="Determines who is allowed to reserve this asset.<br/>Lea"
                  "ve blank to use the policy category or catalog default.")
    reservable = models.BooleanField(default=True,
        help_text="Uncheck to make this asset unavailable.")

    #objects = QuerySetManager()

    class Meta:
        unique_together = [('catalog', 'barcode')]
        ordering = ['catalog', 'product', 'barcode']
        get_latest_by = 'date_added'

    def __unicode__(self):
        return self.barcode

    @models.permalink
    def get_absolute_url(self):
        return ('admin:assets_asset_change', [self.id])

