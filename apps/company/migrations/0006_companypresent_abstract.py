# Generated by Django 4.0 on 2022-05-11 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0005_companypresent_is_hot_companypresent_is_trends'),
    ]

    operations = [
        migrations.AddField(
            model_name='companypresent',
            name='abstract',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]