# Generated by Django 3.2.25 on 2025-05-25 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0017_auto_20250504_1308'),
        ('sitebase', '0002_auto_20250316_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='member.person', verbose_name='Recipient'),
        ),
        migrations.AlterField(
            model_name='email',
            name='type',
            field=models.CharField(choices=[('closing', 'Closing (common)'), ('registration', 'Pickleader Registration Invite'), ('password_reset', 'Password Reset'), ('new_rfp', 'New Request For Participation'), ('new_comment', 'New Harvest Comment'), ('property_registered', 'Property was registered'), ('season_authorization', 'Seasonal property authorization'), ('unselected_pickers', 'Unselected pickers'), ('selected_picker', 'Selected picker'), ('rejected_picker', 'Rejected picker')], max_length=20, verbose_name='Email type'),
        ),
        migrations.AlterField(
            model_name='emailcontent',
            name='type',
            field=models.CharField(blank=True, choices=[('closing', 'Closing (common)'), ('registration', 'Pickleader Registration Invite'), ('password_reset', 'Password Reset'), ('new_rfp', 'New Request For Participation'), ('new_comment', 'New Harvest Comment'), ('property_registered', 'Property was registered'), ('season_authorization', 'Seasonal property authorization'), ('unselected_pickers', 'Unselected pickers'), ('selected_picker', 'Selected picker'), ('rejected_picker', 'Rejected picker')], default=None, max_length=20, null=True, unique=True, verbose_name='Email type'),
        ),
    ]
