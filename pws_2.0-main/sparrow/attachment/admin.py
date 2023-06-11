from django.contrib import admin

from attachment.models import FileType, Tag


class FileTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description", "is_active")


admin.site.register(FileType, FileTypeAdmin)


class TypeAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "created_by")


admin.site.register(Tag, TypeAdmin)