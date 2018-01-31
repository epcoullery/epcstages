import os
import tempfile

from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import FormView
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

from candidats.models import Candidate
from stages.pdf import InscriptionSummaryPDF
from .forms import EmailBaseForm


class ConfirmationView(FormView):
    template_name = 'email_base.html'
    form_class = EmailBaseForm
    success_url = reverse_lazy('admin:candidats_candidate_changelist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])

        if candidate.date_confirmation_mail:
            messages.error(self.request, 'Une confirmation a déjéà été envoyée!')

        if candidate.section == 'EDE':
            src_email = 'email/candidate_confirm_EDE.txt'
            to = [candidate.email]
        else:
            src_email = 'email/candidate_confirm_FE.txt'
            to = [candidate.email]
            if candidate.corporation and candidate.corporation.email:
                to.append(candidate.corporation.email)
            if candidate.instructor and candidate.instructor.email:
                to.append(candidate.instructor.email)

        msg_context = {
            'candidate': candidate,
            'sender': self.request.user,
        }
        form = EmailBaseForm(initial={
            'id_candidate': candidate.pk,
            'cci': self.request.user.email,
            'to': '; '.join(to),
            'subject': "Inscription à la formation {0}".format(candidate.section_option),
            'message': loader.render_to_string(src_email, msg_context),
            'sender': self.request.user.email,
        })
        context.update({
            'candidat': candidate,
            'form': form,
            'title': "Confirmation de réception de dossier"
        })
        return context

    def form_valid(self, form):
        super().form_valid(form)
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
            candidate.date_confirmation_mail = timezone.now()
            candidate.save()
            messages.success(
                self.request,
                "Le message de confirmation a été envoyé pour le candidat {0}".format(candidate)
            )
        return redirect(reverse("admin:candidats_candidate_change", args=(candidate.id,)))


class ValidationView(FormView):
    template_name = 'email_base.html'
    form_class = EmailBaseForm
    success_url = reverse_lazy('admin:candidats_candidate_changelist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])

        if candidate.date_validation_mail:
            messages.error(self.request, 'Une validation a déjà été envoyée!')

        msg_context = {
            'candidate': candidate,
            'sender': self.request.user,
        }
        form = EmailBaseForm(initial={
            'id_candidate': candidate.pk,
            'cci': self.request.user.email,
            'to': '{0};{1}'.format(candidate.interview.teacher_int.email, candidate.interview.teacher_file.email),
            'subject': "Validation de l'entretien d'admission",
            'message': loader.render_to_string('email/validation_enseignant_EDE.txt', msg_context),
            'sender': self.request.user.email,
        })
        context.update({
            'candidat': candidate,
            'form': form,
            'title': "Validation des examens par les enseignant-e-s EDE"
        })
        return context

    def form_valid(self, form):
        super().form_valid(form)
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
            candidate.date_validation_mail = timezone.now()
            candidate.save()
            messages.success(
                self.request,
                "Le message de validation a été envoyé pour le candidat {0}".format(candidate)
            )
        return redirect(reverse("admin:candidats_candidate_change", args=(candidate.id,)))


class ConvocationView(FormView):
    template_name = 'email_base.html'
    form_class = EmailBaseForm
    success_url = reverse_lazy('admin:candidats_candidate_changelist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = Candidate.objects.get(pk=self.kwargs['pk'])

        if candidate.date_convocation_mail:
            messages.error(self.request, "Une convocation a déjà été envoyée")

        my_dict = {
            0: [],
            1: ['work_certificate'], # CFC ASE
            2: ['certif_of_800_childhood', 'work_certificate'],
            3: ['certif_of_800_general', 'certif_of_800_childhood', 'work_certificate'],
            4: ['certif_of_800_general', 'certif_of_800_childhood', 'work_certificate'],
        }
        docs_required = my_dict[candidate.diploma]
        docs_required.extend([
            'registration_form', 'certificate_of_payement', 'police_record', 'cv', 'reflexive_text',
            'has_photo', 'marks_certificate'
        ])

        missing_documents = {'documents': ', '.join([
            Candidate._meta.get_field(doc).verbose_name for doc in docs_required if not getattr(candidate, doc)
        ])}

        msg_context = {
            'candidate': candidate,
            'date_lieu_examen': settings.DATE_LIEU_EXAMEN_EDE,
            'date_entretien': candidate.interview.date_formatted,
            'salle_entretien': candidate.interview.room,
            'rappel': loader.render_to_string('email/rappel_document_EDE.txt', missing_documents),
            'sender': self.request.user,
        }

        form = EmailBaseForm(initial={
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
            'title': "Convocation aux examens d'admission EDE"
        })
        return context

    def form_valid(self, form):
        super().form_valid(form)
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
            candidate.date_convocation_mail = timezone.now()
            candidate.save()
            messages.success(
                self.request,
                "Le message de convocation a été envoyé pour le candidat {0}".format(candidate)
            )
        return redirect(reverse("admin:candidats_candidate_change", args=(candidate.id,)))


def inscription_summary(request, pk):
    cand = Candidate.objects.get(pk=pk)

    filename = slugify('{0} {1}'.format(cand.last_name, cand.first_name))
    filename = '{0}.pdf'.format(filename)
    path = os.path.join(tempfile.gettempdir(), filename)

    pdf = InscriptionSummaryPDF(path)
    pdf.produce(cand)

    with open(path, mode='rb') as fh:
        response = HttpResponse(fh.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
    return response
