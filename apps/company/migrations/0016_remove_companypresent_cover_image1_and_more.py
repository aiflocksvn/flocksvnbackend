# Generated by Django 4.0 on 2022-10-17 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_companypresent_cover_image1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companypresent',
            name='cover_image1',
        ),
        migrations.RemoveField(
            model_name='companypresent',
            name='cover_image2',
        ),
    ]
