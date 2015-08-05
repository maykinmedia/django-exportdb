import mock
import rules

from django.contrib.auth.models import User
from django.test import TestCase

try:
    from django.test import override_settings
except ImportError:
    from django.test.utils import override_settings


permission_mock = mock.Mock(return_value=True)


class PermissionTests(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser('test', 'test@test.com', 'letmein')
        self.normal_user = User.objects.create_user('normal', 'normal@test.com', 'letmein')
        self.staff_user = User.objects.create_user('staff', 'staf@test.com', 'letmein')
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.client.login(username='test', password='letmein')

    def test_default_permission(self):
        self.assertTrue(
            rules.test_rule('exportdb.can_export', self.super_user)
        )

        self.assertFalse(
            rules.test_rule('exportdb.can_export', self.normal_user)
        )

        self.assertFalse(
            rules.test_rule('exportdb.can_export', self.staff_user)
        )

    @override_settings(EXPORTDB_PERMISSION=permission_mock)
    def test_permission_testings(self):
        with mock.patch('rules.is_staff', return_value=True):
            self.assertTrue(
                rules.test_rule('exportdb.can_export', self.normal_user)
            )
            permission_mock.assertCalledWith(self.normal_user)
