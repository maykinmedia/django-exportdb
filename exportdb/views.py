import json
from pkg_resources import parse_version

import django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db import connection
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, View

import rules
from celery.result import AsyncResult

from .compat import import_string, jquery_in_vendor
from .exporter import get_export_models, Exporter
from .tasks import export


EXPORTDB_EXPORT_KEY = 'exportdb_export'


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
    form_class = None
    template_name = 'exportdb/confirm.html'
    exporter_class = Exporter

    def get_form_class(self):
        """
        Return the form class to use for the confirmation form.

        In the method instead of the attribute, since it's not guaranteed that
        the appconf is loaded in Django versions < 1.7.
        """
        if self.form_class is None:
            self.form_class = import_string(settings.EXPORTDB_CONFIRM_FORM)
        return self.form_class

    def get_export_models(self, **kwargs):
        kwargs.setdefault('admin_only', False)
        try:
            return get_export_models(**kwargs)
        except ImproperlyConfigured as e:
            messages.error(self.request, e.args[0])
        return []

    def get_exporter_class(self):
        return self.exporter_class

    def get_context_data(self, **kwargs):
        context = super(ExportView, self).get_context_data(**kwargs)
        context['title'] = _('Export database')
        context['jquery_in_vendor'] = jquery_in_vendor()
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
        # multi-tenant support
        tenant = getattr(connection, 'tenant', None)
        # start actual export and render the template
        async_result = export.delay(self.get_exporter_class(), tenant=tenant, **form.cleaned_data)
        self.request.session[EXPORTDB_EXPORT_KEY] = async_result.id
        context = self.get_context_data(export_running=True)
        self.template_name = 'exportdb/in_progress.html'
        return self.render_to_response(context)


class ExportPendingView(ExportPermissionMixin, View):

    def json_response(self, data):
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get(self, request, *args, **kwargs):
        async_result = AsyncResult(request.session.get(EXPORTDB_EXPORT_KEY))
        if not async_result:
            return self.json_response({'status': 'FAILURE', 'progress': 0})

        if async_result.state == 'PROGRESS':
            try:
                progress = async_result.info['progress']
                if progress > 0.99:
                    progress = 0.99
            except:
                progress = 0.01
        elif async_result.ready():
            progress = 1
        else:
            progress = 1

        content = {
            'status': async_result.state,
            'progress': progress,
            'file': async_result.result if async_result.ready() else None
        }
        return self.json_response(content)
