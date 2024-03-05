# Generated by Django 5.0.3 on 2024-03-05 10:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iam", "0002_user_created_at_user_is_verified_user_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]