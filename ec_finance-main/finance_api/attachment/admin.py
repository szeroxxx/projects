from django.contrib import admin

# Register your models here.
from attachment.models import FileType


@admin.register(FileType)
class AttachmentAdmin(admin.ModelAdmin):
    list_display =['name',"code"]
