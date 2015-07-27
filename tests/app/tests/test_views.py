from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

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
        self.assertIsInstance(response.context['form'], forms.Form)

    @override_settings(EXPORTDB_CONFIRM_FORM='tests.app.tests.test_views.ExportForm')
    def test_custom_confirm_form(self):
        response = self.client.get(self.confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].__class__.__name__, 'ExportForm')
        self.assertContains(response, 'from date', count=1)
