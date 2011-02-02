from django import forms

from pendle.catalog.models import Catalog
from pendle.assets.models import Asset


class ScanAssetForm(forms.Form):
    class Media:
        js = ('js/knockout.bindings.js', 'js/scan.js',)

    query = forms.CharField(label="Barcode",
        widget=forms.TextInput(attrs={'class': 'query',
                                      'spellcheck': 'false', 'autocomplete': 'off',
                                      'data-bind': "value: query, focused: focused"}),
        help_text="Enter the asset's unique barcode.")
    catalog = forms.ModelChoiceField(queryset=Catalog.objects.all(),
                                     widget=forms.HiddenInput)
    asset = forms.ModelChoiceField(queryset=Asset.objects.all(),
                                   widget=forms.HiddenInput,
                                   required=False)
    
    def clean_query(self):
        return self.cleaned_data['query'].strip()

    def clean(self):
        query = self.cleaned_data['query']
        catalog = self.cleaned_data['catalog']
        try:
            asset = catalog.assets.get(barcode=query)
        except Asset.DoesNotExist:
            try:
                asset = catalog.assets.get(barcode__iexact=query)
            except Asset.DoesNotExist:
                raise forms.ValidationError("No asset with this barcode was "
                                            "found in the selected catalog.")
        self.cleaned_data['asset'] = asset
        return self.cleaned_data

