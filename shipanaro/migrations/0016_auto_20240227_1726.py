# Generated by Django 3.2 on 2024-02-27 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipanaro', '0015_auto_20240227_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='birthday',
            field=models.DateField(help_text='Format: dd/mm/yyyy', verbose_name='Data de naixement'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='id_photo',
            field=models.ImageField(help_text='Utilitza una foto on es vegin les dues cares del document (max 10Mb)', null=True, upload_to='id_photos', verbose_name="Fotografia del document d'identificació"),
        ),
        migrations.AlterField(
            model_name='membership',
            name='nid_type',
            field=models.IntegerField(choices=[(7241, 'DNI'), (7240, 'Passaport'), (7242, 'NIE'), (0, 'Desconegut')], verbose_name="Tipus d'identificació"),
        ),
    ]
