from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView


class ExportView(FormView):
    form_class = forms.Form
    template_name = 'exportdb/confirm.html'

    def get_context_data(self, **kwargs):
        context = super(ExportView, self).get_context_data(**kwargs)
        context['title'] = _('Export database')
        return context
