# Generated by Django 4.0.4 on 2022-11-26 10:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0241_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addonlabservices',
            name='materialId',
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 15, 39, 35, 797302)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 15, 39, 35, 862429)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 15, 39, 35, 862429)),
        ),
    ]