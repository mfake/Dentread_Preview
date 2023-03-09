# Generated by Django 4.0.3 on 2022-05-14 15:19

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0043_invoice_refpt_orgid_invoice_refptid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 14, 20, 49, 27, 713676)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 14, 20, 49, 27, 721677)),
        ),
        migrations.CreateModel(
            name='ClinicFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('refptid', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to='static/clinicfiles/')),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
    ]