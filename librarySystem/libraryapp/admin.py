from django.contrib import admin
from .models import Book, Genre, Customer, BookTransaction, BookReturn

# Register your models here.


class BookAdmin(admin.ModelAdmin):
    fields = ['book_name', 'book_author', 'genre', 'amount_of_copies']
    list_display = ['book_name', 'book_author', 'genre', 'amount_of_copies']


class BookTransactionAdmin(admin.ModelAdmin):
    fields = ['customer', 'book', 'issue_date', 'return_date']
    readonly_fields = ['return_date']
    list_display = ['book', 'customer', 'issue_date', 'return_date']


class BookReturnAdmin(admin.ModelAdmin):
    fields = ['transaction', 'actual_return_date', 'late_status', 'late_fee', 'transaction_info']
    readonly_fields = ['late_status', 'late_fee', 'transaction_info']
    list_display = ['get_transaction_display', 'actual_return_date', 'late_status', 'late_fee']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'transaction':
            kwargs['queryset'] = BookTransaction.objects.filter(status='issued')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def late_status(self, obj):
        return 'Yes' if obj.is_late else 'No'
    late_status.short_description = 'Late?'

    def transaction_info(self, obj):
        if obj.transaction:
            return f"{obj.transaction.book.book_name} - {obj.transaction.customer.first_name} {obj.transaction.customer.last_name} - Issued: {obj.transaction.issue_date}"
        return "N/A"
    transaction_info.short_description = "Transaction Details"
    
    def get_transaction_display(self, obj):
        if obj.transaction:
            return f"{obj.transaction.book.book_name} - {obj.transaction.customer.first_name} {obj.transaction.customer.last_name} - {obj.transaction.issue_date}"
        return "N/A"
    get_transaction_display.short_description = "Book Issued To (Issue Date)"


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(Customer)
admin.site.register(BookReturn, BookReturnAdmin)
admin.site.register(BookTransaction, BookTransactionAdmin)