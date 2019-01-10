from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.db import transaction
from django.db.models.deletion import Collector
from django.urls import reverse

from tabimport import FileFactory, UnsupportedFileFormat

from .models import Corporation, Section, Period


class StudentImportForm(forms.Form):
    upload = forms.FileField()

    def __init__(self, file_label='Fichier', mandatory_headers=None, **kwargs):
        super().__init__(**kwargs)
        self.fields['upload'].label = file_label
        self.mandatory_headers = mandatory_headers

    def clean_upload(self):
        f = self.cleaned_data['upload']
        try:
            imp_file = FileFactory(f)
        except UnsupportedFileFormat as e:
            raise forms.ValidationError("Erreur: %s" % e)
        # Check needed headers are present
        headers = imp_file.get_headers()
        missing = set(self.mandatory_headers) - set(headers)
        if missing:
            raise forms.ValidationError("Erreur: il manque les colonnes %s" % (
                ", ".join(missing)))
        return f


class PeriodForm(forms.Form):
    section = forms.ModelChoiceField(queryset=Section.objects.all())
    period = forms.ModelChoiceField(queryset=None)

    def __init__(self, data, *args, **kwargs):
        pass


class UploadHPFileForm(forms.Form):
    upload = forms.FileField(label='Fichier HyperPlanning')


class UploadReportForm(forms.Form):
    semester = forms.ChoiceField(label='Semestre', choices=(('1', '1'), ('2', '2')), required=True)
    upload = forms.FileField(label='Bulletins CLOEE (pdf)')


class EmailBaseForm(forms.Form):
    sender = forms.CharField(widget=forms.HiddenInput())
    to = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    cci = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': 120}))



class CorpAutocompleteSelect(AutocompleteSelect):
    model = Corporation

    def __init__(self, **kwargs):
        super().__init__(None, None, **kwargs)

    def get_url(self):
        return reverse(self.url_name % ('admin', self.model._meta.app_label, self.model._meta.model_name))


class CorporationMergeForm(forms.Form):
    corp_merge_from = forms.ModelChoiceField(
        label="L'institution", queryset=Corporation.objects.filter(archived=False),
        widget=CorpAutocompleteSelect
    )
    corp_merge_to = forms.ModelChoiceField(
        label="Sera fusionnée dans", queryset=Corporation.objects.filter(archived=False),
        widget=CorpAutocompleteSelect
    )

    def merge_corps(self):
        def check_no_links(instance):
            collector = Collector(using='default')
            collector.collect(instance._meta.model.objects.filter(pk=instance.pk))
            if len(collector.data) > 1:
                raise Exception(collector.data)

        with transaction.atomic():
            # Try first to merge corpcontacts with same name
            merge_to_contacts = {
                (cont.last_name, cont.first_name): cont
                for cont in self.cleaned_data['corp_merge_to'].corpcontact_set.all()
            }
            for contact in self.cleaned_data['corp_merge_from'].corpcontact_set.all():
                ckey = (contact.last_name, contact.first_name)
                if ckey in merge_to_contacts:
                    # Merge contacts
                    for rel in (
                            'availability_set', 'candidate_set', 'rel_expert', 'rel_mentor',
                            'rel_supervisor', 'student_set', 'supervisionbill_set'):
                        relation = getattr(contact, rel)
                        relation.all().update(**{relation.field.name: merge_to_contacts[ckey]})
                    check_no_links(contact)
                    contact.delete()
            # Merge corporation now
            self.cleaned_data['corp_merge_from'].corpcontact_set.all(
                ).update(corporation=self.cleaned_data['corp_merge_to'])
            self.cleaned_data['corp_merge_from'].availability_set.all(
                ).update(corporation=self.cleaned_data['corp_merge_to'])
            self.cleaned_data['corp_merge_from'].student_set.all(
                ).update(corporation=self.cleaned_data['corp_merge_to'])
            self.cleaned_data['corp_merge_from'].candidate_set.all(
                ).update(corporation=self.cleaned_data['corp_merge_to'])
            check_no_links(self.cleaned_data['corp_merge_from'])
            self.cleaned_data['corp_merge_from'].delete()
