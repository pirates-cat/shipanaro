# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-25 19:02
from __future__ import unicode_literals

from django.db import migrations, models


def set_drop_out(apps, schema_editor):
    Membership = apps.get_model('shipanaro', 'Membership')
    db_alias = schema_editor.connection.alias
    for m in Membership.objects.using(db_alias).all():
        m.drop_out = m.date_left is not None
        m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('shipanaro', '0004_auto_20160824_0101'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='drop_out',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(code=set_drop_out, ),
    ]
