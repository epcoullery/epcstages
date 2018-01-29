from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template import loader
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, CreateView, UpdateView
from django.http import HttpResponseRedirect
from candidats.models import Candidate
from candidats.forms import CandidateProfileForm


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
        my_dict = {
            0: [],
            1: ['work_certificate'], # CFC ASE
            2: ['certif_of_800_childhood', 'work_certificate'],
            3: ['certif_of_800_general', 'certif_of_800_childhood', 'work_certificate'],
            4: ['certif_of_800_general', 'certif_of_800_childhood', 'work_certificate'],
        }
        docs_required = my_dict[candidate.diploma]
        docs_required.extend(['registration_form', 'certificate_of_payement', 'police_record', 'cv', 'reflexive_text',
            'has_photo', 'marks_certificate'])

        print(docs_required)

        missing_documents = {'documents': ', '.join([
            Candidate._meta.get_field(doc).verbose_name for doc in docs_required if not getattr(candidate, doc)
        ])}

        msg_context = {
            'candidate_name': " ".join([candidate.civility, candidate.first_name, candidate.last_name]),
            'candidate_civility': candidate.civility,
            'option': candidate.get_option_display(),
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
            #to=form.cleaned_data['to'].split(';'),
            to=['alain.zosso@rpn.ch'],
            bcc=form.cleaned_data['cci'].split(';'),
        )
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        try:
            # email.send()
            print(email)
        except Exception as err:
            messages.error(self.request, "Échec d’envoi pour le candidat {0} ({1})".format(candidate, err))
        else:
            candidate.convocation_date = timezone.now()
            candidate.save()
            messages.success(self.request,
                "Le message de convocation a été envoyé pour le candidat {0}".format(candidate)
            )
        return super().form_valid(form)


class CandidateCreateView(CreateView):
    model = Candidate
    template_name = 'candidate_profile.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CandidateProfileForm
        return context

    def form_valid(self, form):
        print(self.request.user)
        return super().form_valid(form)


class CandidateUpdateView(UpdateView):
    template_name = 'candidate_update_form.html'
    model = Candidate
    fields = '__all__'
    success_url = '/admin/candidats/candidate'

    def form_valid(self, form):
        print(form)
        return super(CandidateUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(CandidateUpdateView, self).form_invalid(form)