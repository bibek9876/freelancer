# Generated by Django 4.2.3 on 2023-09-21 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("job", "0026_remove_job_hour_job_price_per"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="project_length",
            field=models.CharField(default="medium", max_length=200),
            preserve_default=False,
        ),
    ]
