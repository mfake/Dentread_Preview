# Generated by Django 4.0.4 on 2022-08-12 09:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0097_imageanalysis_comment_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 12, 15, 21, 45, 511372)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 12, 15, 21, 45, 536987)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 12, 15, 21, 45, 536987)),
        ),
    ]
