from __future__ import unicode_literals
from pws.models import Operator
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from attachment.models import Attachment
from base.choices import task_priority, task_status


class TaskType(models.Model):
    name = models.CharField(max_length=100, null=False, verbose_name="Task type")
    code = models.CharField(max_length=100, null=True, blank=True)
    icon = models.CharField(max_length=500, verbose_name="Icon", null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)


class Task(models.Model):
    name = models.CharField(max_length=200, default="")
    entity_id = models.IntegerField(null=True, blank=True, verbose_name="ID of the object")
    related_to = models.CharField(max_length=200, null=True, blank=True, verbose_name="Related to")
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.PROTECT)
    description = models.TextField(default="", verbose_name="Description", blank=True)
    due_date = models.DateTimeField(verbose_name="Due date", null=True, blank=True)
    status = models.CharField(max_length=40, choices=task_status, default="not_started", null=True, blank=True)
    priority = models.CharField(max_length=40, choices=task_priority, default="low", null=True, blank=True)
    assign_to = models.CharField(max_length=4000, null=True, blank=True)
    email_notification = models.BooleanField(verbose_name="Email notification", default=False)
    task_type = models.ForeignKey(TaskType, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Task type")
    private = models.BooleanField(verbose_name="Private task", default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    due_mail_sent_time = models.DateTimeField(null=True)
    reminder_on = models.DateTimeField(null=True, blank=True)
    reminder_on_text = models.CharField(max_length=50, null=True, blank=True)
    has_reminder_sent = models.BooleanField(default=False)
    remarks = models.TextField(verbose_name="Remarks", blank=True, null=True)
    general = models.BooleanField(verbose_name="General", default=False)
    is_delete = models.BooleanField(verbose_name="Is delete", default=False)


class Task_Attachment(Attachment):
    pass


class Message(models.Model):
    task_id = models.ForeignKey(Task, on_delete=models.PROTECT)
    operator_id = models.ForeignKey(Operator, on_delete=models.PROTECT)
    is_read = models.BooleanField(verbose_name="Is read", default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    read_on = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(verbose_name="Is delete", default=False)

