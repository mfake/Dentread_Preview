# Generated by Django 4.0.3 on 2022-04-28 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0033_rename_ptid_feedfile_pid_feedfile_orgid'),
    ]

    operations = [
        migrations.AddField(
            model_name='refpt',
            name='orgid',
            field=models.ForeignKey(default=26, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
    ]