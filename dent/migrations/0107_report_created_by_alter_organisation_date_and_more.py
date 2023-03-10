# Generated by Django 4.0.4 on 2022-08-23 06:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0106_suricalguide_planning_type_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='created_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 23, 11, 51, 7, 223227)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 23, 11, 51, 7, 238856)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 23, 11, 51, 7, 238856)),
        ),
    ]
