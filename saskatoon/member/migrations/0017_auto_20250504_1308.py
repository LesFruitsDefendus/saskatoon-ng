# Generated by Django 3.2.25 on 2025-05-04 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0016_alter_person_language'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='neighborhood',
            options={'ordering': ['name'], 'verbose_name': 'borough', 'verbose_name_plural': 'boroughs'},
        ),
        migrations.AlterField(
            model_name='organization',
            name='neighborhood',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='member.neighborhood', verbose_name='Borough'),
        ),
        migrations.AlterField(
            model_name='person',
            name='neighborhood',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='member.neighborhood', verbose_name='Borough'),
        ),
    ]
