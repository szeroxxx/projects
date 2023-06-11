from django.contrib import admin

from auditlog.models import AuditAction, Auditlog

# Register your models here.


@admin.register(Auditlog)
class AuditlogAdmin(admin.ModelAdmin):
    list_display =["action_by","action_on","descr"]

admin.site.register(AuditAction)
