from django.contrib import admin

from .models import Book, Category, Author

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Author)
