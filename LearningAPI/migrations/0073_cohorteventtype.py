# Generated by Django 5.2.3 on 2025-06-21 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LearningAPI', '0072_alter_cohortevent_cohort'),
    ]

    operations = [
        migrations.CreateModel(
            name='CohortEventType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(help_text='Name of the event', max_length=255)),
            ],
        ),
    ]
