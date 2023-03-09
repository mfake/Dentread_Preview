# Generated by Django 4.0.3 on 2022-05-31 10:40

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0055_organisation_logo_users_sign_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 31, 16, 10, 47, 517243)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 31, 16, 10, 47, 525245)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 31, 16, 10, 47, 525245)),
        ),
        migrations.CreateModel(
            name='Dent_Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(default=datetime.date.today)),
                ('refdoc', models.CharField(max_length=200)),
                ('refclinic', models.CharField(max_length=50)),
                ('pid', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('study', models.CharField(max_length=200)),
                ('price', models.CharField(max_length=200)),
                ('invid', models.IntegerField()),
                ('refptid', models.IntegerField(blank=True, null=True)),
                ('refpt_orgid', models.IntegerField(blank=True, null=True)),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
    ]
