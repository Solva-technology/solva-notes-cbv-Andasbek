from django import forms
from .models import Note, Status, Category

class NoteForm(forms.ModelForm):
    # Доп. поле: новые категории через запятую (необязательное)
    new_categories = forms.CharField(
        required=False,
        label="Новые категории (через запятую)",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Напр.: Работа, Учёба"}),
        help_text="Если нужной категории нет в списке — добавь здесь, они создадутся автоматически.",
    )

    class Meta:
        model = Note
        fields = ("text", "status", "categories", "new_categories")  # author убран
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-control", "rows": 6, "placeholder": "Текст заметки"
            }),
            "status": forms.Select(attrs={"class": "form-select"}),
            # удобнее, чем SelectMultiple
            "categories": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "text": "Текст",
            "status": "Статус",
            "categories": "Категории",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].queryset = Status.objects.all().order_by("name")
        self.fields["categories"].queryset = Category.objects.all().order_by("title")
        # дефолтный статус draft, если он есть
        try:
            self.fields["status"].initial = Status.objects.get(name="draft").pk
        except Status.DoesNotExist:
            pass

    def save(self, commit=True):
        # обычное сохранение заметки
        note = super().save(commit=commit)

        # создаём новые категории по необходимости
        raw = (self.cleaned_data.get("new_categories") or "").strip()
        if raw:
            names = [x.strip() for x in raw.split(",") if x.strip()]
            if names:
                created_or_found = []
                for title in names:
                    cat, _ = Category.objects.get_or_create(title=title)
                    created_or_found.append(cat.pk)
                # объединяем с уже выбранными
                current = list(self.cleaned_data.get("categories").values_list("pk", flat=True))
                note.categories.set(set(current + created_or_found))  # уникализируем

        return note
