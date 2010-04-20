from datetime import datetime

from django.db import models
from django.db.models import Sum
from django.contrib.admin.models import User

from reservations.models import Reservation
from utils.text import format_dollars


class FineManager(models.Manager):
    def get_amount_due(self, user):
        issued = user.fines.aggregate(total=Sum('amount'))
        paid = user.fine_payments.aggregate(total=Sum('amount'))
        return (issued['total'] or 0) - (paid['total'] or 0)

class Fine(models.Model):
    customer = models.ForeignKey(User, related_name='fines')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True)
    staff_member = models.ForeignKey(User, verbose_name="issued by",
        related_name='fines_issued', limit_choices_to={'is_staff': True})
    date_issued = models.DateTimeField(default=datetime.now)

    objects = FineManager()

    class Meta:
        ordering = ['-date_issued']

    def __unicode__(self):
        return "%s fined %s" % (self.customer, format_dollars(self.amount))

class FinePayment(models.Model):
    customer = models.ForeignKey(User, related_name='fine_payments')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True)
    date_received = models.DateTimeField(default=datetime.now)
    staff_member = models.ForeignKey(User, verbose_name="received by",
        related_name='fine_payments_received',
        limit_choices_to={'is_staff': True})

    class Meta:
        ordering = ['-date_received']

    def __unicode__(self):
        return "%s paid %s" % (self.customer, format_dollars(self.amount))

