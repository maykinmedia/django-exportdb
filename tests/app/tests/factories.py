import factory
import factory.fuzzy

from ..models import Author, Book, Category


class AuthorFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=8)

    class Meta:
        model = Author


class BookFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=15)
    author = factory.SubFactory(AuthorFactory)

    class Meta:
        model = Book


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=15)

    class Meta:
        model = Category
