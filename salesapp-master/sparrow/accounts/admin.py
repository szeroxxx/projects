from django.contrib import admin
from accounts.models import UserProfile, MainMenu, PagePermission, GroupPermission, UserGroup, ContentPermission

class MainMenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'icon', 'parent_id', 'sequence', 'menu_code','is_active', 'is_master')

class PagePermissionAdmin(admin.ModelAdmin):
    list_display = ('menu','act_name', 'act_code')

class ContentPermissionAdmin(admin.ModelAdmin):
    list_display = ('content_group','content_name', 'sequence')

admin.site.register(UserProfile)
admin.site.register(GroupPermission)
admin.site.register(UserGroup)
admin.site.register(MainMenu, MainMenuAdmin)
admin.site.register(PagePermission, PagePermissionAdmin)
admin.site.register(ContentPermission, ContentPermissionAdmin)
