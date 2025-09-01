# notes/urls.py
from django.urls import path

from .views import (
    NoteListView,
    NoteDetailView,
    NoteCreateView,
    NoteUpdateView,
    NoteDeleteView,
    UserListView,
    UserDetailView,
)

app_name = "notes"

urlpatterns = [
    # Заметки
    path("", NoteListView.as_view(), name="index"),
    path("notes/create/", NoteCreateView.as_view(), name="note_create"),
    path("notes/<int:note_id>/", NoteDetailView.as_view(), name="note_detail"),
    path("notes/<int:note_id>/edit/", NoteUpdateView.as_view(), name="note_edit"),
    path("notes/<int:note_id>/delete/", NoteDeleteView.as_view(), name="note_delete"),

    # Пользователи (страницы внутри приложения notes)
    path("users/", UserListView.as_view(), name="users_list"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user_detail"),
]
