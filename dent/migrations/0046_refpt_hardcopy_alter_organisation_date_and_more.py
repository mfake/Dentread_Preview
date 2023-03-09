# Generated by Django 4.0.3 on 2022-05-19 04:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0045_alter_clinicfile_file_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='refpt',
            name='hardcopy',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 19, 10, 3, 5, 686097)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 19, 10, 3, 5, 694108)),
        ),
    ]