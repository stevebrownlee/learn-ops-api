# Generated by Django 4.2.8 on 2024-01-10 18:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("LearningAPI", "0037_alter_cohortinfo_github_classroom_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]
