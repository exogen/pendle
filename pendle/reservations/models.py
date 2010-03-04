from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from pendle.catalog.models import Catalog
from pendle.assets.models import Asset


class Transaction(models.Model):
    catalog = models.ForeignKey(Catalog, related_name='transactions')
    staff_user = models.ForeignKey(User, related_name='staff_transactions',
                                   limit_choices_to={'is_staff': True})
    customer = models.ForeignKey(User, related_name='transactions')
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['-timestamp']


class Reservation(models.Model):
    asset = models.ForeignKey(Asset, related_name='reservations')
    transaction_out = models.ForeignKey(Transaction,
        verbose_name="checkout transaction", related_name='reservations_out',
        help_text="The transaction in which this asset was checked out.")
    transaction_in = models.ForeignKey(Transaction, null=True, blank=True,
        verbose_name="checkin transaction", related_name='reservations_in',
        help_text="The transaction in which this asset was returned.")
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [('asset', 'transaction_out'),
                           ('asset', 'transaction_in')]
        ordering = ['-transaction_out', 'asset']


