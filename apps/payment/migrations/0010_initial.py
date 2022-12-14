# Generated by Django 4.0 on 2022-06-29 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payment', '0009_remove_stripecustomer_user_delete_stripecharge_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partnerCode', models.TextField(null=True)),
                ('orderId', models.TextField(null=True)),
                ('requestId', models.TextField(null=True)),
                ('amount', models.IntegerField(null=True)),
                ('orderInfo', models.TextField(null=True)),
                ('orderType', models.TextField(null=True)),
                ('transId', models.TextField(null=True)),
                ('resultCode', models.TextField(null=True)),
                ('message', models.TextField(null=True)),
                ('payType', models.TextField(null=True)),
                ('responseTime', models.TextField(null=True)),
                ('extraData', models.TextField(null=True)),
                ('signature', models.TextField(null=True)),
            ],
            options={
                'db_table': 'transaction_history',
            },
        ),
    ]
