from __future__ import unicode_literals

from django.test import TestCase

from import_export.resources import ModelResource

from exportdb.exporter import get_export_models, get_resource_for_model, Exporter

from ..models import Author, Book, Category
from .factories import AuthorFactory, BookFactory, CategoryFactory


class ExporterTests(TestCase):

    def test_get_export_models(self):
        """
        Test that `get_export_models` returns the expected list of installed models.
        """
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib.sites.models import Site
        from django.contrib.sessions.models import Session
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType

        export_models = set(get_export_models(admin_only=False))
        expected_export_models = set([
            User, Group, Permission, Site, Session, LogEntry, ContentType,
            Author, Book, Category
        ])

        self.assertEqual(export_models, expected_export_models)

        export_models_admin = set(get_export_models(admin_only=True))
        expected_export_models_admin = set([
            User, Group, Site,
            Author, Book, Category
        ])

        self.assertEqual(export_models_admin, expected_export_models_admin)

    def test_get_resource_for_model(self):
        resource = get_resource_for_model(Author)
        self.assertIsInstance(resource, ModelResource)
        self.assertEqual(resource.Meta.model, Author)

    def test_exporter(self):
        authors = AuthorFactory.create_batch(3)
        categories = CategoryFactory.create_batch(3)

        books = BookFactory.create_batch(2, author=authors[0])
        books += BookFactory.create_batch(3, author=authors[1])
        books += BookFactory.create_batch(4, author=authors[2])

        books[0].categories = categories[:2]  # 2 categories
        books[-1].categories = categories[2:]  # 1 category

        resources = [get_resource_for_model(model) for model in [Author, Book, Category]]
        exporter = Exporter(resources)
        book = exporter.export()

        sheets = book.sheets()
        self.assertEqual(len(sheets), 3)
        titles = set([sheet.title for sheet in sheets])
        expected_titles = set(['authors (app.Author)', 'books (app.Book)', 'categorys (app.Category)'])
        self.assertEqual(titles, expected_titles)

        # test that all the data is there as expected
        author_sheet, book_sheet, category_sheet = sheets

        self.assertEqual(len(author_sheet), 3)  # 3 authors
        self.assertEqual(len(author_sheet[0]), 3)  # id, name, birthday

        self.assertEqual(len(book_sheet), 9)  # 3 authors
        # id, name, author_id, author_email, imported, published, price, categories
        self.assertEqual(len(book_sheet[0]), 8)
        self.assertEqual(book_sheet[0][2], authors[0].id)
        self.assertEqual(book_sheet[0][-1], ','.join([str(cat.id) for cat in categories[:2]]))

        self.assertEqual(len(category_sheet), 3)
        self.assertEqual(len(category_sheet[0]), 2)  # id, name
