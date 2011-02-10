from django import forms
from django.contrib.admin import widgets
from django.contrib.auth.models import User

from pendle.assets.models import Asset
from pendle.reservations.models import Transaction, Reservation


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['catalog', 'customer', 'staff_notes']

    due_date = forms.DateTimeField(required=False, input_formats=[
        '%Y-%m-%d %I:%M%p',
        '%Y-%m-%d %I:%M %p',
        '%Y-%m-%d %I%p',
        '%Y-%m-%d %I %p',
        '%m/%d/%Y %I:%M%p',
        '%m/%d/%Y %I:%M %p',
        '%m/%d/%Y %I%p',
        '%m/%d/%Y %I %p'])

