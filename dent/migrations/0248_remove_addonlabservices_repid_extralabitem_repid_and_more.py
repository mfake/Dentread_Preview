# Generated by Django 4.0.4 on 2022-11-29 17:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0247_addonlabservices_repid_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addonlabservices',
            name='repid',
        ),
        migrations.AddField(
            model_name='extralabitem',
            name='repid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 29, 23, 20, 36, 601810)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 29, 23, 20, 36, 648804)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 29, 23, 20, 36, 649806)),
        ),
    ]
