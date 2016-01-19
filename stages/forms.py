from django import forms
from django.conf import settings

from tabimport import FileFactory, UnsupportedFileFormat

from .models import Section, Period


class StudentImportForm(forms.Form):
    upload = forms.FileField(label="Fichier des étudiants")

    def clean_upload(self):
        f = self.cleaned_data['upload']
        try:
            imp_file = FileFactory(f)
        except UnsupportedFileFormat as e:
            raise forms.ValidationError("Erreur: %s" % e)
        # Check needed headers are present
        headers = imp_file.get_headers()
        missing = set(settings.STUDENT_IMPORT_MAPPING.keys()) - set(headers)
        if missing:
            raise forms.ValidationError("Erreur: il manque les colonnes %s" % (
                ", ".join(missing)))
        return f


class PeriodForm(forms.Form):
    section = forms.ModelChoiceField(queryset=Section.objects.all())
    period = forms.ModelChoiceField(queryset=None)

    def __init__(self, data, *args, **kwargs):
        pass
        
