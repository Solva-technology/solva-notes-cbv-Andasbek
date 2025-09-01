# users/views.py
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView

from .forms import RegisterForm


class UserRegisterView(CreateView):
    """Регистрация через CBV + авто-логин + messages."""
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("notes:index")  # важно: namespace 'notes'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("notes:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()      # важно создать self.object
        login(self.request, self.object)
        messages.success(self.request, "Регистрация прошла успешно!")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)
