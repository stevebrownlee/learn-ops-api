# Generated by Django 4.2.14 on 2024-10-02 11:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "LearningAPI",
            "0052_studentteam_nssuserteam_groupprojectrepository_squashed_0060_studentteam_slack_channel",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="groupprojectrepository",
            name="repository",
            field=models.CharField(default="", max_length=255),
        ),
    ]