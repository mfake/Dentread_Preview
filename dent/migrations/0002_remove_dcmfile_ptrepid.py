# Generated by Django 3.1.6 on 2021-10-24 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dcmfile',
            name='ptrepid',
        ),
    ]
