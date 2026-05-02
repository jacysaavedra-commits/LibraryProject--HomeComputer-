from django.contrib import admin  # import Django admin site helpers
from .models import Book, Genre, Customer, BookTransaction, BookReturn  # import models to register and customize in admin

# Register your models here.


class BookAdmin(admin.ModelAdmin):
    fields = ['book_name', 'book_author', 'genre', 'amount_of_copies']  # fields shown in the book edit page
    list_display = ['book_name', 'book_author', 'genre', 'amount_of_copies']  # fields shown in the book admin list view


class BookTransactionAdmin(admin.ModelAdmin):
    fields = ['customer', 'book', 'issue_date', 'return_date']  # fields shown in the transaction edit page
    readonly_fields = ['return_date']  # make return_date readonly in the admin form
    list_display = ['book', 'customer', 'issue_date', 'return_date']  # show key transaction fields in the list view


class BookReturnAdmin(admin.ModelAdmin):
    fields = ['transaction', 'actual_return_date', 'late_status', 'late_fee', 'transaction_description']
    readonly_fields = ['late_status', 'late_fee', 'transaction_description']
    list_display = ['transaction_description', 'actual_return_date', 'late_status', 'late_fee']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'transaction':
            kwargs['queryset'] = BookTransaction.objects.filter(issue_date__isnull=False, book_return__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def late_status(self, obj):
        return 'Yes' if obj.is_late else 'No'
    late_status.short_description = 'Late?'

    def transaction_description(self, obj):
        if not obj.transaction:
            return 'N/A'
        transaction = obj.transaction
        customer_name = str(transaction.customer) if transaction.customer else 'Unknown customer'
        return f"{transaction.book.book_name} - {customer_name} - {transaction.issue_date}"
    transaction_description.short_description = 'Issued Book (Customer - Issue Date)'


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(Customer)
admin.site.register(BookReturn, BookReturnAdmin)
admin.site.register(BookTransaction, BookTransactionAdmin)