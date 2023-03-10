# Generated by Django 4.0.3 on 2022-06-20 09:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0068_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Def_Study',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('maincat', models.CharField(max_length=200)),
                ('subcat', models.CharField(max_length=200)),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 20, 15, 11, 56, 44200)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 20, 15, 11, 56, 52179)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 20, 15, 11, 56, 53178)),
        ),
    ]
