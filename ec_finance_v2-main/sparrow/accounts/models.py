from __future__ import unicode_literals

from uuid import uuid4

from base.choices import user_type
# from base.models import CommentType
from base.util import Util
from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
from django.db import models

profile_image_storage = FileSystemStorage()


def get_profile_image_name(instance, filename):
    resouce_img_path = Util.get_resource_path("profile", "")
    profile_image_storage.location = resouce_img_path
    newfilename = str(uuid4()) + "." + filename.split(".")[-1]
    return newfilename


def get_uid():
    return str(uuid4())


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    partner_id = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=0)
    avatar = models.TextField(default="")
    notification_email = models.EmailField(null=True)
    notification_mob = models.CharField(max_length=15, null=True, blank=True)
    color_scheme = models.CharField(max_length=300, verbose_name="Color Scheme", null=True, blank=True)
    image_name = models.CharField(max_length=150, verbose_name="Background image", null=True, blank=True)
    user_type = models.IntegerField(choices=user_type, verbose_name="User type", null=True)
    ip_restriction = models.NullBooleanField(verbose_name="IP Restriction", null=True, blank=True)
    purchase_plan_settings = models.TextField(max_length=1000, default="")
    display_row = models.IntegerField(verbose_name="Display row", null=True, blank=True)
    default_page = models.TextField(max_length=250, null=True, blank=True, verbose_name="Default page loaded after login")
    timezone_offset = models.IntegerField(blank=True, null=True)
    menu_launcher = models.BooleanField(default=False)
    profile_image = models.ImageField(storage=profile_image_storage, upload_to=get_profile_image_name, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    resetuid = models.CharField(default=get_uid, max_length=50)
    is_used = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)


class MainMenu(models.Model):

    name = models.CharField(max_length=150, verbose_name="Menu name", null=False)
    url = models.CharField(max_length=1000, verbose_name="Url", null=False, blank=True)
    icon = models.CharField(max_length=500, verbose_name="Icon", null=False, blank=True)
    parent_id = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    sequence = models.IntegerField(verbose_name="Sequence", default=0, null=False)
    is_active = models.BooleanField(default=True)
    is_external = models.NullBooleanField(null=True, help_text="Check if used for customer account")
    is_master = models.BooleanField(default=False)
    on_click = models.CharField(max_length=500, verbose_name="On click", null=False, blank=True)
    company_code = models.IntegerField(verbose_name="Company Code", null=True, blank=True, help_text="Specify company code if this menu is specific to company")
    menu_code = models.CharField(max_length=200, verbose_name="Menu Code", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    launcher_add_url = models.CharField(max_length=1000, verbose_name="Launcher Add New Url", null=True, blank=True)
    launcher_menu = models.BooleanField(verbose_name="Launcher menu", default=False)
    launcher_sequence = models.IntegerField(verbose_name="Launcher Sequence", null=True, blank=True, default=0, help_text="Specify the order of menu icons.")
    is_operator = models.BooleanField(verbose_name="View operator", default=False)
    is_customer_user = models.BooleanField(verbose_name="View customer user", default=False)

    def __str__(self):
        if self.parent_id is None:
            return "%s" % (self.name)
        else:
            return "%s" % (str(self.parent_id.name) + " - " + str(self.name))


class ContentPermission(models.Model):
    content_group = models.CharField(max_length=150)
    content_name = models.CharField(max_length=150)
    sequence = models.IntegerField(default=0)

    def __str__(self):
        return "%s" % (str(self.content_group) + " - " + str(self.content_name))


class PagePermission(models.Model):
    menu = models.ForeignKey(MainMenu, null=True, on_delete=models.PROTECT)
    content = models.ForeignKey(ContentPermission, null=True, on_delete=models.PROTECT)
    act_name = models.CharField(max_length=30)
    act_code = models.CharField(max_length=200)

    def __str__(self):
        return "%s" % (str(self.menu.name) + " - " + str(self.act_name))


class GroupPermission(models.Model):
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.PROTECT)
    page_permission = models.ForeignKey(PagePermission, blank=True, null=True, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return "%s" % (self.group)


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.PROTECT)


class RoleGroup(models.Model):
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=150, blank=True, null=True)
    user = models.BooleanField(default=False)
    operator = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)