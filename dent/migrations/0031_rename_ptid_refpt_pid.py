# Generated by Django 4.0.3 on 2022-04-22 05:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0030_appointment_orgid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refpt',
            old_name='ptid',
            new_name='pid',
        ),
    ]