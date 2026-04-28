from django.contrib import admin
from .models import Book, Genre, Customer, BookTransaction, BookReturn

# Register your models here.


class BookAdmin(admin.ModelAdmin):
    fields = ['book_name', 'book_author', 'genre', 'amount_of_copies']
    list_display = ['book_name', 'book_author', 'genre', 'amount_of_copies']


class BookTransactionAdmin(admin.ModelAdmin):
    fields = ['customer', 'book', 'issue_date', 'return_date', 'status']
    readonly_fields = ['return_date']
    list_display = ['book', 'customer', 'issue_date', 'return_date', 'status']


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(Customer)
admin.site.register(BookReturn)
admin.site.register(BookTransaction, BookTransactionAdmin)