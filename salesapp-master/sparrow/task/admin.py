from django.contrib import admin
from task.models import TaskType

class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('name','code', 'created_by')

admin.site.register(TaskType, TaskTypeAdmin)

