# Generated by Django 4.0 on 2022-07-20 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0018_rename_biztype_cryptopaymenttransaction_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptopaymenttransaction',
            name='amount',
            field=models.DecimalField(decimal_places=8, max_digits=20),
        ),
    ]