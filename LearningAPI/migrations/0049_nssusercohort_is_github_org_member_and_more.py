# Generated by Django 4.2.11 on 2024-07-08 03:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("LearningAPI", "0048_add_assessment_url_to_db_function"),
    ]

    operations = [
        migrations.AddField(
            model_name="nssusercohort",
            name="is_github_org_member",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name="nssusercohort",
            unique_together={("nss_user", "cohort")},
        ),
    ]
