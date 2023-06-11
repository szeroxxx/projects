from django import forms

from .models import Messaging


class MessageForm(forms.ModelForm):
    class Meta:
        model = Messaging
        fields = ["subject", "message"]
