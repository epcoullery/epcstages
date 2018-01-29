from django import forms
from candidats.models import Candidate


class CandidateProfileForm(forms.ModelForm):

    class Meta:
        model= Candidate
        fields = '__all__'

