# Generated by Django 3.2.25 on 2025-02-22 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0014_alter_equipment_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvest',
            name='status',
            field=models.CharField(choices=[('pending', 'To be confirmed'), ('orphan', 'Orphan'), ('adopted', 'Adopted'), ('scheduled', 'Scheduled'), ('ready', 'Ready'), ('succeeded', 'Succeeded'), ('cancelled', 'Cancelled')], max_length=100, null=True, verbose_name='Harvest status'),
        ),
    ]
