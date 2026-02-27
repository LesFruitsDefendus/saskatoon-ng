from django.db import migrations
import djgeojson.fields


def migrate_coordinates(apps, _schema_editor):
    for org in apps.get_model('member', 'Organization').objects.all():
        if org.latitude is not None and org.longitude is not None:
            org.geom = {'type': 'Point', 'coordinates': [org.longitude, org.latitude]}
            org.save()


class Migration(migrations.Migration):
    dependencies = [
        ('member', '0019_auto_20251128_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='geom',
            field=djgeojson.fields.PointField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_coordinates),
        migrations.RemoveField(
            model_name='organization',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='longitude',
        ),
    ]
