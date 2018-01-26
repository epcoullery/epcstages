from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template import loader
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from candidats.models import Candidate


class ConvocationForm(forms.Form):
    id_candidate = forms.CharField(widget=forms.HiddenInput())
    sender = forms.CharField(widget=forms.HiddenInput())
    to = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    cci = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 25, 'cols': 120}))


class SendConvocationView(FormView):
    template_name = 'candidats/convocation.html'
    form_class = ConvocationForm
    success_url = reverse_lazy('admin:candidats_candidate_changelist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        docs = [
            'registration_form', 'certificate_of_payement', 'police_record', 'cv', 'reflexive_text',
            'has_photo', 'work_certificate', 'marks_certificate',
        ]
        if candidate.option == 'PE-5400h':
            docs.append('promise', 'contract', 'certif_of_800h')
        elif candidate.option == 'PE-3600h':
            docs.append('certif_of_cfc', 'promise', 'contract')
        elif candidate.option == 'PS':
            docs.append('certif_of_800h')

        missing_documents = {'documents': ', '.join([
            Candidate._meta.get_field(doc).verbose_name for doc in docs if not getattr(candidate, doc)
        ])}

        msg_context = {
            'candidate_name': " ".join([candidate.civility, candidate.first_name, candidate.last_name]),
            'candidate_civility': candidate.civility,
            'date_lieu_examen': settings.DATE_LIEU_EXAMEN_EDE,
            'date_entretien': candidate.interview.date_formatted,
            'salle_entretien': candidate.interview.room,
            'rappel': loader.render_to_string('email/rappel_document_EDE.txt', missing_documents),
            'sender_name': " ".join([self.request.user.first_name, self.request.user.last_name]),
            'sender_email': self.request.user.email,
        }

        form = ConvocationForm(initial={
            'id_candidate': candidate.pk,
            'cci': self.request.user.email,
            'to': candidate.email,
            'subject': "Procédure de qualification",
            'message': loader.render_to_string('email/candidate_convocation_EDE.txt', msg_context),
            'sender': self.request.user.email,
        })
        context.update({
            'candidat': candidate,
            'form': form,
        })
        return context

    def form_valid(self, form):
        email = EmailMessage(
            subject=form.cleaned_data['subject'],
            body=form.cleaned_data['message'],
            from_email=form.cleaned_data['sender'],
            to=form.cleaned_data['to'].split(';'),
            bcc=form.cleaned_data['cci'].split(';'),
        )
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        try:
            email.send()
        except Exception as err:
            messages.error(self.request, "Échec d’envoi pour le candidat {0} ({1})".format(candidate, err))
        else:
            candidate.convocation_date = timezone.now()
            candidate.save()
            messages.success(self.request,
                "Le message de convocation a été envoyé pour le candidat {0}".format(candidate)
            )
        return super().form_valid(form)
