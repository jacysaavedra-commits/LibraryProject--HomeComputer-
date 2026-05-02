from django.db import models  # import Django ORM model base classes
from django.core.exceptions import ValidationError  # import validation error for model checks
from datetime import timedelta  # import timedelta for date calculations
from decimal import Decimal  # import Decimal for precise money handling
# username/password for superuser - (jacygravy27,jacy2705)
# Create your models here.

class Customer(models.Model): # Creates a model named Customer made for holding customer information
    student_id = models.AutoField(primary_key=True) # Creates an automatic gives a unique id for each customer 
    first_name = models.CharField(max_length=30) # Creates a charfield for strings of text with a max character length of 30 for first names
    last_name = models.CharField(max_length=30) # Creates a charfield for strings of text with a max character length of 30 for last names

    def __str__(self): # Makes it so that it displays first and last name as a string instead of the default object name when printed
        return f"{self.first_name} {self.last_name}" # Makes whatever is inputted as first and last name as a string 
    
class Genre(models.Model): # Creates a model named Genre made for holding genre information
    genre_name = models.CharField(max_length=30) # Creates a charfield for strings of text with a max character length of 30 for genre names

    def __str__(self): # Displays the genre inputted as a string 
        return self.genre_name # Makes whatever is inputted as genre name as a string 
    
class Book(models.Model): # Creates a model named Book made for holding book information
    
    book_id = models.AutoField(primary_key=True) # Creates an automatic gives a unique id for each book
    book_name = models.CharField(max_length=30) # Creates a charfield for strings of text with a max character length of 30 for book names
    book_author = models.CharField(max_length=30) # Creates a charfield for strings of text with a max character length of 30 for book authors
    
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, blank=True) # Creates a Many-to-one relationship by linking to the genre model, also makes it so that if a genre were deleted it would delete all books associated with that genre and allows for the genre to have a empty value 
    amount_of_copies = models.PositiveIntegerField(default=1) # Makes a positive integer field so you cant input a negative amount of copies for books, and it sets the default copy of bboks to 1

    def save(self): # This overrides the built in Django save method so that in Book model when you save a book the code below happens
        if self.amount_of_copies < 0: # Checks if the amount of copies is less than 0
            self.amount_of_copies = 0 # if the amount of copies is set as a negative number it will automatically set to 0
        super().save() # Saves all the changes saved to the book model in the database

    def __str__(self): # Displays the book name and author as a string 
        return f"{self.book_name} by {self.book_author}" # Makes whatever is inputted as book name and author as a string 

class BookTransaction(models.Model): # Creates a model named BookTransaction made for holding book transaction information
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True) # Creates a Many-to-one relationship with the customer model and all makes it so that when a customer is deleted their transaction history is also deleted
    book = models.ForeignKey(Book, on_delete=models.CASCADE) # Creates a Many-to-one relationship with the book model and makes it so that when a book is deleted all transactions associated with that book are also deleted
    issue_date = models.DateField(null=True, blank=True) #Creates a datefield so you can choose when the book was issued out
    return_date = models.DateField(null=True, blank=True) # Creates a datefield for when customer returns their book

    def _set_default_return_date(self): # This creates a defined function for setting the return date automatically
        if self.issue_date and not self.return_date: # If there is an issue date but no return date the following code will run
            self.return_date = self.issue_date + timedelta(days=14) # This will automatically set the return date to 14 days after the issue date

    @property # Allows you to have accessible functions that dont require brackets () to call them 
    def is_issued(self): # this creates a Funciion for checking if a books is issued out
        if not self.issue_date: # If the issue date is empty then the following code will run
            return False # Tells the program that a book isn't issued out when there's no issue date
        return not BookReturn.objects.filter(transaction=self).exists() # This checks in the BookReturn model meaning if a similar book was returned then it would return false but if it wasn't returned it would return true meaning the book is still issued out

    @property # This allows you to have accessible functions that dont require brackets () to call them
    def label(self): # This creates a function for displaying the book transaction information in a specific format
        customer_name = str(self.customer) if self.customer else 'Unknown customer' # this will print the customer name if there is a customer associated with the transaction but if there isn't it will state unknown customer instead
        issue_date = self.issue_date.isoformat() if self.issue_date else 'no issue date' # This checks if there is an issue date and if there isn't then it will state that there is no issue date
        return f"{self.book.book_name} - {customer_name} - {issue_date}" # This will display the book name, customer name and the issue date in a nice line (show in admin panel)

    def _get_old_transaction(self): # This function is for getting any old transaction information before saved 
        return BookTransaction.objects.filter(pk=self.pk).first() if self.pk else None # It checks if there is an issue record with the same primary key if there isn't then it the program will return none but if there is a record then it will compare the old transaction with the new transaction to see if there are any changes that need to be made to the book stock

    def _update_book_stock(self, old_transaction): # This function is for updating the book stock based on the changes made to the transaction
        old_returned = BookReturn.objects.filter(transaction=old_transaction).exists() if old_transaction else False # This line checks if a book return record exists for the old transaction, if there is then it means the book was returned and if there isn't then it means the book is still issued out
        old_issued = bool(old_transaction and old_transaction.issue_date and not old_returned) # IN this line if there is an old transaction with an issue date and there isn't a book return record then it means the book was issued out in the old transaction
        new_issued = self.is_issued # This calls the is_issued function to see if the book has been issued out in the new transaction
        old_book = old_transaction.book if old_transaction else None # This code reaches into the book field to see if there was an old book associated with the old transaction, if there isn't then it will return none but if there is then it will compare the old book with the new book to see if there are any changes that need to be made to the book stock

        if old_book and old_book != self.book and old_issued: # This line prevents the book stock from being messed if changes are made to the transaction that don't involve the book being issued out, for example if you change the customer name or the issue date it won't change the book stock but if you change the book that is being issued out then it will update the stock of both the old and new book accordingly
            old_book.amount_of_copies = max(old_book.amount_of_copies + 1, 0) # This line increases the stock of the old book by 1 since the book is no longer issued out in the new transaction, it also makes sure that the amount of copies doesn't go below 0
            old_book.save() # This saves the changes made to the book stock of the old book in the database

        if new_issued and (not old_issued or (old_book and old_book != self.book)):  # Handles cases where the book is now issued either newly or switched to a different book
            if self.book.amount_of_copies <= 0:  # Verifies that there are available copies before issuing
                raise ValidationError('No copies available for this book.')  # Prevents issuing a book with no remaining stock
            self.book.amount_of_copies -= 1  # Reduces the available copies by 1 for the issued book
            self.book.save()  # Updates the book's stock in the database
        elif old_issued and not new_issued:  # Manages scenarios where a previously issued book is no longer issued
            self.book.amount_of_copies = max(self.book.amount_of_copies + 1, 0)  # Increases stock by 1, ensuring it doesn't go below zero
            self.book.save()  # Saves the adjusted stock level

    def clean(self):
        if self.issue_date and self.return_date and self.return_date < self.issue_date:  # Checks if both issue and return dates are set and ensures return date is not before issue date
            raise ValidationError('Return date cannot be before issue date.')  # Raises a validation error to prevent illogical date sequences

    def save(self):
        self._set_default_return_date()  # Automatically sets a default return date 14 days after issue if not specified
        self.clean()  # Validates the transaction data for consistency
        old_transaction = self._get_old_transaction()  # Retrieves the existing transaction record if updating
        self._update_book_stock(old_transaction)  # Adjusts book stock levels based on transaction changes
        super().save()  # Saves the transaction record to the database

    def delete(self):
        if self.is_issued:  # Checks if the book is currently issued out
            self.book.amount_of_copies = max(self.book.amount_of_copies + 1, 0)  # Restores one copy to stock upon transaction deletion
            self.book.save()  # Persists the updated stock count
        super().delete()  # Removes the transaction record from the database
    def __str__(self): # This will help to display the book name, customer name and the issue date in a nice line (show in admin panel)
        return self.label # This will display the book name, customer name and the issue date in a nice line (show in admin panel)


