# Generated by Django 3.2.25 on 2024-04-26 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0008_alter_person_onboarding'),
    ]

    operations = [
        migrations.AddField(
            model_name='authuser',
            name='has_temporary_password',
            field=models.BooleanField(default=False),
        ),
    ]
