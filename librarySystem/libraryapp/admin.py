from django.contrib import admin  # import Django admin site helpers
from .models import Book, Genre, Customer, BookTransaction, BookReturn  # import models to register and customize in admin

# Register your models here.


class BookAdmin(admin.ModelAdmin):  # This creates a custom admin configuration for the Book model to control how books are displayed and edited in the admin interface
    fields = ['book_name', 'book_author', 'genre', 'amount_of_copies']  # This specifies the fields to display in the book edit form, allowing control over the input fields
    list_display = ['book_name', 'book_author', 'genre', 'amount_of_copies']  # This defines the columns shown in the book list view, making it easier to browse books


class BookTransactionAdmin(admin.ModelAdmin):  # This creates a custom admin configuration for the BookTransaction model to manage transaction records effectively
    fields = ['customer', 'book', 'issue_date', 'return_date']  # This specifies the fields to display in the transaction edit form, including key transaction details
    readonly_fields = ['return_date']  # This makes the return_date field read-only in the admin form, preventing manual changes
    list_display = ['book', 'customer', 'issue_date', 'return_date']  # This defines the columns shown in the transaction list view, showing essential transaction info


class BookReturnAdmin(admin.ModelAdmin):  # This creates a custom admin configuration for the BookReturn model to handle return records properly
    fields = ['transaction', 'actual_return_date', 'late_status', 'late_fee', 'transaction_description']  # This specifies the fields to display in the return edit form, including return details and calculations
    readonly_fields = ['late_status', 'late_fee', 'transaction_description']  # This makes computed fields read-only in the admin, as they are auto-calculated
    list_display = ['transaction_description', 'actual_return_date', 'late_status', 'late_fee']  # This defines the columns shown in the return list view, summarizing return information

    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # This overrides the default foreign key field to customize available options for the transaction field
        if db_field.name == 'transaction':  # This specifically targets the transaction foreign key field to filter options
            kwargs['queryset'] = BookTransaction.objects.filter(issue_date__isnull=False, book_return__isnull=True)  # This filters the queryset to only include issued transactions without returns, preventing invalid selections
        return super().formfield_for_foreignkey(db_field, request, **kwargs)  # This calls the parent method for standard behavior on other fields

    def late_status(self, obj):  # This creates a custom display method for the late status in the admin list, making it user-friendly
        return 'Yes' if obj.is_late else 'No'  # This returns a user-friendly string based on the boolean late flag, improving readability
    late_status.short_description = 'Late?'  # This sets the column header text for the late status field in the list view

    def transaction_description(self, obj):  # This creates a custom display method for transaction details in the admin, combining related information
        if not obj.transaction:  # This checks if the return has an associated transaction to handle missing data
            return 'N/A'  # This returns a placeholder if no transaction exists, avoiding errors
        transaction = obj.transaction  # This retrieves the linked transaction object for data access
        customer_name = str(transaction.customer) if transaction.customer else 'Unknown customer'  # This safely gets the customer name or defaults to unknown, handling null customers
        return f"{transaction.book.book_name} - {customer_name} - {transaction.issue_date}"  # This formats and returns the book, customer, and date information for display
    transaction_description.short_description = 'Issued Book (Customer - Issue Date)'  # This defines the header for the transaction description column in the list view


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(Customer)
admin.site.register(BookReturn, BookReturnAdmin)
admin.site.register(BookTransaction, BookTransactionAdmin)