# Generated by Django 4.2.3 on 2023-09-25 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("job", "0031_jobbid"),
    ]

    operations = [
        migrations.RemoveField(model_name="agreedjob", name="agreed_hour",),
    ]
