# Register your models here.
from django.contrib import admin

from .models import IdentityVerification


@admin.register(IdentityVerification)
class SmtpConfigAdmin(admin.ModelAdmin):
    # list_display = ['host_user', 'host', 'used_for']
    pass
