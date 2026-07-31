from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("books/<int:book_id>/", views.book_detail, name="book_detail"),
    path("authors/", views.authors, name="authors"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("about/", views.about, name="about")
]

