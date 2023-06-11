from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "task_type", "due_date", "reminder_on", "reminder_on_text", "status", "priority", "assign_to", "email_notification", "private", "general"]
