from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from decimal import Decimal
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

    def _update_book_stock(self, old_transaction):
        old_returned = BookReturn.objects.filter(transaction=old_transaction).exists() if old_transaction else False
        old_issued = bool(old_transaction and old_transaction.issue_date and not old_returned)
        new_issued = self.is_issued
        old_book = old_transaction.book if old_transaction else None

        if old_book and old_book != self.book and old_issued:
            old_book.amount_of_copies = max(old_book.amount_of_copies + 1, 0)
            old_book.save()

        if new_issued and (not old_issued or (old_book and old_book != self.book)):
            if self.book.amount_of_copies <= 0:
                raise ValidationError('No copies available for this book.')
            self.book.amount_of_copies -= 1
            self.book.save()
        elif old_issued and not new_issued:
            self.book.amount_of_copies = max(self.book.amount_of_copies + 1, 0)
            self.book.save()

    def clean(self):
        if self.issue_date and self.return_date and self.return_date < self.issue_date:
            raise ValidationError('Return date cannot be before issue date.')

    def save(self):
        self._set_default_return_date()
        self.clean()

        old_transaction = self._get_old_transaction()
        self._update_book_stock(old_transaction)

        super().save()

    def delete(self):
        if self.is_issued:
            self.book.amount_of_copies = max(self.book.amount_of_copies + 1, 0)
            self.book.save()
        super().delete()

    def __str__(self): # This will help to display the book name, customer name and the issue date in a nice line (show in admin panel)
        return self.label # This will display the book name, customer name and the issue date in a nice line (show in admin panel)


class BookReturn(models.Model):
    transaction = models.OneToOneField(
        BookTransaction,
        on_delete=models.CASCADE,
        related_name='book_return'
    )
    actual_return_date = models.DateField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    late_fee = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))

    def _validate_transaction(self):
        if self.transaction and not self.transaction.issue_date:
            raise ValidationError({'transaction': 'Can only return books that have been issued.'})

    def _validate_dates(self):
        if self.actual_return_date and self.transaction and self.transaction.issue_date:
            if self.actual_return_date < self.transaction.issue_date:
                raise ValidationError({'actual_return_date': 'Actual return date cannot be before issue date.'})

    def _update_late_fee(self):
        if self.actual_return_date and self.transaction.return_date:
            days_late = max(0, (self.actual_return_date - self.transaction.return_date).days)
            self.is_late = days_late > 0
            self.late_fee = Decimal(days_late * 5)
        else:
            self.is_late = False
            self.late_fee = Decimal('0.00')

    def clean(self):
        self._validate_transaction()
        self._validate_dates()

    def save(self):
        is_new_return = self._state.adding
        self.full_clean()
        self._update_late_fee()
        if is_new_return and self.transaction and self.transaction.book:
            self.transaction.book.amount_of_copies = max(self.transaction.book.amount_of_copies + 1, 0)
            self.transaction.book.save()
        super().save()

    def __str__(self):
        return f"Return for {self.transaction.book.book_name}"
    