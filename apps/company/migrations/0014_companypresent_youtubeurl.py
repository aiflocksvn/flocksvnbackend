# Generated by Django 4.0 on 2022-10-17 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0013_companypresent_cover_image_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companypresent',
            name='youtubeUrl',
            field=models.TextField(null=True),
        ),
    ]
