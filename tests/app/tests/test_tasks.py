from __future__ import unicode_literals

import mock

from django.test import TestCase

from tablib import Databook, Dataset

from exportdb.exporter import Exporter, get_export_models


class TaskTests(TestCase):

    @mock.patch('exportdb.exporter.Exporter.export')
    @mock.patch('exportdb.tasks.get_resource_for_model')
    def test_kwargs_forwarded(self, resource_for_model, mocked_export):
        """
        Test that kwargs passed to `export` are forwarded to the ModelResource
        for export.
        """
        from exportdb.tasks import export

        book = Databook()
        book.add_sheet(Dataset())
        mocked_export.return_value = book

        kwargs = {'foo': 'bar', 'baz': 10}
        export(Exporter, **kwargs)

        export_models = get_export_models()
        for i, export_model in enumerate(export_models):
            self.assertEqual(
                resource_for_model.call_args_list[i],
                mock.call(export_model, foo='bar', baz=10)
            )
