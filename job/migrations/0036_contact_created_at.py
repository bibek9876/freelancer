# Generated by Django 4.2.3 on 2023-09-25 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("job", "0035_agreedjob_created_at_jobapplies_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="created_at",
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
