# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.db.models import permalink, Q
from django.db.models.query import QuerySet
from django.contrib.auth.models import User

from pendle.catalog.models import FinePolicy, ReservationDuration, \
                                  Requirements, Catalog
from pendle.utils.text import truncate


class ProductType(models.Model):
    name = models.CharField(max_length=75, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('admin:assets_producttype_change', [self.pk])

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

    @permalink
    def get_absolute_url(self):
        return ('admin:assets_policycategory_change', [self.pk])

class Manufacturer(models.Model):
    name = models.CharField(max_length=75, unique=True)
    url = models.URLField("URL", verify_exists=False, null=True, blank=True)
    phone_number = models.CharField(max_length=24, null=True, blank=True)
    staff_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('admin:assets_manufacturer_change', [self.pk])

    @property
    def assets(self):
        return Asset.objects.filter(product__manufacturer=self)

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

    @permalink
    def get_absolute_url(self):
        return ('admin:assets_product_change', [self.pk])

class AssetManager(models.Manager):
    def checked_out(self, *args, **kwargs):
        kwargs.update(reservations__transaction_out__isnull=False,
                      reservations__transaction_in__isnull=True)
        return self.filter(*args, **kwargs).distinct()
    
    def checked_in(self, *args, **kwargs):
        return self.filter(
            Q(reservations__isnull=True) |
            ~Q(reservations__transaction_in__isnull=True),
            *args, **kwargs).distinct()

    def overdue(self, now=None, *args, **kwargs):
        if now is None:
            now = datetime.now()
        kwargs.update(reservations__due_date__lt=now)
        return self.checked_out(*args, **kwargs)

    def available(self, *args, **kwargs):
        kwargs.update(reservable=True, catalog__online=True)
        return self.checked_in(*args, **kwargs)

    def unavailable(self, *args, **kwargs):
        checked_out = Q(reservations__transaction_out__isnull=False,
                        reservations__transaction_in__isnull=True)
        offline = Q(catalog__online=False)
        unreservable = Q(reservable=False)
        return self.filter(checked_out | offline | unreservable, *args,
            **kwargs).distinct()

class Asset(models.Model):
    CONDITION_CHOICES = (('unopened', "Unopened"),
                         ('like_new', "Like new"),
                         ('worn', "Worn"),
                         ('unreliable', "Unreliable"),
                         ('needs_service', "Needs service"),
                         ('destroyed', "Destroyed"))
    catalog = models.ForeignKey(Catalog, related_name='assets',
                                default=Catalog.objects.get_or_default)
    product = models.ForeignKey(Product, related_name='assets')
    bundle = models.ForeignKey('self', null=True, blank=True,
        related_name='bundled_assets',
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

    objects = AssetManager()

    class Meta:
        unique_together = [('catalog', 'barcode')]
        ordering = ['catalog', 'product', 'barcode']
        get_latest_by = 'date_added'

    def __unicode__(self):
        return self.barcode

    @permalink
    def get_absolute_url(self):
        return ('admin:assets_asset_change', [self.pk])

    def get_reservation_duration(self):
        if self.reservation_duration:
            return self.reservation_duration
        elif self.policy_category and self.policy_category.reservation_duration:
            return self.policy_category.reservation_duration
        else:
            return self.catalog.default_reservation_duration

    def get_fine_policy(self):
        if self.fine_policy:
            return self.fine_policy
        elif self.policy_category and self.policy_category.fine_policy:
            return self.policy_category.fine_policy
        else:
            return self.catalog.default_fine_policy

    def is_checked_out(self):
        return self.__class__.objects.checked_out(pk=self.pk).exists()
    is_checked_out.boolean = True
    is_checked_out.short_description = "checked out?"

    def is_overdue(self):
        return self.__class__.objects.overdue(pk=self.pk).exists()
    is_overdue.boolean = True
    is_overdue.short_description = "overdue?"

    def is_available(self):
        return self.__class__.objects.available(pk=self.pk).exists()
    is_available.boolean = True
    is_available.short_description = "available?"
    
    def get_current_customer(self):
        try:
            return User.objects.get(
                transactions__reservations_out__asset=self,
                transactions__reservations_out__transaction_in__isnull=True)
        except User.DoesNotExist:
            return None
    get_current_customer.short_description = u"checked out by…"

    def get_current_reservation(self):
        try:
            return self.reservations.get(transaction_in__isnull=True)
        except self.reservations.model.DoesNotExist:
            return None

