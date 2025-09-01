# notes/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .forms import NoteForm
from .models import Note, User


# ----------------------------
# ЗАМЕТКИ
# ----------------------------

class NoteListView(ListView):
    """Главная страница со списком заметок + пагинация"""
    model = Note
    template_name = "notes/index.html"
    context_object_name = "page_obj"   # чтобы шаблон не менять: в FBV передавался page_obj
    paginate_by = 10

    def get_queryset(self):
        return (
            Note.objects
            .select_related("author", "status")
            .prefetch_related("categories")
            .order_by("-created_at")
        )

    # ListView сам строит paginator и page_obj, но по умолчанию кладет:
    # object_list, is_paginated, paginator, page_obj. Мы переназвали context_object_name,
    # поэтому всё будет доступно как page_obj в шаблоне.


class NoteDetailView(DetailView):
    """Детальная заметка"""
    model = Note
    pk_url_kwarg = "note_id"
    template_name = "notes/note_detail.html"
    context_object_name = "note"

    def get_queryset(self):
        return (
            Note.objects
            .select_related("author", "status", "author__userprofile")
            .prefetch_related("categories")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        note = ctx["note"]
        ctx["profile"] = getattr(note.author, "userprofile", None)
        return ctx


class AuthorOrAdminRequiredMixin(UserPassesTestMixin):
    """Проверка прав: автор объекта или админ."""
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return user.is_authenticated and (user.is_staff or obj.author_id == user.id)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Доступ запрещен.")
        return super().handle_no_permission()


class NoteCreateView(LoginRequiredMixin, CreateView):
    """Создание заметки (автор = текущий пользователь). redirect -> index"""
    model = Note
    form_class = NoteForm
    template_name = "notes/note_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "create"  # для существующего шаблона
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        note = form.save(commit=False)
        note.author = self.request.user
        note.save()
        form.save_m2m()
        messages.success(self.request, f"Заметка #{note.id} создана.")
        return super().form_valid(form)

    def get_success_url(self):
        # как и раньше: после создания возвращаемся на главную
        return reverse_lazy("notes:index")


class NoteUpdateView(LoginRequiredMixin, AuthorOrAdminRequiredMixin, UpdateView):
    """Редактирование заметки. redirect -> detail"""
    model = Note
    form_class = NoteForm
    pk_url_kwarg = "note_id"
    template_name = "notes/note_form.html"
    context_object_name = "note"

    def get_queryset(self):
        return (
            Note.objects
            .select_related("author", "status")
            .prefetch_related("categories")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "edit"  # для существующего шаблона
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, f"Заметка #{self.object.id} обновлена.")
        return resp

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки формы.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("note_detail", kwargs={"note_id": self.object.id})


class NoteDeleteView(LoginRequiredMixin, AuthorOrAdminRequiredMixin, DeleteView):
    """Удаление заметки: подтверждение -> POST -> redirect index"""
    model = Note
    pk_url_kwarg = "note_id"
    template_name = "notes/note_confirm_delete.html"
    context_object_name = "note"
    success_url = reverse_lazy("notes:index")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Заметка удалена.")
        return super().delete(request, *args, **kwargs)


# ----------------------------
# ПОЛЬЗОВАТЕЛИ (страницы внутри приложения notes)
# ----------------------------

class UserDetailView(DetailView):
    """Страница пользователя + его заметки"""
    model = User
    pk_url_kwarg = "user_id"
    template_name = "notes/user_detail.html"
    context_object_name = "user"

    def get_queryset(self):
        # Нужен профиль в select_related
        return User.objects.select_related("userprofile")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_obj = ctx["user"]
        ctx["profile"] = getattr(user_obj, "userprofile", None)
        ctx["notes"] = (
            Note.objects
            .filter(author=user_obj)
            .select_related("status")
            .order_by("-created_at")
        )
        return ctx


class UserListView(ListView):
    """Список пользователей"""
    model = User
    template_name = "notes/users_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all().order_by("username")
