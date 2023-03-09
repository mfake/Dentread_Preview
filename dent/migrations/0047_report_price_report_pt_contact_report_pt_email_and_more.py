# Generated by Django 4.0.3 on 2022-05-22 02:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0046_refpt_hardcopy_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='pt_contact',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='pt_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 22, 7, 55, 1, 403507)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 22, 7, 55, 1, 411517)),
        ),
    ]