from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
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
    # Dropdown for copies (1 to 5 as an example)
    COPY_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    amount_of_copies = models.IntegerField(choices=COPY_CHOICES, default=1) #

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
    def clean(self):