# Generated by Django 3.2.5 on 2022-02-14 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pathology', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='advice',
            field=models.TextField(blank=True, null=True, verbose_name='诊断意见'),
        ),
    ]
