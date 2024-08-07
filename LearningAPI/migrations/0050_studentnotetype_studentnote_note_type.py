# Generated by Django 4.2.14 on 2024-08-02 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("LearningAPI", "0049_nssusercohort_is_github_org_member_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentNoteType",
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
                ("label", models.CharField(max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name="studentnote",
            name="note_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="LearningAPI.studentnotetype",
            ),
        ),
    ]
