from django import forms

from .models import Candidate, Interview


class CandidateForm(forms.ModelForm):
    interview = forms.ModelChoiceField(queryset=Interview.objects.all(), required=False)

    class Meta:
        model = Candidate
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 100, 'rows': 1}),
            'pcode': forms.TextInput(attrs={'size': 10}),
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            try:
                kwargs['initial'] = {'interview': kwargs['instance'].interview}
            except Interview.DoesNotExist:
                pass
        return super().__init__(*args, **kwargs)

    def save(self, **kwargs):
        obj = super().save(**kwargs)
        if 'interview' in self.changed_data:
            if self.cleaned_data['interview'] is None:
                self.initial['interview'].candidat = None
                self.initial['interview'].save()
            else:
                self.cleaned_data['interview'].candidat = obj
                self.cleaned_data['interview'].save()
        return obj


class EmailBaseForm(forms.Form):
    id_candidate = forms.CharField(widget=forms.HiddenInput())
    sender = forms.CharField(widget=forms.HiddenInput())
    to = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    cci = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 25, 'cols': 120}))
