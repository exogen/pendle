from django import forms
from django.forms.widgets import Input
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User


class YearInput(Input):
    input_text = 'text'

    def _format_value(self, value):
        if value is None:
            return ''
        else:
            return force_unicode(value)

    def render(self, name, value, attrs=None):
        value = self._format_value(value)
        return super(YearInput, self).render(name, value, attrs)


class UserChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset=None, *args, **kwargs):
        if queryset is None:
            queryset = User.objects.order_by('last_name', 'first_name')
        super(UserChoiceField, self).__init__(queryset, *args, **kwargs)

    def label_from_instance(self, user):
        label = user.last_name
        if label:
            label = '%s, %s' % (label, user.first_name)
        else:
            label = user.first_name
        if label:
            label = '%s &mdash; %s' % (label, user.username)
        else:
            label = user.username
        return mark_safe(label)


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = FilteredSelectMultiple("users", False)

    def __init__(self, queryset=None, *args, **kwargs):
        if queryset is None:
            queryset = User.objects.order_by('last_name', 'first_name')
        super(UserMultipleChoiceField, self).__init__(queryset, *args, **kwargs)

    label_from_instance = UserChoiceField.label_from_instance.__func__

