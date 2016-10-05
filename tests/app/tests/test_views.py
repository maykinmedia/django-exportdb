from __future__ import unicode_literals

from pkg_resources import parse_version

import mock
from datetime import date

import django
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from exportdb.compat import jquery_in_vendor
from exportdb.exporter import Exporter


try:
    from django.test import override_settings
except ImportError:
    from django.test.utils import override_settings


class ExportForm(forms.Form):
    from_date = forms.DateField(label='from date')


class ViewTests(TestCase):

    confirm_url = reverse('exportdb_export')

    def setUp(self):
        self.user = User.objects.create_superuser('test', 'test@test.com', 'letmein')
        self.client.login(username='test', password='letmein')

    def test_confirm_page(self):
        response = self.client.get(self.confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['models']), set([
            _('session (sessions.Session)'),
            _('log entry (admin.LogEntry)'),
            _('author (app.Author)'),
            _('category (app.Category)'),
            _('book (app.Book)'),
            _('site (sites.Site)'),
            _('permission (auth.Permission)'),
            _('group (auth.Group)'),
            _('user (auth.User)'),
            _('content type (contenttypes.ContentType)')
        ]))

        if jquery_in_vendor():
            self.assertContains(response, '/static/admin/js/vendor/jquery/jquery.js', count=1)
        else:
            self.assertContains(response, '/static/admin/js/jquery.js', count=1)

        self.assertIsInstance(response.context['form'], forms.Form)

    @override_settings(EXPORTDB_CONFIRM_FORM='tests.app.tests.test_views.ExportForm')
    def test_custom_confirm_form(self):
        response = self.client.get(self.confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].__class__.__name__, 'ExportForm')
        self.assertContains(response, 'from date', count=1)

    @override_settings(EXPORTDB_CONFIRM_FORM='tests.app.tests.test_views.ExportForm', CELERY_ALWAYS_EAGER=True)
    def test_form_data_passed_to_exporter(self):
        """
        Test that form.cleaned_data is passed to the exporter and exporter resources
        """
        class AsyncResult(object):
            id = 'foo'

        def post_confirm():
            response = self.client.post(self.confirm_url, {'from_date': date.today()})
            self.assertEqual(response.status_code, 200)
            return response

        with mock.patch('exportdb.views.export.delay') as mocked_export:
            mocked_export.return_value = AsyncResult()
            post_confirm()

            self.assertEqual(mocked_export.call_count, 1)
            self.assertEqual(mocked_export.call_args, mock.call(
                Exporter, tenant=None, from_date=date.today()
            ))
