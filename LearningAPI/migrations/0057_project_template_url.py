# Generated by Django 4.2.14 on 2024-08-29 19:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("LearningAPI", "0056_rename_members_studentteam_students"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="template_url",
            field=models.CharField(default="", max_length=256),
        ),
    ]