# Generated by Django 4.0 on 2022-06-15 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0002_investmentparticipation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmentparticipation',
            name='investment_amount',
            field=models.IntegerField(),
        ),
    ]