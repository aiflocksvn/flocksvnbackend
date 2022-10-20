# Generated by Django 4.0 on 2022-06-29 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0005_alter_investmentparticipation_investment_amount'),
        ('company', '0011_alter_companypresent_phone_number_and_more'),
        ('payment', '0013_onlinetransaction_delete_transactionhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlinetransaction',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transaction', to='company.company'),
        ),
        migrations.AddField(
            model_name='onlinetransaction',
            name='participant_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='investment.investmentparticipation'),
        ),
        migrations.AddField(
            model_name='onlinetransaction',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='company.company'),
        ),
        migrations.AlterField(
            model_name='onlinetransaction',
            name='message',
            field=models.TextField(default='empty'),
        ),
        migrations.AlterField(
            model_name='onlinetransaction',
            name='partner_code',
            field=models.TextField(help_text='MOMOTW0N20220620', null=True),
        ),
    ]
