from django import forms

# Widgets 
from reception.widgets import DurationWidget
from reception.widgets import DurationFormField
from reception.widgets import DurationUpdateWidget

# models
from reception.models import Attendance
from reception.models import SortLeave


class AttendanceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    entering_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    exit_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Attendance
        exclude = ('attendance_of',)


class SortLeaveForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    outing_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    
    class Meta:
        model = SortLeave
        fields = ('employee_id', 'date', 'outing_time', 'description')
       
