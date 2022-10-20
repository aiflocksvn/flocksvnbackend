# Generated by Django 4.0 on 2022-06-29 22:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_momointegrationinformation'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnlineTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('partner_code', models.TextField(null=True)),
                ('order_id', models.TextField(null=True)),
                ('request_id', models.TextField(null=True)),
                ('amount', models.IntegerField(null=True)),
                ('order_info', models.TextField(null=True)),
                ('order_type', models.TextField(null=True)),
                ('trans_id', models.TextField(null=True)),
                ('result_code', models.TextField(null=True)),
                ('message', models.TextField(null=True)),
                ('pay_type', models.TextField(null=True)),
                ('response_time', models.TextField(null=True)),
                ('extra_data', models.JSONField(null=True)),
                ('signature', models.TextField(null=True)),
            ],
            options={
                'db_table': 'transaction_history_list',
            },
        ),
        migrations.DeleteModel(
            name='TransactionHistory',
        ),
    ]