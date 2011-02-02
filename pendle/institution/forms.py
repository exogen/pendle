from django import forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from pendle.institution.models import ScheduledCourse, Profile, Department
from pendle.utils.forms import YearInput


class ScheduledCourseForm(forms.ModelForm):
    class Meta:
        model = ScheduledCourse
        widgets = {'year': YearInput(attrs={'size': 5}),
                   'students': FilteredSelectMultiple("users", False)}

class ScanCustomerForm(forms.Form):
    class Media:
        js = ('js/knockout.bindings.js', 'js/scan.js',)

    query = forms.CharField(label="ID number",
        widget=forms.TextInput(attrs={'class': 'query', 'spellcheck': 'false',
                                      'autocomplete': 'off',
                                      'data-bind': "value: query, focused: focused"}),
        help_text="Enter the user's ID number or username.")
    customer = forms.ModelChoiceField(queryset=User.objects.all(),
                                      widget=forms.HiddenInput,
                                      required=False)
    
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
                raise forms.ValidationError("No user with this ID number or "
                                            "username was found.")
        self.cleaned_data['customer'] = user
        return self.cleaned_data

class ScanNewCustomerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ScanNewProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['id_number']
    
    department = forms.ModelChoiceField(queryset=Department.objects.all(),
        required=False)
