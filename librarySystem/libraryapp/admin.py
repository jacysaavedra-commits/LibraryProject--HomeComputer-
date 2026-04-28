from django.contrib import admin
from .models import Book, Genre, Customer, BookTransaction, BookReturn

# Register your models here.

admin.site.register(Book)
admin.site.register(Genre)
admin.site.register(Customer)
admin.site.register(BookReturn)


class BookTransactionAdmin(admin.ModelAdmin):
    fields = ['customer', 'book', 'issue_date', 'return_date', 'status']
    readonly_fields = ['return_date']
    list_display = ['book', 'customer', 'issue_date', 'return_date', 'status']


admin.site.register(BookTransaction, BookTransactionAdmin)