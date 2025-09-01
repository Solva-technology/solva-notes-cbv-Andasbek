# notes/migrations/0002_seed_statuses.py
from django.db import migrations

def seed_statuses(apps, schema_editor):
    Status = apps.get_model("notes", "Status")
    defaults = [
        ("draft", False),
        ("published", True),
        ("archived", True),
    ]
    for name, is_final in defaults:
        Status.objects.get_or_create(name=name, defaults={"is_final": is_final})

class Migration(migrations.Migration):
    dependencies = [
        ("notes", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(seed_statuses, migrations.RunPython.noop),
    ]
