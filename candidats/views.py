import os

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from candidats.forms import EmailBaseForm
from candidats.models import Candidate, Interview
from .pdf import InscriptionSummaryPDF


class EmailConfirmationBaseView(FormView):
    template_name = 'email_base.html'
    form_class = EmailBaseForm
    success_url = reverse_lazy('admin:candidats_candidate_changelist')
    success_message = "Le message a été envoyé pour le candidat {candidate}"
    candidate_date_field = None

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
            setattr(candidate, self.candidate_date_field, timezone.now())
            candidate.save()
            messages.success(self.request, self.success_message.format(candidate=candidate))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'candidat': Candidate.objects.get(pk=self.kwargs['pk']),
            'title': self.title,
        })
        return context


class ConfirmationView(EmailConfirmationBaseView):
    success_message = "Le message de confirmation a été envoyé pour le candidat {candidate}"
    candidate_date_field = 'confirmation_date'
    title = "Confirmation de réception de dossier"

    def get(self, request, *args, **kwargs):
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        if candidate.section != 'EDE' and not candidate.section in {'ASA', 'ASE', 'ASSC'}:
            messages.error(request, "Ce formulaire n'est disponible que pour les candidats EDE ou FE")
        elif candidate.confirmation_date:
            messages.error(request, 'Une confirmation a déjà été envoyée!')
        elif candidate.canceled_file:
            messages.error(request, 'Ce dossier a été annulé!')
        else:
            return super().get(request, *args, **kwargs)
        return redirect(reverse("admin:candidats_candidate_change", args=(candidate.pk,)))

    def get_initial(self):
        initial = super().get_initial()
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])

        to = [candidate.email]
        if candidate.section == 'EDE':
            src_email = 'email/candidate_confirm_EDE.txt'
        elif candidate.section in {'ASA', 'ASE', 'ASSC'}:
            src_email = 'email/candidate_confirm_FE.txt'
            if candidate.corporation and candidate.corporation.email:
                to.append(candidate.corporation.email)
            if candidate.instructor and candidate.instructor.email:
                to.append(candidate.instructor.email)

        msg_context = {
            'candidate': candidate,
            'sender': self.request.user,
        }
        initial.update({
            'id_candidate': candidate.pk,
            'cci': self.request.user.email,
            'to': '; '.join(to),
            'subject': "Inscription à la formation {0}".format(candidate.section_option),
            'message': loader.render_to_string(src_email, msg_context),
            'sender': self.request.user.email,
        })
        return initial


class ValidationView(EmailConfirmationBaseView):
    success_message = "Le message de validation a été envoyé pour le candidat {candidate}"
    candidate_date_field = 'validation_date'
    title = "Validation des examens par les enseignant-e-s EDE"

    def get(self, request, *args, **kwargs):
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        if candidate.validation_date:
            messages.error(request, 'Une validation a déjà été envoyée!')
            return redirect(reverse("admin:candidats_candidate_change", args=(candidate.pk,)))
        elif not candidate.has_interview:
            messages.error(request, "Aucun interview attribué à ce candidat pour l’instant")
            return redirect(reverse("admin:candidats_candidate_change", args=(candidate.pk,)))
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])

        msg_context = {
            'candidate': candidate,
            'sender': self.request.user,
        }
        initial.update({
            'id_candidate': candidate.pk,
            'cci': self.request.user.email,
            'to': ';'.join([
                candidate.interview.teacher_int.email, candidate.interview.teacher_file.email
            ]),
            'subject': "Validation de l'entretien d'admission",
            'message': loader.render_to_string('email/validation_enseignant_EDE.txt', msg_context),
            'sender': self.request.user.email,
        })
        return initial


class ConvocationView(EmailConfirmationBaseView):
    success_message = "Le message de convocation a été envoyé pour le candidat {candidate}"
    candidate_date_field = 'convocation_date'
    title = "Convocation aux examens d'admission EDE"

    def get(self, request, *args, **kwargs):
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        if not candidate.has_interview:
            messages.error(request, "Impossible de convoquer sans d'abord définir un interview!")
            return redirect(reverse("admin:candidats_candidate_change", args=(candidate.pk,)))
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        # Define required documents depending on candidate diploma
        common_docs = [
            'registration_form', 'certificate_of_payement', 'police_record', 'cv', 'reflexive_text',
            'has_photo', 'marks_certificate',
        ]
        dipl_docs = {
            0: [],
            1: ['work_certificate'],  # CFC ASE
            2: ['certif_of_800_childhood', 'work_certificate'],
            3: ['certif_of_800_general', 'certif_of_800_childhood', 'work_certificate'],
            4: ['certif_of_800_general', 'certif_of_800_childhood', 'work_certificate'],
        }[candidate.diploma]
        docs_required = dipl_docs + common_docs

        missing_documents = {'documents': ', '.join([
            Candidate._meta.get_field(doc).verbose_name for doc in docs_required
            if not getattr(candidate, doc)
        ])}

        msg_context = {
            'candidate': candidate,
            'candidate_name': " ".join([candidate.civility, candidate.first_name, candidate.last_name]),
            'option': candidate.get_option_display(),
            'date_lieu_examen': settings.DATE_LIEU_EXAMEN_EDE,
            'date_entretien': candidate.interview.date_formatted,
            'salle_entretien': candidate.interview.room,
            'sender_name': " ".join([self.request.user.first_name, self.request.user.last_name]),
            'sender_email': self.request.user.email,
        }

        if missing_documents['documents']:
            msg_context['rappel'] = loader.render_to_string('email/rappel_document_EDE.txt', missing_documents)

        initial.update({
            'id_candidate': candidate.pk,
            'cci': self.request.user.email,
            'to': candidate.email,
            'subject': "Procédure de qualification",
            'message': loader.render_to_string('email/candidate_convocation_EDE.txt', msg_context),
            'sender': self.request.user.email,
        })
        return initial


def inscription_summary(request, pk):
    """
    Print a PDF summary of inscription
    """
    candidat = Candidate.objects.get(pk=pk)
    pdf = InscriptionSummaryPDF(candidat)
    pdf.produce(candidat)

    with open(pdf.filename, mode='rb') as fh:
        response = HttpResponse(fh.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(os.path.basename(pdf.filename))
    return response
