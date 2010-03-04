from django import forms
from django.forms.widgets import TextInput
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.encoding import force_unicode


class YearInput(TextInput):
    input_text = 'text'

    def _format_value(self, value):
        if value is None:
            return ''
        else:
            return force_unicode(value)

    def render(self, name, value, attrs=None):
        value = self._format_value(value)
        return super(YearInput, self).render(name, value, attrs)

