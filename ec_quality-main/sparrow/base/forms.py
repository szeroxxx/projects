from django import forms

from base.models import CurrencyRate, SysParameter, TaskScheduler


class SysParameterForm(forms.ModelForm):
    class Meta:
        model = SysParameter
        fields = ["para_code", "descr", "para_value", "para_group"]


class CurrencyRateForm(forms.ModelForm):
    class Meta:
        model = CurrencyRate
        fields = ["currency", "factor", "reference_date", "expire_date"]


class TaskScheduleForm(forms.ModelForm):
    class Meta:
        model = TaskScheduler
        fields = ["title", "schedule", "url", "is_active", "next_run", "pattern", "last_run_result", "notification_email", "is_running"]
