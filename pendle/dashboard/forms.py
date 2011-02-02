from django import forms


class CustomizeActivityFeedForm(forms.Form):
    TYPES_CHOICES = (('transaction', "Transactions"),
                     ('overdue', "Overdue assets"),
                     ('fine-paid', "Fines paid"),
                     ('catalog', "Catalog changes"))
    LIMIT_CHOICES = ((10, 10), (25, 25), (50, 50), (100, 100))
    types = forms.MultipleChoiceField(choices=TYPES_CHOICES,
        initial=['transaction', 'overdue', 'fine-paid', 'catalog'],
        widget=forms.CheckboxSelectMultiple)
    limit = forms.TypedChoiceField(choices=LIMIT_CHOICES, coerce=int, initial=25)

