from django.utils.translation import ugettext_lazy as _
import logging
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from sales.models import Invoice

try:
    from idmapper.models import SharedMemoryModel as Model
except ImportError:
    Model = models.Model


LOG_LEVELS = (
    (logging.INFO, _("info")),
    (logging.WARNING, _("warning")),
    (logging.DEBUG, _("debug")),
    (logging.ERROR, _("error")),
    (logging.FATAL, _("fatal")),
)


class ErrorBase(Model):
    class_name = models.CharField(_("type"), max_length=128, blank=True, null=True, db_index=True)
    level = models.PositiveIntegerField(choices=LOG_LEVELS, default=logging.ERROR, blank=True, db_index=True)
    message = models.TextField()
    traceback = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

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
    action_by = models.ForeignKey(User, on_delete=models.PROTECT,null=True,blank=True)
    username = models.CharField(max_length=200,null=True,blank=True)
    ip_addr = models.CharField(default="", max_length=45)
    descr = models.TextField(default="")
    status_code = models.CharField(default="", max_length=45)
    group = models.CharField(default="", max_length=45) # New column add
    document_no = models.CharField(default="", max_length=45,null=True)


# class AuditReportLog(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
#     object_id = models.IntegerField(null=False)
#     action = models.ForeignKey(AuditAction, on_delete=models.PROTECT)
#     action_on = models.DateTimeField(blank=True, null=True)
#     action_by = models.ForeignKey(User, on_delete=models.PROTECT)
#     ip_addr = models.CharField(default="", max_length=45)
#     descr = models.TextField(default="")
#     group = models.CharField(default="", max_length=45)
#     status_code = models.CharField(default="", max_length=45)


class InvoiceHistory(models.Model):
    entity = models.ForeignKey(Invoice, on_delete=models.PROTECT,null=True,blank=True)
    entity_type = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    status_code = models.CharField(default="", max_length=45)
    action = models.CharField(max_length=100)
    created_on = models.DateTimeField(blank=True, null=True)
    ip_address =  models.CharField(default="", max_length=45,null=True)
    document_no = models.CharField(default="", max_length=45,null=True)
    old_value = models.DecimalField(decimal_places=5,max_digits=12,null=True)