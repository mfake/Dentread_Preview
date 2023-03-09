# Generated by Django 4.0.4 on 2022-10-19 11:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0210_prosthetic_filestatus_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='iosfile',
            name='badge',
            field=models.CharField(default=1, max_length=400),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 19, 17, 5, 18, 472508)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 19, 17, 5, 18, 517496)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 19, 17, 5, 18, 518510)),
        ),
    ]
