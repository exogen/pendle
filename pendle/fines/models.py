from datetime import datetime

from django.db import models
from django.contrib.admin.models import User

from reservations.models import Reservation


class Fine(models.Model):
    customer = models.ForeignKey(User, related_name='fines')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True)
    staff_member = models.ForeignKey(User, verbose_name="issued by",
        related_name='fines_issued', limit_choices_to={'is_staff': True})
    date_issued = models.DateTimeField(default=datetime.now)


class FinePayment(models.Model):
    customer = models.ForeignKey(User, related_name='fine_payments')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True)
    date_received = models.DateTimeField(default=datetime.now)
    staff_member = models.ForeignKey(User, verbose_name="received by",
        related_name='fine_payments_received',
        limit_choices_to={'is_staff': True})

