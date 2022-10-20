# Generated by Django 4.0 on 2022-06-21 18:44

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenge', '0002_challenge_challengequestion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='challengequestion',
            name='answer_text',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(), default=[], size=None),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ChallengeQuestionDefaultAnswer',
        ),
    ]