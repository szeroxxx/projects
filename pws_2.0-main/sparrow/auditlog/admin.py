from auditlog.models import AuditAction, Auditlog, AuditReportLog
from django.contrib import admin

# Register your models here.



@admin.register(AuditAction)
class AuditActionAdmin(admin.ModelAdmin):
    list_display = ["id", "name"][::-1]


@admin.register(Auditlog)
class AuditlogAdmin(admin.ModelAdmin):
    list_display = ["prep_time", "operator", "descr", "ip_addr", "action_by", "action_on", "action", "object_id", "content_type"][::-1]


@admin.register(AuditReportLog)
class AuditReportLogAdmin(admin.ModelAdmin):
    list_display = ["status_code", "group", "descr", "ip_addr", "action_by", "action_on", "action", "object_id", "content_type"][::-1]
