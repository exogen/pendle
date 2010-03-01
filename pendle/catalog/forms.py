import calendar

from django import forms

from catalog.models import Period, Catalog


class PeriodForm(forms.ModelForm):
    DAY_CHOICES = tuple((day, calendar.day_name[day]) for day in range(7))
    days = forms.MultipleChoiceField(label="days", choices=DAY_CHOICES,
                                     initial=range(5),
                                     widget=forms.CheckboxSelectMultiple)
    
    class Meta:
        model = Period

    def clean_days(self):
        return ','.join(map(str, self.cleaned_data['days']))


class InlinePeriodForm(PeriodForm):
    DAY_CHOICES = tuple((day, calendar.day_abbr[day]) for day in range(7))
    days = forms.MultipleChoiceField(label="days", choices=DAY_CHOICES,
                                     initial=range(5),
                                     widget=forms.CheckboxSelectMultiple)

