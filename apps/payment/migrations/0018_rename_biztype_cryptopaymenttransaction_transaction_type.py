# Generated by Django 4.0 on 2022-07-20 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0017_cryptopaymenteventlog_cryptopaymenttransaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cryptopaymenttransaction',
            old_name='bizType',
            new_name='transaction_type',
        ),
    ]