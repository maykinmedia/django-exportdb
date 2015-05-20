import mimetypes
import os

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from django.http import CompatibleStreamingHttpResponse

import rules

from .exporter import get_export_models, get_resource_for_model, Exporter
from .settings import EXPORT_ROOT


class ExportPermissionMixin(object):
    """
    Check permissions
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not rules.test_rule('exportdb.can_export', request.user):
            raise PermissionDenied
        return super(ExportPermissionMixin, self).dispatch(request, *args, **kwargs)


class ExportView(ExportPermissionMixin, FormView):
    form_class = forms.Form
    template_name = 'exportdb/confirm.html'
    exporter_class = Exporter

    def get_export_models(self, **kwargs):
        kwargs.setdefault('admin_only', False)
        return get_export_models(**kwargs)

    def get_exporter(self, resources):
        return self.exporter_class(resources)

    def get_context_data(self, **kwargs):
        context = super(ExportView, self).get_context_data(**kwargs)
        context['title'] = _('Export database')
        context['models'] = [
            u'{name} ({app}.{model})'.format(
                name=model._meta.verbose_name,
                app=model._meta.app_label,
                model=model.__name__
            )
            for model in self.get_export_models()
        ]
        return context

    def form_valid(self, form):
        models = self.get_export_models()
        resources = [get_resource_for_model(model) for model in models]

        format = 'xlsx'  # TODO: form

        filename = u'export-{timestamp}.{ext}'.format(
            timestamp=timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            ext=format
        )

        exporter = self.get_exporter(resources)
        exporter.export_to = os.path.join(EXPORT_ROOT, filename)
        outfile = exporter.export(format=format)

        content_type, encoding = mimetypes.guess_type(outfile.name)
        content_type = content_type or 'application/octet-stream'
        response = CompatibleStreamingHttpResponse(
            open(outfile.name, 'rb'),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = u'attachment; filename={}'.format(filename)
        return response
