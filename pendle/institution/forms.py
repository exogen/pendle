from django import forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from pendle.institution.models import ScheduledCourse
from pendle.utils.forms import YearInput


class ScheduledCourseForm(forms.ModelForm):
    class Meta:
        model = ScheduledCourse
        widgets = {'year': YearInput(attrs={'size': 5}),
                   'students': FilteredSelectMultiple("users", False)}

class ScanCustomerForm(forms.Form):
    class Media:
        js = ('js/scan.js',)

    query = forms.CharField(label="ID number",
        widget=forms.TextInput(attrs={'class': 'query'}),
        help_text="Enter the user's ID number or username.")
    customer = forms.ModelChoiceField(queryset=User.objects.all(),
                                      widget=forms.HiddenInput,
                                      required=False)
    
    def clean_query(self):
        return self.cleaned_data['query'].strip()

    def clean_customer(self):
        query = self.cleaned_data['query']
        try:
            user = User.objects.get(profile__id_number=query)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=query)
            except User.DoesNotExist:
                raise forms.ValidationError("No user with this ID number or "
                                            "username was found.")
        return user

