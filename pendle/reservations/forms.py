from django import forms
from django.contrib.auth.models import User

from pendle.reservations.models import Transaction, Reservation


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction


class ScanCustomerForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['customer']

    class Media:
        js = ('js/scan.js',)

    query = forms.CharField(label="ID number",
        help_text="Enter the user's ID number or username")
    customer = forms.ModelChoiceField(queryset=User.objects.all(),
                                      widget=forms.HiddenInput)
    
    def clean_query(self):
        return self.cleaned_data['query'].strip()

    def clean(self):
        query = self.cleaned_data['query']
        try:
            user = User.objects.get(profile__id_number=query)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=query)
            except User.DoesNotExist:
                raise forms.ValidationError("A user with this ID number or "
                                            "username was not found.")
        self.cleaned_data['customer'] = user
        return self.cleaned_data

