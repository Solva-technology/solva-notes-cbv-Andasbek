# seed.py
import os
import argparse
import random
import string
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notebook_project.settings")

import django  # noqa: E402
django.setup()

from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from notes.models import UserProfile, Status, Category, Note  # noqa: E402

User = get_user_model()

FIRST_NAMES = ["Иван", "Казбек", "Мария", "Анна", "Сергей", "Алия", "Елена", "Даниил", "Азамат", "Ерлан"]
LAST_NAMES  = ["Иванов", "Садыков", "Петрова", "Ким", "Смирнов", "Тлеуханов", "Ахметова", "Кузнецов", "Ковалёв", "Жумабеков"]
WORDS = (
    "django orm шаблоны база данных postgres оптимизация выборки фильтрация категории статусы проект "
    "заметка пользователь профиль админка локализация docker compose"
).split()


def rands(n=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def rand_person():
    first = random.choice(FIRST_NAMES)
    last  = random.choice(LAST_NAMES)
    return first, last, f"{first} {last}"


def rand_username():
    # короткий юзернейм: имя латиницей + случайный хвост
    return f"user_{rands(6)}"


def rand_email():
    return f"{rands(6)}@example.com"


def rand_sentence(min_w=6, max_w=16):
    n = random.randint(min_w, max_w)
    return " ".join(random.choice(WORDS) for _ in range(n)).capitalize() + "."


def rand_text(min_s=2, max_s=6):
    return " ".join(rand_sentence() for _ in range(random.randint(min_s, max_s)))


def rand_birthdate():
    # возраст 18–60
    today = date.today()
    years = random.randint(18, 60)
    return today.replace(year=today.year - years) - timedelta(days=random.randint(0, 364))


@transaction.atomic
def run(users_n: int, notes_n: int, cats_n: int, reset: bool, fresh: bool):
    # 0) Базовые статусы (идемпотентно)
    st_draft, _ = Status.objects.get_or_create(name="draft", defaults={"is_final": False})
    st_pub,   _ = Status.objects.get_or_create(name="published", defaults={"is_final": True})
    # при желании:
    Status.objects.get_or_create(name="archived", defaults={"is_final": True})

    # 1) Очистка по флагам
    if fresh:
        print("Fresh: удаляем все сущности (Note, Category, UserProfile, User)…")
        Note.objects.all().delete()
        Category.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
    elif reset:
        print("Reset: удаляем только Note…")
        Note.objects.all().delete()

    # 2) Категории — докидываем до cats_n
    have_cats = Category.objects.count()
    if have_cats < cats_n:
        to_create = []
        for i in range(cats_n - have_cats):
            idx = i + 1 + have_cats
            to_create.append(Category(title=f"Категория #{idx}", description=rand_sentence()))
        Category.objects.bulk_create(to_create)

    categories = list(Category.objects.all().order_by("title"))
    if not categories:
        categories = [Category.objects.create(title="Общее", description="Разное")]

    # 3) Пользователи + профили — докидываем до users_n
    have_users = User.objects.count()
    to_make = max(0, users_n - have_users)
    for _ in range(to_make):
        first, last, _full = rand_person()
        username = rand_username()
        email = rand_email()
        # создаём корректно через create_user, чтобы пароль захешировался
        u = User.objects.create_user(
            username=username,
            email=email,
            password="password123",
            first_name=first,
            last_name=last,
        )
        UserProfile.objects.create(user=u, bio=rand_sentence(8, 18), birth_date=rand_birthdate())

    users = list(User.objects.select_related("userprofile").all())
    if not users:
        # страховка: если fresh удалил всё и users_n=0 — делаем хотя бы одного
        u = User.objects.create_user(
            username="demo_" + rands(4),
            email=rand_email(),
            password="password123",
            first_name="Иван",
            last_name="Иванов",
        )
        UserProfile.objects.create(user=u, bio="Профиль по умолчанию", birth_date=rand_birthdate())
        users = [u]

    # 4) Заметки
    now = timezone.now()
    created_ids = []
    for _ in range(notes_n):
        author = random.choice(users)
        status = st_pub if random.random() < 0.65 else st_draft
        created_at = now - timedelta(days=random.randint(0, 180), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        n = Note.objects.create(author=author, status=status, text=rand_text())
        # если хочется «историчности» — обновляем created_at отдельным запросом
        Note.objects.filter(pk=n.pk).update(created_at=created_at)

        # категории: 1..3 случайных
        k = random.randint(1, min(3, len(categories)))
        n.categories.set(random.sample(categories, k=k))
        created_ids.append(n.id)

    print(
        "Готово:",
        f"users={User.objects.count()}",
        f"profiles={UserProfile.objects.count()}",
        f"categories={Category.objects.count()}",
        f"notes_total={Note.objects.count()}",
        f"notes_added={len(created_ids)}",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Заполнить БД реалистичными данными (идемпотентно).")
    parser.add_argument("--users", type=int, default=20, help="сколько пользователей должно быть в итоге (докинем до этого числа)")
    parser.add_argument("--notes", type=int, default=200, help="сколько заметок добавить за прогон")
    parser.add_argument("--categories", type=int, default=6, help="минимум категорий в системе")
    parser.add_argument("--reset", action="store_true", help="очистить только Note перед генерацией")
    parser.add_argument("--fresh", action="store_true", help="полный reset: удалить Note/Category/UserProfile/User и создать всё заново")

    args = parser.parse_args()
    run(args.users, args.notes, args.categories, args.reset, args.fresh)
