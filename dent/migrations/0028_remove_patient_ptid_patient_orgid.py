# Generated by Django 4.0.3 on 2022-04-15 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0027_users_propic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='ptid',
        ),
        migrations.AddField(
            model_name='patient',
            name='orgid',
            field=models.ForeignKey(default=26, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
    ]
