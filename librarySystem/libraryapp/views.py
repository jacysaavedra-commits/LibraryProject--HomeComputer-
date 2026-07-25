from django.shortcuts import redirect, render
from .models import Book
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from .models import Book, Customer
from django.core.exceptions import ValidationError

def Books(request):
    books = Book.objects.all()
    return render(request, 'books.html', {'books': books})
# Create your views here.
def home(request):
    return render(request, 'home.html')
def books(request):
    return render(request, 'books.html')
def authors(request):
    return render(request, 'authors.html')
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
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            student = Customer.objects.get(email=email)
            if check_password(password, student.password):
                request.session['customer_id'] = student.student_id
                request.session['customer_name'] = student.first_name
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid email or password.'})
        except Customer.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email or password.'})
    return render(request, 'login.html')
       