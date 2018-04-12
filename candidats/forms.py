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
        if kwargs.get('instance') and kwargs['instance'].has_interview:
            kwargs['initial'] = {'interview': kwargs['instance'].interview}
        return super().__init__(*args, **kwargs)

    def save(self, **kwargs):
        obj = super().save(**kwargs)
        if 'interview' in self.changed_data:
            if self.cleaned_data['interview'] is None:
                self.initial['interview'].candidat = None
                self.initial['interview'].save()
            else:
                Interview.objects.filter(candidat=obj).update(candidat=None)
                self.cleaned_data['interview'].candidat = obj
                self.cleaned_data['interview'].save()
        return obj
