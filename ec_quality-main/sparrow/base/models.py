from __future__ import unicode_literals
from email.policy import default

import json
from io import StringIO

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from sqlalchemy import null
from base.choices import app_label, remark_type, scheduler_status, order_status
from attachment.models import Attachment, Tag
from qualityapp.models import Company, Operator

class AppResponse(object):
    @staticmethod
    def msg(code, message):
        msg = {"code": code, "msg": message}
        return json.dumps(msg)

    @staticmethod
    def get(object):
        s = StringIO()
        json.dump(object, s)
        s.seek(0)
        return s.read()


class DocNumber(models.Model):
    code = models.CharField(max_length=20, verbose_name="Code", null=False)
    desc = models.CharField(max_length=100, verbose_name="Description", null=True, blank=True)
    prefix = models.CharField(max_length=20, verbose_name="Prefix", null=True, blank=True, help_text="Either put fixed characters or an expression")
    # padding = models.IntegerField(verbose_name="Padding", null=False, help_text="Number of leading zeros fullfilling length")
    length = models.IntegerField(verbose_name="Length", null=False)
    increment = models.IntegerField(verbose_name="Increment by", default=1, null=False)
    nextint = models.IntegerField(verbose_name="Next integer", default=1, null=False)
    nextnum = models.CharField(max_length=30, verbose_name="Next number")

    def increase(self):
        nint = self.nextint
        pfix = self.prefix
        lng = self.length
        inc = self.increment

        val = pfix + str(nint + inc).zfill(lng)

        self.nextnum = val
        self.nextint = nint + 1


class SysParameter(models.Model):
    para_code = models.CharField(max_length=60, verbose_name="Parameter code", null=False)
    descr = models.CharField(max_length=1000, verbose_name="Description", null=True, blank=True)
    para_value = models.CharField(max_length=1000, verbose_name="Parameter value", null=False, blank=True)
    para_group = models.CharField(max_length=30, verbose_name="Parameter Group", null=True, blank=True)
    for_system = models.BooleanField(default=True)


class DMI_queries(models.Model):
    title = models.CharField(max_length=100, verbose_name="Report title", null=True, blank=True)
    descr = models.CharField(max_length=250, verbose_name="Report description", null=True, blank=True)
    report_code = models.CharField(max_length=10, verbose_name="Report code", null=True, blank=True)
    report_sql = models.CharField(max_length=2000, verbose_name="Report SQL", null=True, blank=True)
    report_para = models.CharField(max_length=300, verbose_name="Report Parameters", null=True, blank=True)
    url = models.CharField(max_length=1000, verbose_name="Url", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return "%s" % (self.title)


class FavoriteReport(models.Model):
    report = models.ForeignKey(DMI_queries, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)


class AppReport(models.Model):
    report = models.ForeignKey(DMI_queries, on_delete=models.PROTECT)
    app = models.CharField(choices=app_label, max_length=50)


class Currency(models.Model):

    name = models.CharField(max_length=40, null=False, verbose_name="Currency name")
    symbol = models.CharField(max_length=3, null=False, verbose_name="Currency symbol")
    is_base = models.BooleanField(default=False, verbose_name="Base currency")
    is_deleted = models.BooleanField(verbose_name="Deleted")

    def __str__(self):
        return "%s" % (self.name)


class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=False, related_name="currency")
    factor = models.DecimalField(null=False, max_digits=10, decimal_places=4, verbose_name="Currency factor")
    reference_date = models.DateTimeField(verbose_name="Reference date", null=False)
    expire_date = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)


class FavoriteView(models.Model):

    name = models.CharField(max_length=150, verbose_name="View name")
    url = models.CharField(max_length=500, verbose_name="View url")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)


class ReleaseNotes(models.Model):
    version = models.CharField(max_length=12, verbose_name="Release version")
    note = models.TextField(verbose_name="Release note")
    created_on = models.DateTimeField(verbose_name="Release date", null=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)


class UISettings(models.Model):
    url = models.CharField(max_length=300)
    table_index = models.IntegerField()
    col_settings = models.CharField(max_length=2000, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)


class TaskScheduler(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True, unique=True)
    code = models.CharField(max_length=15, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    schedule = models.CharField(max_length=500, blank=True, null=True, verbose_name="How often to be done", help_text="Recur Daily, Weekly, Monthly, Yearly, Specific Date")
    pattern = models.CharField(max_length=100, blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)
    last_run = models.DateTimeField(blank=True, null=True)
    last_run_result = models.CharField(max_length=500, blank=True, null=True)
    notification_email = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=scheduler_status, default="pending", null=True, blank=True)
    is_running = models.BooleanField(default=False)


# model  review pending (for https://app.clickup.com/t/2vjvt25)


class CommentType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, default="")


class Remark(models.Model):
    entity_id = models.IntegerField(null=True, blank=True, verbose_name="ID of the object")
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.PROTECT)
    remark = models.TextField(null=True, blank=True)
    remark_type = models.CharField(max_length=10, choices=remark_type, verbose_name="Remark type")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    comment_type = models.ForeignKey(CommentType, on_delete=models.PROTECT, null=True, blank=True)
    prep_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="Operator")
    prep_on = models.DateTimeField(null=True, blank=True)
    prep_section = models.CharField(choices=order_status, max_length=50, null=True, blank=True)


class Remark_Attachment(Attachment):
    pass


class Base_Attachment(Attachment):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)

class BaseAttachmentTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    attachment = models.ForeignKey(Base_Attachment, on_delete=models.CASCADE)