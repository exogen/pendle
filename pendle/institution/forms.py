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

