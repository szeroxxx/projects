from django.contrib import admin
from task.models import Task, TaskType, Message, Task_Attachment


admin.site.register(Task_Attachment)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["is_delete", "general", "remarks", "has_reminder_sent", "reminder_on_text", "reminder_on", "due_mail_sent_time", "created_by", "created_on", "private", "task_type", "email_notification", "assign_to", "priority", "status", "due_date", "description", "content_type", "related_to", "entity_id", "name"][::-1]


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ["created_by", "created_on", "icon", "code", "name"][::-1]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["is_delete", "read_on", "created_on", "is_read", "operator_id", "task_id"][::-1]
