# Generated by Django 4.0 on 2022-05-11 10:13

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('media_center', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmtpConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_tls', models.BooleanField()),
                ('host', models.CharField(max_length=100)),
                ('port', models.PositiveSmallIntegerField()),
                ('host_user', models.EmailField(help_text='email address', max_length=254)),
                ('host_password', models.CharField(max_length=200)),
                ('use_ssl', models.BooleanField()),
                ('default', models.BooleanField()),
                ('used_for', models.CharField(choices=[('confirm_mail', 'confirm_mail'), ('reset_password', 'reset_password'), ('info_mail', 'info_mail')], max_length=100, unique=True)),
            ],
            options={
                'db_table': 'smtp_config',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='SocialApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hidden', models.BooleanField(default=False, editable=False)),
                ('provider', models.CharField(choices=[('google', 'google'), ('twitter', 'twitter'), ('apple', 'apple'), ('facebook', 'facebook'), ('linkedin', 'linkedin')], max_length=100, unique=True)),
                ('auth_token_url', models.CharField(max_length=150)),
                ('authenticate_url', models.CharField(max_length=100)),
                ('profile_url', models.CharField(max_length=300, null=True)),
                ('email_url', models.CharField(blank=True, max_length=200, null=True)),
                ('client_id', models.CharField(max_length=100)),
                ('client_secret', models.CharField(max_length=300)),
                ('redirect_uri', models.CharField(max_length=500)),
                ('grant_type', models.CharField(max_length=100)),
                ('basic_authorization', models.BooleanField(default=False)),
                ('scope', models.CharField(max_length=500, null=True)),
                ('response_type', models.CharField(max_length=100)),
                ('params', models.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'social_app',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='SystemOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_label', models.CharField(max_length=100)),
                ('option_name', models.CharField(choices=[('contact_mail_address', 'contact form data send to this email'), ('web_logo', 'web_logo')], max_length=100, unique=True)),
                ('option_value', models.CharField(max_length=100)),
                ('tag', models.CharField(max_length=100, null=True)),
                ('hint', models.CharField(max_length=100, null=True)),
                ('context', models.CharField(choices=[('server', 'server'), ('web', 'web')], max_length=100)),
                ('order', models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(1)])),
                ('attach', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='media_center.media')),
            ],
            options={
                'db_table': 'system_option',
                'ordering': ('order',),
            },
        ),
    ]