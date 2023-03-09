# Generated by Django 4.0.3 on 2022-05-22 05:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0050_organisation_ctperson_name_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='gender',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 22, 10, 37, 42, 699891)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 22, 10, 37, 42, 707892)),
        ),
    ]
