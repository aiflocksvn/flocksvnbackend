# Generated by Django 4.0 on 2022-06-29 23:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0015_alter_onlinetransaction_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='onlinetransaction',
            old_name='participant_id',
            new_name='participant',
        ),
    ]