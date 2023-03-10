# Generated by Django 4.0.3 on 2022-05-22 02:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0048_report_reg_by_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='regby_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='regby_userid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 22, 8, 11, 43, 484128)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 22, 8, 11, 43, 492138)),
        ),
    ]
