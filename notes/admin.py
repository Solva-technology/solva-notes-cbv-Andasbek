from django.contrib import admin
from .models import Note, Status, Category


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "is_final")
    list_filter = ("is_final",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ("title", "description")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "status", "created_at", "short_text")
    list_filter = ("status", "created_at", "categories")
    search_fields = ("text", "author__username", "author__email")
    date_hierarchy = "created_at"
    filter_horizontal = ("categories",)

    def short_text(self, obj):
        return (obj.text[:75] + "...") if len(obj.text) > 75 else obj.text
    short_text.short_description = "Текст"
