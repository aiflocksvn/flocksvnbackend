# Generated by Django 4.0 on 2022-06-16 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_stripecharge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripecharge',
            name='balance_transaction',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
