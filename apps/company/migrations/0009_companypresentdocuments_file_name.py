# Generated by Django 4.0 on 2022-05-14 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0008_alter_companypresentdocuments_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='companypresentdocuments',
            name='file_name',
            field=models.TextField(default='documents.pdf'),
            preserve_default=False,
        ),
    ]
