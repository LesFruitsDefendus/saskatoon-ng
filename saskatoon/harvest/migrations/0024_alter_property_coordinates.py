from django.db import migrations


def migrate_coordinates(apps, _schema_editor):
    for property in apps.get_model('harvest', 'Property').objects.all():
        if (
            property.geom is not None
            and property.latitude is not None
            and property.longitude is not None
        ):
            property.geom = {
                'type': 'Point',
                'coordinates': [property.longitude, property.latitude],
            }
            property.save()


def restore_coordinates(apps, _schema_editor):
    for property in apps.get_model('harvest', 'Property').objects.all():
        if property.geom is not None and property.geom['type'] == 'Point':
            property.longitude = property.geom['coordinates'][0]
            property.latitude = property.geom['coordinates'][1]
            property.save()


class Migration(migrations.Migration):
    dependencies = [
        ('harvest', '0023_auto_20251128_1414'),
    ]

    operations = [
        migrations.RunPython(migrate_coordinates, restore_coordinates),
        migrations.RemoveField(
            model_name='property',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='property',
            name='longitude',
        ),
    ]
