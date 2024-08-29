# Generated by Django 4.2.14 on 2024-08-28 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("LearningAPI", "0051_add_student_note_type_to_database_function"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentTeam",
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
                ("group_name", models.CharField(max_length=55, unique=True)),
                ("sprint_team", models.BooleanField(default=False)),
                (
                    "cohort",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="LearningAPI.cohort",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NSSUserTeam",
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
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="LearningAPI.nssuser",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="LearningAPI.studentteam",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GroupProjectRepository",
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
                ("repository_url", models.URLField()),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="LearningAPI.project",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="LearningAPI.studentteam",
                    ),
                ),
            ],
        ),
    ]