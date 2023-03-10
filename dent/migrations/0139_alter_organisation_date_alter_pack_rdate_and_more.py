# Generated by Django 4.0.4 on 2022-09-10 09:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0138_radiologycalservices_portal_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 10, 15, 1, 19, 271040)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 10, 15, 1, 19, 286668)),
        ),
        migrations.AlterField(
            model_name='radiologycalservices',
            name='pid',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 10, 15, 1, 19, 286668)),
        ),
    ]
