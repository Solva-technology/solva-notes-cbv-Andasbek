from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("notes.urls", "notes"), namespace="notes")),
    path("", include(("users.urls", "users"), namespace="users")),
    path("accounts/profile/", lambda r: redirect("notes:index")),
]
# если добавляли, 404-хэндлер можно оставить:
# handler404 = "notes.views.page_not_found"
