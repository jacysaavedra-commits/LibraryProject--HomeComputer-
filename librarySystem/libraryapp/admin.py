from django.contrib import admin
from .models import Book, Genre, Customer, BookTransaction, BookReturn
# Register your models here.

admin.site.register(Book)
admin.site.register(Genre)
admin.site.register(Customer)
admin.site.register(BookTransaction)
admin.site.register(BookReturn)