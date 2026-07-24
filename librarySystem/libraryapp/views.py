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
def login(request):
    return render(request, 'login.html')
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the password matches
        if password != confirm_password:
            return render(request, "register.html", {
                "errors": {"password": ["Passwords do not match."]
                },
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            })
        student = Customer(first_name=first_name, last_name=last_name, email=email, password=password)
        try:
            student.full_clean()
            student.save()
            return redirect('login')
        except ValidationError as e:
            return render(request, "register.html", {
                "errors": e.message_dict,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            })
        return render(request, "register.html")
    

       