from django.contrib import admin
from messaging.models import (MessageRecipient, Messaging, Notification,
                              NotificationEvent, SMSTemplate,
                              SubscribeNotification)



@admin.register(MessageRecipient)
class MessageRecipientAdmin(admin.ModelAdmin):
    list_display = ["recipient", "msg"][::-1]


@admin.register(Messaging)
class MessagingAdmin(admin.ModelAdmin):
    list_display = ["created_on", "created_by", "is_resolved", "parent_msg_id", "is_read", "message", "subject"][::-1]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["push_notify", "read_on", "read_by", "created_on", "entity_id", "type", "user", "is_read", "text", "subject"][::-1]


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ["created_on", "created_by", "is_active", "sms_template", "template", "text", "subject", "action", "model", "group", "name"][::-1]


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ["created_on", "created_by", "content", "code"][::-1]


@admin.register(SubscribeNotification)
class SubscribeNotificationAdmin(admin.ModelAdmin):
    list_display = ["created_on", "created_by", "entity_id", "by_sms", "in_system", "by_email", "user", "event"][::-1]
