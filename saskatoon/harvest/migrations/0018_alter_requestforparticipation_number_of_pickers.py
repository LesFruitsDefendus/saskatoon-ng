# Generated by Django 3.2.25 on 2025-04-20 01:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0017_auto_20250316_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestforparticipation',
            name='number_of_pickers',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)], verbose_name='Number of pickers'),
        ),
    ]
