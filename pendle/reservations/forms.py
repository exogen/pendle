from django import forms
from django.contrib.auth.models import User

from pendle.assets.models import Asset
from pendle.reservations.models import Transaction, Reservation


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['catalog', 'customer', 'staff_notes']

    #asset_in = forms.ModelChoiceField(queryset=Asset.objects.all())
    #asset_out = forms.ModelChoiceField(queryset=Asset.objects.all())

