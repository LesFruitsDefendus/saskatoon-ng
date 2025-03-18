from django.db import migrations, models
from django.core import validators
from django.conf import settings
from django.utils import timezone as tz


def migrate_rfp_status(apps, _schema_editor):
    for rfp in apps.get_model('harvest', 'RequestForParticipation').objects.all():
        if rfp.is_cancelled:
            rfp.status = 'cancelled'
        elif rfp.is_accepted is True:
            rfp.status = 'accepted'
        elif rfp.is_accepted is False:
            rfp.status = 'declined'
        elif rfp.harvest.end_date > tz.now():
            rfp.status = 'pending'
        else:
            rfp.status = 'obsolete'

        rfp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0015_alter_harvest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestforparticipation',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('cancelled', 'Cancelled'), ('obsolete', 'Obsolete')], default='pending', max_length=20, verbose_name='Request status'),
        ),
        migrations.RunPython(migrate_rfp_status),
        migrations.RemoveField(
            model_name='requestforparticipation',
            name='is_accepted',
        ),
        migrations.RemoveField(
            model_name='requestforparticipation',
            name='is_cancelled',
        ),
        migrations.RenameField(
            model_name='requestforparticipation',
            old_name='creation_date',
            new_name='date_created',
        ),
        migrations.AlterField(
            model_name='requestforparticipation',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created on'),
        ),
        migrations.RenameField(
            model_name='requestforparticipation',
            old_name='acceptation_date',
            new_name='date_status_updated',
        ),
        migrations.AlterField(
            model_name='requestforparticipation',
            name='date_status_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Status updated on'),
        ),
        migrations.RenameField(
            model_name='requestforparticipation',
            old_name='number_of_people',
            new_name='number_of_pickers',
        ),
        migrations.AlterField(
            model_name='requestforparticipation',
            name='number_of_pickers',
            field=models.PositiveIntegerField(default=1, validators=[validators.MinValueValidator(1)], verbose_name='Number of pickers'),
        ),
        migrations.RenameField(
            model_name='requestforparticipation',
            old_name='picker',
            new_name='person',
        ),
        migrations.RenameField(
            model_name='requestforparticipation',
            old_name='notes_from_pickleader',
            new_name='notes',
        ),
        migrations.AlterField(
            model_name='requestforparticipation',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='PickLeader notes'),
        ),
        migrations.AlterField(
            model_name='requestforparticipation',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Comment from participant'),
        ),
        migrations.AlterField(
            model_name='requestforparticipation',
            name='showed_up',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='Picker(s) showed up'),
        ),
        migrations.RenameField(
            model_name='harvest',
            old_name='creation_date',
            new_name='date_created',
        ),
        migrations.AlterField(
            model_name='harvest',
            name='status',
            field=models.CharField(choices=[('orphan', 'Orphan'), ('adopted', 'Adopted'), ('pending', 'To be confirmed'), ('scheduled', 'Date scheduled'), ('ready', 'Ready'), ('succeeded', 'Succeeded'), ('cancelled', 'Cancelled')], default='orphan', max_length=20, verbose_name='Harvest status'),
        ),
        migrations.AlterField(
            model_name='harvest',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='harvest_edited', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='created_date',
            new_name='date_created',
        ),
        migrations.AddField(
            model_name='comment',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated on'),
        ),
        migrations.AddField(
            model_name='comment',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=tz.now, verbose_name='Created on'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='property',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='properties', to='member.actor', verbose_name='Owner'),
        ),
    ]
