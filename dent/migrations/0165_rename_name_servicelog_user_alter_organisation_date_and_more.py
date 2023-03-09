# Generated by Django 4.0.4 on 2022-09-18 08:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0164_servicelog_message_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='servicelog',
            old_name='name',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 18, 13, 40, 55, 966369)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 18, 13, 40, 55, 981369)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 18, 13, 40, 55, 982369)),
        ),
    ]
