from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from pws.models import Operator


class AuditAction(models.Model):
    INSERT = 1
    UPDATE = 2
    DELETE = 3

    name = models.CharField(blank=False, max_length=200)

    @staticmethod
    def get_action_id(name):
        return AuditAction.objects.filter(name=name).first().id


class Auditlog(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.IntegerField(null=False)
    action = models.ForeignKey(AuditAction, on_delete=models.PROTECT)
    action_on = models.DateTimeField(auto_now=True)
    action_by = models.ForeignKey(User, on_delete=models.PROTECT)
    ip_addr = models.CharField(default="", max_length=45)
    descr = models.TextField(default="")
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True)
    prep_time = models.IntegerField(null=True, blank=True)


class AuditReportLog(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.IntegerField(null=False)
    action = models.ForeignKey(AuditAction, on_delete=models.PROTECT)
    action_on = models.DateTimeField(blank=True, null=True)
    action_by = models.ForeignKey(User, on_delete=models.PROTECT)
    ip_addr = models.CharField(default="", max_length=45)
    descr = models.TextField(default="")
    group = models.CharField(default="", max_length=45)
    status_code = models.CharField(default="", max_length=45)
