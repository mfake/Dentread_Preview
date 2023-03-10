# Generated by Django 4.0.4 on 2022-08-17 11:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0104_radiologycalservices_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suricalguide',
            old_name='casetype',
            new_name='data_type1',
        ),
        migrations.RenameField(
            model_name='suricalguide',
            old_name='datatype',
            new_name='data_type2',
        ),
        migrations.RenameField(
            model_name='suricalguide',
            old_name='material',
            new_name='guide_type',
        ),
        migrations.RenameField(
            model_name='suricalguide',
            old_name='method',
            new_name='output_type',
        ),
        migrations.RemoveField(
            model_name='suricalguide',
            name='type',
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 17, 17, 0, 48, 99298)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 17, 17, 0, 48, 130557)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 17, 17, 0, 48, 146186)),
        ),
    ]
