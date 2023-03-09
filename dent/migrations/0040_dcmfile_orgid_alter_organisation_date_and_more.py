# Generated by Django 4.0.3 on 2022-05-03 05:56

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0039_pack_applied_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dcmfile',
            name='orgid',
            field=models.ForeignKey(default=26, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 3, 11, 26, 30, 954312)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 3, 11, 26, 30, 961319)),
        ),
    ]
