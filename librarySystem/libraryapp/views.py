from django.shortcuts import get_object_or_404, redirect, render
from .models import Book, Customer, BookTransaction
from django.core.exceptions import ValidationError

# Create your views here.
def home(request):
    return render(request, 'home.html')

def books(request):
    return render(request, 'books.html')

def book_list(request):
    q = request.GET.get('q', '')
    if q:
        books = Book.objects.filter(book_name__icontains=q)
    else:
        books = Book.objects.all()
    return render(request, 'books.html', {'books': books, 'query': q})

def authors(request):
    books = Book.objects.all()
    return render(request, 'authors.html', {'books': books})

def book_detail(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    return render(request, 'book_detail.html', {'book': book})

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the password matches
        if password != confirm_password:
            return render(request, "register.html", {
                "errors": {"password": ["Passwords do not match."]
                },
                "first_name": first_name,
                "last_name": last_name,
            })
        student = Customer(first_name=first_name, last_name=last_name, password=password)
        try:
            student.full_clean()
            student.save()
            return redirect('login')
        except ValidationError as e:
            return render(request, "register.html", {
                "errors": e.message_dict,
                "first_name": first_name,
                "last_name": last_name,
            })
    return render(request, "register.html")
    
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            student = Customer.objects.get(first_name=username)
            if password == student.password:
                request.session['customer_id'] = student.student_id
                request.session['customer_name'] = student.first_name
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid username or password.'})
        except Customer.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')


def logout(request):
    request.session.flush()
    return redirect('login')


def profile(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    customer = get_object_or_404(Customer, student_id=customer_id)
    book_transactions = BookTransaction.objects.filter(customer=customer).select_related('book').order_by('-issue_date')

    return render(request, 'profile.html', {
        'customer': customer,
        'book_transactions': book_transactions,
    })

def about(request):
    return render(request, 'about.html')

       