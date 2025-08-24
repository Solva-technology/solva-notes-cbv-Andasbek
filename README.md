[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20143499&assignment_repo_type=AssignmentRepo)
# Note App — Часть #5: Переписывание на CBV

## Цель
Рефакторинг приложения: заменить все существующие view-функции на **class-based views (CBV)**. Это позволит упростить поддержку кода, сделать его более структурированным и гибким для расширения.

## Описание проекта
Note App — учебное Django-приложение для работы с заметками.  
К текущему этапу проект уже включает:

- админку и локализацию;
- список заметок (главная), страницу отдельной заметки, страницу редактирования / удаления заметки;
- CRUD для модели Note через Django Forms;
- систему пользователей: регистрация, авторизация, восстановление пароля;
- разграничение прав доступа (редактировать и удалять может только автор или администратор);
- базовый шаблон `base.html`;
- запуск в Docker + PostgreSQL.

## Новые требования
Все view-функции должны быть заменены на соответствующие **классы Django CBV**:

1. **Заметки**
   - Список заметок → `ListView`
   - Просмотр отдельной заметки → `DetailView`
   - Создание заметки → `CreateView`
   - Редактирование заметки → `UpdateView`
   - Удаление заметки → `DeleteView`
   - Для форм использовать встроенные механизмы CBV (`form_class` / `fields`).

2. **Аутентификация и регистрация**
   - Вход → `LoginView`
   - Выход → `LogoutView`
   - Регистрация → реализовать через `CreateView` с кастомной формой.
   - Сброс пароля → `PasswordResetView`, `PasswordResetDoneView`, `PasswordResetConfirmView`, `PasswordResetCompleteView`.

3. **Ограничение прав**
   - Использовать `UserPassesTestMixin` или `PermissionRequiredMixin` для проверки прав на редактирование/удаление заметок.
   - Авторизация должна работать на уровне CBV через `LoginRequiredMixin`.

## Требования
- Переписать все функции во `views.py` на классы.
- Использовать стандартные Django CBV (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, `FormView` и т.д.).
- Для защиты маршрутов применять `LoginRequiredMixin` и проверки на автора/админа.
- Поддерживать существующую структуру URL'ов.
- Все шаблоны должны остаться рабочими без изменений или с минимальными правками.
- В шаблонах `note_form.html` и `note_confirm_delete.html` формы должны быть привязаны к CBV.

