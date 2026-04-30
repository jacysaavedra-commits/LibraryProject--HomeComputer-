from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from decimal import Decimal
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

    def _set_default_return_date(self):
        if self.issue_date and not self.return_date:
            self.return_date = self.issue_date + timedelta(days=14)

    def _normalize_status(self):
        if self.status == 'returned':
            return
        self.status = 'issued' if self.issue_date else 'registered'

    @property
    def is_issued(self):
        return self.status == 'issued'

    @property
    def label(self):
        customer_name = str(self.customer) if self.customer else 'Unknown customer'
        issue_date = self.issue_date.isoformat() if self.issue_date else 'no issue date'
        return f"{self.book.book_name} - {customer_name} - {issue_date}"

    def _get_old_transaction(self):
        return BookTransaction.objects.filter(pk=self.pk).first() if self.pk else None

    def _update_book_stock(self, old_transaction):
        old_issued = bool(old_transaction and old_transaction.is_issued)
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

    def save(self, *args, **kwargs):
        self._set_default_return_date()
        self._normalize_status()
        self.clean()

        old_transaction = self._get_old_transaction()
        self._update_book_stock(old_transaction)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_issued:
            self.book.amount_of_copies = max(self.book.amount_of_copies + 1, 0)
            self.book.save()
        super().delete(*args, **kwargs)

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
        if self.transaction and self.transaction.status != 'issued':
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

    def save(self, *args, **kwargs):
        self.full_clean()
        self._update_late_fee()
        if self.transaction:
            self.transaction.status = 'returned'
            self.transaction.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Return for {self.transaction.book.book_name}"
    