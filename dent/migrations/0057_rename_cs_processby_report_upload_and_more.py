# Generated by Django 4.0.3 on 2022-06-01 11:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0056_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='CS_processby',
            new_name='upload',
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 1, 16, 51, 44, 202791)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 1, 16, 51, 44, 210803)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 1, 16, 51, 44, 210803)),
        ),
    ]
