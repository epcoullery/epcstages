from django import forms
from django.conf import settings


class MailingForm(forms.Form):
    to = forms.EmailField(max_length=100, verbose_name='destinataire')
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()




