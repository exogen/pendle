from django import forms
from django.contrib.auth.models import User

from pendle.institution.models import ScheduledCourse
from pendle.utils.forms import (YearInput, UserChoiceField,
                                UserMultipleChoiceField)


class ScheduledCourseForm(forms.ModelForm):
    class Meta:
        model = ScheduledCourse
        widgets = {'year': YearInput(attrs={'size': 5})}

    instructor = UserChoiceField(label="instructor")
    students = UserMultipleChoiceField(label="enrolled")

