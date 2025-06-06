from django.db import migrations, models


def migrate_language(apps, _schema_editor):
    for person in apps.get_model('member', 'Person').objects.all():
        if (person.lang_obj is not None and person.lang_obj.name == "English"):
            person.language = 'en'
            person.save()


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0015_alter_neighborhood_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='redmine_contact_id',
        ),
        migrations.RenameField('person', 'language', 'lang_obj'),
        migrations.AddField(
            model_name='person',
            name='language',
            field=models.CharField(choices=[('fr', 'Français'), ('en', 'English')], default='fr', max_length=2, verbose_name='Preferred Language'),
        ),
        migrations.RunPython(migrate_language),
        migrations.RemoveField(
            model_name='person',
            name='lang_obj',
        ),
        migrations.DeleteModel(
            name='Language',
        ),
    ]
