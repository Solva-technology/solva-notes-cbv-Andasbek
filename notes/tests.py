# notes/tests.py
import uuid
from django.test import TestCase
from django.urls import reverse
from .models import User, UserProfile, Status, Category, Note

class PagesSmokeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # статусы
        st_draft = Status.objects.create(name='draft', is_final=False)
        st_pub   = Status.objects.create(name='published', is_final=True)

        # категории
        cat_general = Category.objects.create(title='Общее', description='Разное')
        cat_work    = Category.objects.create(title='Работа', description='По работе')

        # пользователь + профиль (email уникальный на каждый прогон)
        email = f"test-{uuid.uuid4().hex}@example.com"
        u = User.objects.create(name='Иван', email=email)
        UserProfile.objects.create(user=u, bio='Разработчик', birth_date='1990-01-01')

        # заметки
        n1 = Note.objects.create(text='Первая заметка про проект.', author=u, status=st_draft)
        n1.categories.set([cat_general, cat_work])

        n2 = Note.objects.create(text='Опубликованная заметка.', author=u, status=st_pub)
        n2.categories.set([cat_general])

        cls.user = u
        cls.note = n1

    def test_index_ok(self):
        r = self.client.get(reverse('index'))
        self.assertEqual(r.status_code, 200)

    def test_user_detail_ok(self):
        r = self.client.get(reverse('user_detail', args=[self.user.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.user.name)

    def test_note_detail_ok(self):
        r = self.client.get(reverse('note_detail', args=[self.note.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.note.status.name)
