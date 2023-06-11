from accounts.models import (ContentPermission, GroupPermission, MainMenu,
                             PagePermission, RoleGroup, UserGroup, UserProfile)
from django.contrib import admin




@admin.register(ContentPermission)
class ContentPermissionAdmin(admin.ModelAdmin):
    list_display = ["sequence", "content_name", "content_group"][::-1]


@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ["created_by", "created_on", "page_permission", "group"][::-1]


@admin.register(MainMenu)
class MainMenuAdmin(admin.ModelAdmin):
    list_display = ["is_customer_user", "is_operator", "launcher_sequence", "launcher_menu", "launcher_add_url", "created_by", "menu_code", "company_code", "on_click", "is_master", "is_external", "is_active", "sequence", "parent_id", "icon", "url", "name"][::-1]


@admin.register(PagePermission)
class PagePermissionAdmin(admin.ModelAdmin):
    list_display = ["act_code", "act_name", "content", "menu"][::-1]


@admin.register(RoleGroup)
class RoleGroupAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "operator", "user", "description", "group"][::-1]


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ["group", "user"][::-1]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["session_key", "profile_image", "menu_launcher", "timezone_offset", "display_row", "purchase_plan_settings", "ip_restriction", "user_type", "image_name", "color_scheme", "notification_mob", "notification_email", "avatar", "is_deleted", "partner_id", "user"][::-1]
