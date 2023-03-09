# Generated by Django 4.0.4 on 2022-09-25 09:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0181_users_first_name_users_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='city',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='organisation',
            name='country',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='organisation',
            name='pincode',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='organisation',
            name='state',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 25, 15, 18, 12, 408269)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 25, 15, 18, 12, 449271)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 25, 15, 18, 12, 449271)),
        ),
    ]
