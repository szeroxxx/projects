from django.contrib import admin

from accounts.models import (ContentPermission, GroupPermission, MainMenu,
                             PagePermission, UserGroup, UserProfile)


@admin.register(MainMenu)
class MainMenuAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "icon", "parent_id", "sequence", "menu_code")

@admin.register(PagePermission)
class PagePermissionAdmin(admin.ModelAdmin):
    list_display = ("menu", "act_name", "act_code")

@admin.register(ContentPermission)
class ContentPermissionAdmin(admin.ModelAdmin):
    list_display = ("content_group", "content_name", "sequence")

admin.site.register(UserProfile)
admin.site.register(GroupPermission)
admin.site.register(UserGroup)
