# users/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from .views import UserRegisterView

app_name = "users"

urlpatterns = [
    # Регистрация
    path("auth/register/", UserRegisterView.as_view(), name="register"),

    # Вход / Выход
    path(
        "auth/login/",
        LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "auth/logout/",
        LogoutView.as_view(
            template_name="registration/logout.html",
            # при желании можно: next_page = "index"
        ),
        name="logout",
    ),

    # Сброс пароля
    path(
        "auth/password_reset/",
        PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.txt",   # <-- добавляем
            subject_template_name="registration/password_reset_subject.txt",# <-- добавляем
            success_url=reverse_lazy("password_reset_done"),               # без namespace
        ),
        name="password_reset",
    ),
    path(
        "auth/password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "auth/reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "auth/reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
