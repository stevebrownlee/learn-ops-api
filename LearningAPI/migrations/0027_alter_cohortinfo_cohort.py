# Generated by Django 4.0.3 on 2023-01-16 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LearningAPI', '0026_cohortinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cohortinfo',
            name='cohort',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='info', to='LearningAPI.cohort'),
        ),
    ]