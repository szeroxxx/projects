from django.contrib import admin
from messaging.models import NotificationEvent,SMSTemplate

class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'model', 'action', 'template','sms_template', 'subject','text','is_active','created_by')

class SMSTemplateAdmin(admin.ModelAdmin):
	list_display = ('code', 'content','created_by')	

admin.site.register(NotificationEvent, NotificationEventAdmin)
admin.site.register(SMSTemplate, SMSTemplateAdmin)
