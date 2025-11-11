from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('harvest', '0011_alter_harvest_about')]

    operations = [
        migrations.RenameField(
            model_name='equipmenttype',
            old_name='name',
            new_name='name_fr',
        ),
    ]
