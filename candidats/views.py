import io
import os

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.text import slugify

from stages.views.base import EmailConfirmationBaseView
from candidats.models import Candidate, Interview
from .pdf import InscriptionSummaryPDF


class CandidateConfirmationView(EmailConfirmationBaseView):
    person_model = Candidate
    success_url = reverse_lazy('admin:candidats_candidate_changelist')
    error_message = "Échec d’envoi pour le candidat {person} ({err})"
    candidate_date_field = None

    def on_success(self, candidate):
        setattr(candidate, self.candidate_date_field, timezone.now())
        candidate.save()


class ConfirmationView(CandidateConfirmationView):
    """
    Email confirming the receipt of the registration form
    """
    success_message = "Une confirmation d’inscription a été envoyée à {person}"
    candidate_date_field = 'confirmation_date'
    title = "Confirmation de réception de dossier"

    def get(self, request, *args, **kwargs):
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        if candidate.section not in {'ASA', 'ASE', 'ASSC', 'EDE', 'EDS'}:
            messages.error(request, "Ce formulaire n'est disponible que pour les candidats FE ou ES")
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
        elif candidate.section == 'EDS':
            src_email = 'email/candidate_confirm_EDS.txt'
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
            'cci': self.request.user.email,
            'to': '; '.join(to),
            'subject': "Inscription à la formation {0}".format(candidate.section_option),
            'message': loader.render_to_string(src_email, msg_context),
            'sender': self.request.user.email,
        })
        return initial


class ValidationView(CandidateConfirmationView):
    success_message = "Le message de validation a été envoyé pour le candidat {person}"
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
            'cci': self.request.user.email,
            'to': ';'.join([
                candidate.interview.teacher_int.email, candidate.interview.teacher_file.email
            ]),
            'subject': "Validation de l'entretien d'admission",
            'message': loader.render_to_string('email/validation_enseignant_EDE.txt', msg_context),
            'sender': self.request.user.email,
        })
        return initial


class ConvocationView(CandidateConfirmationView):
    success_message = "Le message de convocation a été envoyé pour le candidat {person}"
    candidate_date_field = 'convocation_date'
    title = "Convocation aux examens d'admission EDE/EDS"

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
            'has_photo',
        ]
        dipl_docs = {
            0: [],
            1: ['work_certificate'],  # CFC ASE
            2: ['work_certificate'],
            3: ['certif_of_400_general', 'work_certificate'],
            4: ['certif_of_400_general', 'work_certificate'],
        }[candidate.diploma]
        docs_required = dipl_docs + common_docs

        missing_documents = {
            'candidate': candidate,
            'documents': ', '.join([
                Candidate._meta.get_field(doc).verbose_name for doc in docs_required
                if not getattr(candidate, doc)
            ]),
        }

        msg_context = {
            'candidate': candidate,
            'candidate_name': " ".join([candidate.civility, candidate.first_name, candidate.last_name]),
            'filiere': "Éducation de l’enfance" if candidate.section == 'EDE' else "Éducation sociale",
            'date_lieu_examen': settings.DATE_LIEU_EXAMEN_EDE if candidate.section == 'EDE' else settings.DATE_LIEU_EXAMEN_EDS,
            'duree_examen': '2h30' if candidate.section == 'EDE' else '3h00',
            'date_entretien': candidate.interview.date_formatted,
            'salle_entretien': candidate.interview.room,
            'sender_name': " ".join([self.request.user.first_name, self.request.user.last_name]),
            'sender_email': self.request.user.email,
        }

        if missing_documents['documents']:
            msg_context['rappel'] = loader.render_to_string('email/rappel_document_EDE.txt', missing_documents)

        initial.update({
            'cci': self.request.user.email,
            'to': candidate.email,
            'subject': "Procédure d'admission",
            'message': loader.render_to_string('email/candidate_convocation_EDE.txt', msg_context),
            'sender': self.request.user.email,
        })
        return initial


def inscription_summary(request, pk):
    """
    Print a PDF summary of inscription
    """
    candidat = get_object_or_404(Candidate, pk=pk)
    buff = io.BytesIO()
    pdf = InscriptionSummaryPDF(buff)
    pdf.produce(candidat)
    filename = slugify('{0}_{1}'.format(candidat.last_name, candidat.first_name)) + '.pdf'
    buff.seek(0)
    return FileResponse(buff, as_attachment=True, filename=filename)
