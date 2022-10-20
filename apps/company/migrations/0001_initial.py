# Generated by Django 4.0 on 2022-05-11 10:13

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
        ('dashboard', '0001_initial'),
        ('media_center', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('status', models.CharField(choices=[('approved', 'approved'), ('rejected', 'rejected'), ('pending', 'pending')], default='pending', max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('company_name', models.TextField(unique=True)),
                ('entrepreneur_name', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None)),
                ('website', models.TextField()),
                ('email', models.TextField()),
                ('address', models.TextField()),
                ('phone_number', models.TextField()),
                ('github', models.TextField(blank=True, null=True)),
                ('intro_video', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='intro_video_media', to='media_center.media')),
                ('registration_docs', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='register_doc_media', to='media_center.media')),
                ('tax_receipt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tax_doc_media', to='media_center.media')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_company', to='authentication.systemuser')),
            ],
            options={
                'db_table': 'company',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CompanyPresent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('company_name', models.TextField()),
                ('company_sub_title', models.TextField()),
                ('Legal_name', models.TextField(null=True)),
                ('founded', models.DateField()),
                ('employees', models.IntegerField(null=True)),
                ('website', models.TextField(null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('phone_number', models.EmailField(max_length=254, null=True)),
                ('location', models.TextField(null=True)),
                ('facebook', models.TextField(null=True)),
                ('twitter', models.TextField(null=True)),
                ('linkedin', models.TextField(null=True)),
                ('instagram', models.TextField(null=True)),
                ('youtube', models.TextField(null=True)),
                ('investment_min', models.IntegerField()),
                ('investment_target', models.IntegerField()),
                ('price_per_share', models.DecimalField(decimal_places=4, max_digits=30)),
                ('shares_offered', models.TextField(null=True)),
                ('offering_type', models.TextField(null=True)),
                ('closing_date', models.DateField(null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='company_present', to='company.company')),
            ],
            options={
                'db_table': 'company_present',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CompanyPresentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'company_present_category',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CompanyPresentTeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('position', models.TextField()),
                ('about', models.TextField()),
                ('linkedin', models.TextField()),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_present_team_member', to='company.companypresent')),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_present_team_member', to='media_center.media')),
            ],
            options={
                'db_table': 'company_present_team_member',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CompanyPresentHeaderSlider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(1)])),
                ('company_present', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media_center.media')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_present_header_slider', to='media_center.media')),
            ],
            options={
                'db_table': 'company_present_header_slider',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CompanyPresentDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='present_document', to='media_center.media')),
            ],
            options={
                'db_table': 'company_present_documents',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CompanyPresentDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('details', models.TextField()),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='present_details', to='company.companypresent')),
            ],
            options={
                'db_table': 'company_present_details',
                'ordering': ('id',),
            },
        ),
        migrations.AddField(
            model_name='companypresent',
            name='company_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='company_present_category', to='company.companypresentcategory'),
        ),
        migrations.AddField(
            model_name='companypresent',
            name='cover_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='company_present_preview', to='media_center.media'),
        ),
        migrations.AddField(
            model_name='companypresent',
            name='logo_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='company_present_logo', to='media_center.media'),
        ),
        migrations.CreateModel(
            name='CompanyDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('attachment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_details_media', to='media_center.media')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='company_details', to='company.company')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dashboard.question')),
            ],
            options={
                'db_table': 'company_details',
                'ordering': ('id',),
            },
        ),
    ]
