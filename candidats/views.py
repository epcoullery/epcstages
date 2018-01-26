from django import forms
from datetime import datetime

from django.template import loader
from django.views.generic import FormView
from django.core.mail import EmailMessage
from django.conf import settings

from candidats.models import Candidate
from candidats.models import OPTION_CHOICES

class ConvocationForm(forms.Form):
    id_candidate = forms.CharField(widget=forms.HiddenInput())
    sender = forms.CharField(widget=forms.HiddenInput())
    to = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    cci = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': '60'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':25, 'cols':120}))


class SendConvocationView(FormView):
    template_name = 'convocation.html'
    form_class = ConvocationForm
    success_url = '/admin/candidats/candidate'

    def get_context_data(self, **kwargs):
        context = super(SendConvocationView, self).get_context_data(**kwargs)

        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        context['candidat'] = candidate

        docs = ['registration_form', 'certificate_of_payement', 'police_record', 'cv', 'reflexive_text',
                'has_photo', 'work_certificate', 'marks_certificate']
        if candidate.option == 'PE-5400h':
            docs.append('promise', 'contract', 'certif_of_800_chilhood')
        elif candidate.option == 'PE-3600h':
            docs.append('certif_of_cfc', 'promise', 'contract')
        elif candidate.option == 'PS':
            docs.append('certif_of_800_childhood')

        documents_list = [Candidate._meta.get_field(doc).verbose_name for doc in docs if not getattr(candidate, doc)]
        documents = {'documents': ', '.join(documents_list)}
        options = dict((x, y) for x, y in OPTION_CHOICES)


        data = {
            'candidate' : candidate,
            'candidate_name': " ".join([candidate.civility, candidate.first_name, candidate.last_name]),
            'candidate_civility': candidate.civility,
            'accord': 'e' if candidate.gender=='F' else '',
            'option': options[candidate.option],
            'date_entretien': candidate.interview.date.strftime(settings.FORMATED_DATE_TIME),
            'salle_entretien': candidate.interview.room,
            'rappel' : loader.render_to_string('email/rappel_document_EDE.txt', documents),
            'sender_name': " ".join([self.request.user.first_name, self.request.user.last_name]),
            'sender_email': self.request.user.email,
        }

        form = ConvocationForm(initial={
            'id_candidate': candidate.id,
            'cci': self.request.user.email,
            'to': candidate.email,
            'subject': "Procédure de qualification",
            'message': loader.render_to_string('email/convocation_EDE.txt', data),
            'sender' : self.request.user.email,
        })
        context.update({
            'candidat':candidate,
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
        # *******************
        email.send()
        # *******************

        candidate = Candidate.objects.get(pk=form.cleaned_data['candidate'])
        candidate.date_convocation_sended=datetime.now()
        candidate.save()

        return super().form_valid(form)

