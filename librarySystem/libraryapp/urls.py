from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("books", views.books, name="books"),
    path("books/<int:book_id>/", views.book_detail, name="book_detail"),
    path("authors", views.authors, name="authors"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
]

