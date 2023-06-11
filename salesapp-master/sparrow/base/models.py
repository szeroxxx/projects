from __future__ import unicode_literals

from django.db import models
from io import StringIO
import json
from django.contrib.auth.models import User
from base.choices import *
from django.contrib.contenttypes.models import ContentType
from attachment.models import Attachment

class AppResponse(object):

    @staticmethod
    def msg(code, message):
        msg = { "code" : code, "msg" : message }
        return json.dumps(msg)

    @staticmethod
    def get(object):
        s = StringIO()    
        json.dump(object, s)
        s.seek(0)
        return s.read()

class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    token = models.CharField(max_length=20)
    expire_on = models.DateTimeField()
    is_used = models.BooleanField(default=False)

class DocNumber(models.Model):
    code = models.CharField(max_length=20,verbose_name="Code", null=False)
    desc = models.CharField(max_length=100,verbose_name="Description", null=True, blank=True)
    prefix = models.CharField(max_length=20,verbose_name="Prefix", null=True, blank=True, help_text="Either put fixed characters or an expression")
    #padding = models.IntegerField(verbose_name="Padding", null=False, help_text="Number of leading zeros fullfilling length")
    length = models.IntegerField(verbose_name="Length", null=False)
    increment = models.IntegerField(verbose_name="Increment by", default=1, null=False)
    nextint = models.IntegerField(verbose_name="Next integer", default=1, null=False)
    nextnum = models.CharField(max_length=30,verbose_name="Next number")

    def increase(self):
        nint = self.nextint
        pfix = self.prefix
        lng = self.length
        inc = self.increment

        val = pfix + str(nint+inc).zfill(lng)

        self.nextnum = val
        self.nextint = nint+1

class SysParameter(models.Model):
    para_code = models.CharField(max_length=60,verbose_name="Parameter code", null=False)
    descr = models.CharField(max_length=250,verbose_name="Description", null=True, blank=True)
    para_value = models.CharField(max_length=1000,verbose_name="Parameter value", null=False)
    para_group = models.CharField(max_length=30,verbose_name="Parameter Group", null=True, blank=True)

class DMI_queries(models.Model):
    title = models.CharField(max_length=100, verbose_name="Report title", null=True, blank=True)
    descr = models.CharField(max_length=250, verbose_name="Report description", null=True, blank=True)
    report_code = models.CharField(max_length=10, verbose_name="Report code", null=True, blank=True)
    report_sql = models.CharField(max_length=2000, verbose_name="Report SQL", null=True, blank=True)
    report_para = models.CharField(max_length=300, verbose_name="Report Parameters", null=True, blank=True)
    url = models.CharField(max_length = 1000, verbose_name="Url", null = True, blank = True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return '%s' % (self.title)

class FavoriteReport(models.Model):
    report = models.ForeignKey(DMI_queries, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

class AppReport(models.Model):
    report = models.ForeignKey(DMI_queries, on_delete=models.PROTECT)
    app = models.CharField(choices = app_label, max_length=50)

class FavoriteView(models.Model):
    
    name = models.CharField(max_length=150, verbose_name='View name')
    url = models.CharField(max_length=500, verbose_name='View url')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

class ReleaseNotes(models.Model):
    version = models.CharField(max_length=12, verbose_name='Release version')
    note = models.TextField(verbose_name='Release note')    
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

class Remark(models.Model):
    entity_id = models.IntegerField(null=True, blank=True, verbose_name="ID of the object")
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.PROTECT)
    remark = models.TextField(null=True, blank=True)
    remark_type = models.CharField(max_length=10, choices=remark_type, verbose_name="Remark type")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

class UISettings(models.Model):
    url = models.CharField(max_length= 300)
    table_index = models.IntegerField()
    col_settings = models.CharField(max_length=500, null= True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

class Remark_Attachment(Attachment):
    pass    
