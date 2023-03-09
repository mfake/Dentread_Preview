# Generated by Django 4.0.3 on 2022-04-15 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0028_remove_patient_ptid_patient_orgid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='ptid',
        ),
        migrations.RemoveField(
            model_name='report',
            name='ptid',
        ),
        migrations.AddField(
            model_name='invoice',
            name='orgid',
            field=models.ForeignKey(default=26, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='pid',
            field=models.IntegerField(default=26),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='refdoctor',
            name='orgid',
            field=models.ForeignKey(default=26, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='orgid',
            field=models.ForeignKey(default=26, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='pid',
            field=models.IntegerField(default=26),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='study',
            name='orgid',
            field=models.ForeignKey(default=26, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
    ]
