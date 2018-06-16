from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.views.generic import FormView

from stages.forms import EmailBaseForm


class EmailConfirmationBaseView(FormView):
    template_name = 'email_base.html'
    form_class = EmailBaseForm
    title = ''
    person_model = None  # To be defined on subclasses
    success_url = reverse_lazy('admin:candidats_candidate_changelist')
    success_message = "Le message a été envoyé pour {person}"
    error_message = "Échec d’envoi pour {person} ({err})"

    def form_valid(self, form):
        email = EmailMessage(
            subject=form.cleaned_data['subject'],
            body=form.cleaned_data['message'],
            from_email=form.cleaned_data['sender'],
            to=form.cleaned_data['to'].split(';'),
            bcc=form.cleaned_data['cci'].split(';'),
        )
        person = self.person_model.objects.get(pk=self.kwargs['pk'])
        try:
            email.send()
        except Exception as err:
            messages.error(self.request, self.error_message.format(person=person, err=err))
        else:
            self.on_success(person)
            messages.success(self.request, self.success_message.format(person=person))
        return super().form_valid(form)

    def on_success(self, person):
        """Operation to apply if message is successfully sent."""
        raise NotImplementedError("You should define an on_success method in your view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'person': self.person_model.objects.get(pk=self.kwargs['pk']),
            'title': self.title,
        })
        return context
