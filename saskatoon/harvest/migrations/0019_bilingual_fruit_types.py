from django.db import migrations, models
import django_quill.fields


class Migration(migrations.Migration):
    dependencies = [
        ('harvest', '0018_alter_requestforparticipation_number_of_pickers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={
                'ordering': ['-id'],
                'verbose_name': 'property',
                'verbose_name_plural': 'properties',
            },
        ),
        migrations.RenameField(
            model_name='treetype',
            old_name='name',
            new_name='name_fr',
        ),
        migrations.RenameField(
            model_name='treetype',
            old_name='fruit_name',
            new_name='fruit_name_fr',
        ),
        migrations.AddField(
            model_name='treetype',
            name='name_en',
            field=models.CharField(
                default='', max_length=20, verbose_name='Tree name (en)'
            ),
        ),
        migrations.AddField(
            model_name='treetype',
            name='fruit_name_en',
            field=models.CharField(
                default='', max_length=20, verbose_name='Fruit name (en)'
            ),
        ),
        migrations.AddField(
            model_name='treetype',
            name='maturity_end',
            field=models.DateField(
                blank=True, null=True, verbose_name='Maturity end date'
            ),
        ),
        migrations.AddField(
            model_name='treetype',
            name='maturity_start',
            field=models.DateField(
                blank=True, null=True, verbose_name='Maturity start date'
            ),
        ),
        migrations.AlterField(
            model_name='harvest',
            name='about',
            field=django_quill.fields.QuillField(
                blank=True,
                help_text='Published on public facing calendar',
                max_length=1000,
                null=True,
                verbose_name='Public announcement',
            ),
        ),
        migrations.AlterModelOptions(
            name='treetype',
            options={
                'ordering': ['name_en'],
                'verbose_name': 'tree type',
                'verbose_name_plural': 'tree types',
            },
        ),
        migrations.RemoveField(
            model_name='treetype',
            name='season_start',
        ),
        migrations.AlterField(
            model_name='treetype',
            name='fruit_name_fr',
            field=models.CharField(
                default='', max_length=20, verbose_name='Nom du fruit (fr)'
            ),
        ),
        migrations.AlterField(
            model_name='treetype',
            name='name_fr',
            field=models.CharField(
                default='', max_length=20, verbose_name="Nom de l'arbre (fr)"
            ),
        ),
        migrations.AddField(
            model_name='treetype',
            name='fruit_icon',
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name='Fruit icon'
            ),
        ),
        migrations.AlterField(
            model_name='treetype',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='fruits_images',
                verbose_name='Fruit image',
            ),
        ),
    ]
