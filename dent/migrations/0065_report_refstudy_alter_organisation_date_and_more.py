# Generated by Django 4.0.3 on 2022-06-19 09:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0064_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='refstudy',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 14, 44, 9, 288995)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 14, 44, 9, 296975)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 14, 44, 9, 297972)),
        ),
    ]