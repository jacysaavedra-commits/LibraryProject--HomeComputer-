from django.contrib import admin  # import Django admin site helpers
from .models import Book, Genre, Customer, BookTransaction, BookReturn  # import models to register and customize in admin

# Register your models here.


class BookAdmin(admin.ModelAdmin):  # Customizes the Django admin interface for the Book model
    fields = ['book_name', 'book_author', 'genre', 'amount_of_copies']  # Specifies the fields to display in the book edit form
    list_display = ['book_name', 'book_author', 'genre', 'amount_of_copies']  # Defines the columns shown in the book list view


class BookTransactionAdmin(admin.ModelAdmin):  # Customizes the Django admin interface for the BookTransaction model
    fields = ['customer', 'book', 'issue_date', 'return_date']  # Specifies the fields to display in the transaction edit form
    readonly_fields = ['return_date']  # Makes the return_date field read-only in the admin form
    list_display = ['book', 'customer', 'issue_date', 'return_date']  # Defines the columns shown in the transaction list view


class BookReturnAdmin(admin.ModelAdmin):  # Customizes the Django admin interface for the BookReturn model
    fields = ['transaction', 'actual_return_date', 'late_status', 'late_fee', 'transaction_description']  # Specifies the fields to display in the return edit form
    readonly_fields = ['late_status', 'late_fee', 'transaction_description']  # Makes computed fields read-only in the admin
    list_display = ['transaction_description', 'actual_return_date', 'late_status', 'late_fee']  # Defines the columns shown in the return list view

    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # Overrides the default foreign key field to customize available options
        if db_field.name == 'transaction':  # Specifically targets the transaction foreign key field
            kwargs['queryset'] = BookTransaction.objects.filter(issue_date__isnull=False, book_return__isnull=True)  # Filters queryset to only include issued transactions without returns
        return super().formfield_for_foreignkey(db_field, request, **kwargs)  # Calls the parent method for standard behavior on other fields

    def late_status(self, obj):  # Defines a custom display method for the late status in the admin list
        return 'Yes' if obj.is_late else 'No'  # Returns a user-friendly string based on the boolean late flag
    late_status.short_description = 'Late?'  # Sets the column header text for the late status field

    def transaction_description(self, obj):  # Creates a custom display method for transaction details in the admin
        if not obj.transaction:  # Checks if the return has an associated transaction
            return 'N/A'  # Returns a placeholder if no transaction exists
        transaction = obj.transaction  # Retrieves the linked transaction object
        customer_name = str(transaction.customer) if transaction.customer else 'Unknown customer'  # Safely gets the customer name or defaults to unknown
        return f"{transaction.book.book_name} - {customer_name} - {transaction.issue_date}"  # Formats and returns the book, customer, and date information
    transaction_description.short_description = 'Issued Book (Customer - Issue Date)'  # Defines the header for the transaction description column


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(Customer)
admin.site.register(BookReturn, BookReturnAdmin)
admin.site.register(BookTransaction, BookTransactionAdmin)