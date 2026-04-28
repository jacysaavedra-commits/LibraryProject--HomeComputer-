from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
# username/password for superuser - (jacygravy27,jacy2705)
# Create your models here.

class Customer(models.Model):
    student_id = models.AutoField(primary_key=True) #
    first_name = models.CharField(max_length=30) # 
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Genre(models.Model):
    genre_name = models.CharField(max_length=30)

    def __str__(self):
        return self.genre_name
    
class Book(models.Model):
    
    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=30)
    book_author = models.CharField(max_length=30)
    
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, blank=True)
    amount_of_copies = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.amount_of_copies < 0:
            self.amount_of_copies = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book_name} by {self.book_author}"

class BookTransaction(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered/Available'),
        ('issued', 'Issued'),
        ('returned', 'Returned'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')

    def save(self, *args, **kwargs):
        if self.issue_date and not self.return_date:
            self.return_date = self.issue_date + timedelta(days=14)

        old_transaction = None
        if self.pk:
            try:
                old_transaction = BookTransaction.objects.get(pk=self.pk)
            except BookTransaction.DoesNotExist:
                old_transaction = None

        old_status = old_transaction.status if old_transaction else None
        old_issue_date = old_transaction.issue_date if old_transaction else None
        old_book = old_transaction.book if old_transaction else None

        old_issued = bool(old_transaction and (old_status == 'issued' or (old_issue_date and old_status != 'returned')))
        new_issued = bool(self.status == 'issued' or (self.issue_date and self.status != 'returned'))

        decrement_stock = False
        increment_stock = False
        restore_old_book = False

        if old_book and old_book != self.book and old_issued:
            restore_old_book = True

        if new_issued and (not old_issued or (old_book and old_book != self.book)):
            decrement_stock = True
        elif old_issued and not new_issued:
            increment_stock = True

        if restore_old_book and old_book is not None:
            old_book.amount_of_copies = max(old_book.amount_of_copies + 1, 0)
            old_book.save()

        if decrement_stock:
            if self.book.amount_of_copies <= 0:
                raise ValidationError('No copies available for this book.')
            self.book.amount_of_copies -= 1
            self.book.save()

        if increment_stock and not restore_old_book:
            self.book.amount_of_copies = max(self.book.amount_of_copies + 1, 0)
            self.book.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status == 'issued':
            self.book.amount_of_copies = max(self.book.amount_of_copies + 1, 0)
            self.book.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.book.book_name} - {self.status}"
    
class BookReturn(models.Model):
    transaction = models.OneToOneField(
        BookTransaction, 
        on_delete=models.CASCADE, 
        related_name='book_return'
    )
    actual_return_date = models.DateField(null=True, blank=True)

    def __claire__(self):
        return f"Return for {self.transaction.book.book_name}"
    