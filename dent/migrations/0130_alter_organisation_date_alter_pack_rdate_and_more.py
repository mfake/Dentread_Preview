# Generated by Django 4.0.4 on 2022-09-06 06:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0129_remove_radiologycalservices_orgid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 11, 32, 21, 410316)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 11, 32, 21, 425946)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 11, 32, 21, 425946)),
        ),
    ]
