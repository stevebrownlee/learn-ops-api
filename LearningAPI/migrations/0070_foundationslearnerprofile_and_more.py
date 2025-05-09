# Generated by Django 4.2.17 on 2025-05-07 21:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("LearningAPI", "0069_alter_foundationsexercise_completed_on_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FoundationsLearnerProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("learner_github_id", models.CharField(max_length=50)),
                ("learner_name", models.CharField(max_length=75)),
                ("cohort_type", models.CharField(default="day", max_length=15)),
                ("cohort_number", models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name="foundationsexercise",
            name="cohort",
        ),
    ]
