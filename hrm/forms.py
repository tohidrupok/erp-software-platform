from django import forms
from .models import LeaveRequest, Attendance, LeaveRequest, Payroll, LeaveBalance

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

#admin 

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['user', 'date', 'status', 'check_in_time', 'check_out_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
        }

# Leave Request Form
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['user', 'start_date', 'end_date', 'reason', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
        
class LeaveBalanceForm(forms.ModelForm):
    class Meta:
        model = LeaveBalance
        fields = ['user','total_leaves', 'used_leaves', 'carry_forward']
        widgets = {
            'total_leaves': forms.NumberInput(attrs={'class': 'form-control'}),
            'used_leaves': forms.NumberInput(attrs={'class': 'form-control'}),
            'carry_forward': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Payroll Form
class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['user', 'month', 'year', 'basic_salary', 'allowances', 'deductions', 'paid_on']
        widgets = {
            'paid_on': forms.DateInput(attrs={'type': 'date'}),
        }
