# Generated by Django 4.0.4 on 2022-09-10 09:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0139_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiologycalservices',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 10, 15, 8, 50, 318106)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 10, 15, 8, 50, 349358)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 10, 15, 8, 50, 349358)),
        ),
    ]
