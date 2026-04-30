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
        return self.genre_name # Makes whatever is inputted as genre name as a string when printed
    
class Book(models.Model): # Creates a model named Book made for holding book information
    
    book_id = models.AutoField(primary_key=True) # Creates an automatic gives a unique id for each book
    book_name = models.CharField(max_length=30) # Creates a charfield for strings of text with a max character length of 30 for book names
    book_author = models.CharField(max_length=30) # Creates a charfield for strings of text with a max character length of 30 for book authors
    
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, blank=True) # Creates a Many-to-one relationship by linking to the genre model, also makes it so that if a genre were deleted it would delete all books associated with that genre and allows for the genre to have a empty value 
    amount_of_copies = models.PositiveIntegerField(default=1) # Makes a positive integer field so you cant input a negative amount of copies for books, and it sets the default copy of bboks to 1

    def save(self):
        if self.amount_of_copies < 0:
            self.amount_of_copies = 0
        super().save()

    def __str__(self):
        return f"{self.book_name} by {self.book_author}"

class BookTransaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    def _set_default_return_date(self):
        if self.issue_date and not self.return_date:
            self.return_date = self.issue_date + timedelta(days=14)

    @property
    def is_issued(self):
        if not self.issue_date:
            return False
        return not BookReturn.objects.filter(transaction=self).exists()

    @property
    def label(self):
        customer_name = str(self.customer) if self.customer else 'Unknown customer'
        issue_date = self.issue_date.isoformat() if self.issue_date else 'no issue date'
        return f"{self.book.book_name} - {customer_name} - {issue_date}"

    def _get_old_transaction(self):
        return BookTransaction.objects.filter(pk=self.pk).first() if self.pk else None

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

    def __str__(self):
        return self.label


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
    