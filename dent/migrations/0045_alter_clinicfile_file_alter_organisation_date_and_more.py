# Generated by Django 4.0.3 on 2022-05-14 15:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0044_alter_organisation_date_alter_pack_rdate_clinicfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicfile',
            name='file',
            field=models.FileField(upload_to='static/cfiles/'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 14, 21, 28, 29, 375017)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 14, 21, 28, 29, 382996)),
        ),
    ]
