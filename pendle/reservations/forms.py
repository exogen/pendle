from django import forms
from django.contrib.auth.models import User

from pendle.reservations.models import Transaction, Reservation


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
