# Register your models here.


from django.contrib import admin

# Register your models here.
from .models import SmtpConfig, SocialApp, SystemOption


@admin.register(SmtpConfig)
class SmtpConfigAdmin(admin.ModelAdmin):
    list_display = ['host_user', 'host', 'used_for']


@admin.register(SocialApp)
class SocialAppAdmin(admin.ModelAdmin):
    list_display = ['provider']


@admin.register(SystemOption)
class SystemOptionAdmin(admin.ModelAdmin):
    list_display = ['option_name', 'option_value', 'context']
