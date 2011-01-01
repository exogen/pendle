from datetime import datetime

from django.db import models
from django.db.models import permalink, Q
from django.contrib.auth.models import User

from pendle.catalog.models import Catalog
from pendle.assets.models import Asset


class Transaction(models.Model):
    catalog = models.ForeignKey(Catalog, related_name='transactions')
    token = models.CharField(max_length=24, null=True, blank=True,
                             editable=False)
    staff_member = models.ForeignKey(User, related_name='staff_transactions',
                                     limit_choices_to={'is_staff': True})
    customer = models.ForeignKey(User, related_name='transactions')
    timestamp = models.DateTimeField(default=datetime.now)
    staff_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return u"Transaction #%d" % self.pk

    @permalink
    def get_absolute_url(self):
        return ('admin:reservations_transaction_change', [self.pk])

    @property
    def assets(self):
        out = Q(reservations__transaction_out=self)
        in_ = Q(reservations__transaction_in=self)
        return Asset.objects.filter(out | in_).distinct()

    @property
    def assets_out(self):
        return Asset.objects.filter(reservations__transaction_out=self)

    @property
    def assets_in(self):
        return Asset.objects.filter(reservations__transaction_in=self)

class ReservationManager(models.Manager):
    def checked_out(self, *args, **kwargs):
        kwargs.update(transaction_in__isnull=True)
        return self.filter(*args, **kwargs)

    def checked_in(self, *args, **kwargs):
        kwargs.update(transaction_in__isnull=False)
        return self.filter(*args, **kwargs)

    def overdue(self, now=None, *args, **kwargs):
        if now is None:
            now = datetime.now()
        kwargs.update(due_date__lt=now)
        return self.checked_out(*args, **kwargs)

class Reservation(models.Model):
    asset = models.ForeignKey(Asset, related_name='reservations')
    transaction_out = models.ForeignKey(Transaction,
        verbose_name="checkout transaction", related_name='reservations_out',
        help_text="The transaction in which this asset was checked out.")
    transaction_in = models.ForeignKey(Transaction, null=True, blank=True,
        verbose_name="checkin transaction", related_name='reservations_in',
        help_text="The transaction in which this asset was returned.")
    due_date = models.DateTimeField(null=True, blank=True)

    objects = ReservationManager()

    class Meta:
        unique_together = [('asset', 'transaction_out'),
                           ('asset', 'transaction_in')]
        ordering = ['-transaction_out', 'asset']

    def __unicode__(self):
        return u"%s in %s" % (self.asset, self.transaction_out)

    @permalink
    def get_absolute_url(self):
        return ('admin:reservations_reservation_change', [self.pk])

    def is_on_time(self, now=None):
        if self.due_date:
            if now is None:
                now = datetime.now()
            if self.transaction_in is None:
                return now <= self.due_date
            else:
                return self.transaction_in.timestamp <= self.due_date
        else:
            return True
    is_on_time.boolean = True
    is_on_time.short_description = "on time?"

