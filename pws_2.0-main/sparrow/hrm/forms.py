from django import forms

from .models import AcademicQualification, LeaveAllocation, LeaveType


class LeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ["name", "days"]


class QualificationForm(forms.ModelForm):
    class Meta:
        model = AcademicQualification
        fields = ["name", "created_by"]


class LeavesAllocationForm(forms.ModelForm):
    class Meta:
        model = LeaveAllocation
        fields = ["worker", "leave_type", "days", "description", "allocate_year"]