class BookReturn(models.Model):
    transaction = models.OneToOneField(  # Defines a one-to-one relationship linking each return record to exactly one book transaction
        BookTransaction,  # Specifies the BookTransaction model as the related model for this field
        on_delete=models.CASCADE,  # Ensures that if the associated transaction is deleted, this return record is also deleted
        related_name='book_return'  # Allows accessing the return from a transaction instance using .book_return
    )
    actual_return_date = models.DateField(null=True, blank=True)  # Stores the date when the book was actually returned, allowing null values for optional entry
    is_late = models.BooleanField(default=False)  # Boolean flag indicating whether the return is considered late, defaulting to False
    late_fee = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))  # Decimal field for storing the calculated late fee with up to 6 digits and 2 decimal places

    def _validate_transaction(self):
        if self.transaction and not self.transaction.issue_date:  # Checks if a transaction is linked and has no issue date set to prevent invalid returns
            raise ValidationError({'transaction': 'Can only return books that have been issued.'})  # Raises a validation error if trying to return a book that was never issued

    def _validate_dates(self):
        if self.actual_return_date and self.transaction and self.transaction.issue_date:  # Verifies that actual return date, transaction, and issue date all exist before comparing
            if self.actual_return_date < self.transaction.issue_date:  # Ensures the actual return date is not earlier than the issue date
                raise ValidationError({'actual_return_date': 'Actual return date cannot be before issue date.'})  # Raises an error if the return date precedes the issue date

    def _update_late_fee(self):
        if self.actual_return_date and self.transaction.return_date:  # Checks if both the actual return date and expected return date are available
            days_late = max(0, (self.actual_return_date - self.transaction.return_date).days)  # Calculates days late by subtracting expected return date from actual, ensuring non-negative result
            self.is_late = days_late > 0  # Sets the late flag to True if there are any days late, otherwise False
            self.late_fee = Decimal(days_late * 5)  # Computes the late fee at $5 per day late using the calculated days
        else:  # Handles cases where required dates are missing
            self.is_late = False  # Resets late status to False when dates are incomplete
            self.late_fee = Decimal('0.00')  # Sets late fee to zero when calculation cannot be performed

    def clean(self):
        self._validate_transaction()  # Calls the transaction validation method to check for valid return conditions
        self._validate_dates()  # Calls the date validation method to ensure chronological order

    def save(self):
        is_new_return = self._state.adding  # Determines if this is a newly created return record by checking the model state
        self.full_clean()  # Performs full validation on all fields before saving to the database
        self._update_late_fee()  # Invokes the method to calculate and update the late fee based on dates
        if is_new_return and self.transaction and self.transaction.book:  # Checks if this is a new return with an associated transaction and book
            self.transaction.book.amount_of_copies = max(self.transaction.book.amount_of_copies + 1, 0)  # Increases the book's available copies by 1 upon return, preventing negative stock
            self.transaction.book.save()  # Saves the updated book stock to the database
        super().save()  # Calls the parent save method to persist the return record

    def __str__(self):
        return f"Return for {self.transaction.book.book_name}"  # Returns a string representation showing the book name for this return
    