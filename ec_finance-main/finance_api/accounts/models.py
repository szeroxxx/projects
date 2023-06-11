from uuid import uuid4


from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
from django.db import models

profile_image_storage = FileSystemStorage()
# from base.models import *


def get_profile_image_name(instance, filename):
    from base.util import Util

    resource_img_path = Util.get_resource_path("profile", "")
    profile_image_storage.location = resource_img_path
    newfilename = str(uuid4()) + "." + filename.split(".")[-1]
    return newfilename


class MainMenu(models.Model):  # base
    name = models.CharField(max_length=150, verbose_name="Menu name")
    url = models.CharField(max_length=1000, verbose_name="Url")
    icon = models.CharField(max_length=500, verbose_name="Icon")
    parent_id = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    sequence = models.IntegerField(verbose_name="Sequence", default=0)
    is_active = models.BooleanField(default=True)
    menu_code = models.CharField(max_length=200, verbose_name="Menu Code", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        if self.parent_id is None:
            return "%s" % (self.name)
        else:
            return "%s" % (str(self.parent_id.name) + " - " + str(self.name))


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    theme = models.CharField(max_length=15, verbose_name="Color", null=True, blank=True)
    display_row = models.IntegerField(verbose_name="Display row", null=True, blank=True)
    default_page = models.TextField(max_length=250, null=True, blank=True, verbose_name="Default page loaded after login")
    profile_image = models.ImageField(storage=profile_image_storage, upload_to=get_profile_image_name, null=True, blank=True)

    def __str__(self):
        return str(self.user.username)


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
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="usergroup")
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.PROTECT)
