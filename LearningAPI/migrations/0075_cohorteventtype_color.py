# Generated by Django 5.2.3 on 2025-06-22 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LearningAPI', '0074_cohortevent_event_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='cohorteventtype',
            name='color',
            field=models.CharField(default='#ffffff', help_text='Color associated with the event type in hex format', max_length=7),
        ),
    ]
