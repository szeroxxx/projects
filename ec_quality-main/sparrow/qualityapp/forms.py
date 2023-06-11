from xml.dom.minidom import Attr
from django import forms
from qualityapp.models import Company, CompanyParameter


class CompanyForm(forms.ModelForm):
    initials = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Company
        fields = ['name', 'is_active']
        widgets = {
            'name' : forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus', 'placeholder': 'Enter customer name'}),
            'is_active' : forms.CheckboxInput(),
        }


class CompanyParameterForm(forms.ModelForm):
    gen_mail = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter general email'}))
    ord_rec_mail = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter order receive mail'}))
    ord_exc_rem_mail = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter exception mail to customer'}))
    ord_exc_gen_mail = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter exception mail to leader'}))
    ord_comp_mail = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter order completion mail'}))
    mail_from = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mail from'}))
    int_exc_from = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Internal Exception From'}))
    int_exc_to = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Internal Exception To'}))
    int_exc_cc = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Internal Exception Cc'}))

    class Meta:
        model = CompanyParameter
        fields = [
            'gen_mail',
            'ord_rec_mail',
            'ord_exc_gen_mail',
            'ord_exc_rem_mail',
            'ord_comp_mail',
            'mail_from',
            'int_exc_from',
            'int_exc_to',
            'int_exc_cc',
            'is_req_files',
            'is_send_attachment',
            'is_exp_file_attachment',
        ]
        widgets = {
            'is_req_files' : forms.CheckboxInput(),
            'is_send_attachment' : forms.CheckboxInput(),
            'is_exp_file_attachment' : forms.CheckboxInput(),
        }
