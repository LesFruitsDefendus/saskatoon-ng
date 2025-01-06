# Generated by Django 3.2.9 on 2024-04-08 04:51

import django.core.validators
from django.db import migrations, models
import django_quill.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator('^[a-z_]+$', 'Content name must only contain lowercase letters or underscore')], verbose_name='Reference name')),
                ('title_en', models.CharField(blank=True, max_length=100, verbose_name='Title (en)')),
                ('title_fr', models.CharField(blank=True, max_length=100, verbose_name='Titre (fr)')),
                ('subtitle_en', models.CharField(blank=True, max_length=100, verbose_name='Subtitle (en)')),
                ('subtitle_fr', models.CharField(blank=True, max_length=100, verbose_name='Sous-titre (fr)')),
                ('body_en', django_quill.fields.QuillField()),
                ('body_fr', django_quill.fields.QuillField()),
            ],
            options={
                'verbose_name': 'Content',
                'verbose_name_plural': 'Content',
                'ordering': ['name'],
            },
        ),
    ]
