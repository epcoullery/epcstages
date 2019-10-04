import io
import os
import tempfile
import zipfile

from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import FileResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, View

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


class PDFBaseView(View):
    pdf_class = None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        buff = io.BytesIO()
        pdf = self.pdf_class(buff, obj)
        pdf.produce()
        buff.seek(0)
        return FileResponse(buff, as_attachment=True, filename=self.filename(obj))


class ZippedFilesBaseView(View):
    """A base class to return a .zip file containing a compressed list of files."""
    filename = 'to_be_defined.zip'

    def generate_files(self):
        """Generator yielding (file_name, file_data) tuples."""
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        tmp_file = tempfile.NamedTemporaryFile()
        with zipfile.ZipFile(tmp_file, mode='w', compression=zipfile.ZIP_DEFLATED) as filezip:
            for file_name, file_data in self.generate_files():
                filezip.writestr(file_name, file_data)

        with open(filezip.filename, mode='rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.filename
        return response
