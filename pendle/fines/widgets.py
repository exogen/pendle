from django import forms
from django.utils.formats import number_format


class DollarsInput(forms.TextInput):
    def __init__(self, attrs=None):
        super(DollarsInput, self).__init__(attrs)
        self.attrs.setdefault('class', 'dollars')

    def _format_value(self, value):
        if self.is_localized:
            return number_format(value, 2)
        return value

    class Media:
        css = {'all': ('css/widgets.css',)}

