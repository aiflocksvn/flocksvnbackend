# Generated by Django 4.0 on 2022-06-29 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0011_rename_extradata_transactionhistory_order_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MomoIntegrationInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_code', models.TextField(null=True)),
                ('access_key', models.TextField(null=True)),
                ('secret_key', models.TextField(null=True)),
            ],
            options={
                'db_table': 'momo_integration_info',
            },
        ),
    ]
