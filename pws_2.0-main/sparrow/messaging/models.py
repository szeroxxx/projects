from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from post_office.models import EmailTemplate

from base.choices import event_action, event_group, notification_type


class Messaging(models.Model):
    subject = models.CharField(max_length=250, null=False, verbose_name="Subject")
    message = models.TextField(verbose_name="Message", null=True, blank=True)
    is_read = models.BooleanField(default=False, verbose_name="Read")
    parent_msg_id = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    is_resolved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)


class MessageRecipient(models.Model):
    msg = models.ForeignKey(Messaging, verbose_name="Message", null=False, on_delete=models.PROTECT)
    recipient = models.ForeignKey(User, verbose_name="Recipient", null=False, on_delete=models.PROTECT)


class Notification(models.Model):
    subject = models.CharField(max_length=250, null=False, verbose_name="Subject")
    text = models.TextField(verbose_name="Body", null=True, blank=True)
    is_read = models.BooleanField(default=False, verbose_name="Read")
    user = models.ForeignKey(User, related_name="%(class)s_subscribe", null=True, on_delete=models.PROTECT)
    type = models.CharField(blank=True, null=True, max_length=20, choices=notification_type, verbose_name="Notification type")
    entity_id = models.IntegerField(blank=True, null=True, verbose_name="Model P.K related to notification type")
    created_on = models.DateTimeField(auto_now_add=True)
    read_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    read_on = models.DateTimeField(null=True, blank=True)
    push_notify = models.BooleanField(default=False)


class SMSTemplate(models.Model):
    code = models.CharField(max_length=50, unique=True)
    content = models.CharField(max_length=600)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class NotificationEvent(models.Model):
    name = models.CharField(max_length=250, null=False)
    group = models.CharField(blank=True, null=True, max_length=30, choices=event_group)
    model = models.ForeignKey(ContentType, null=True, on_delete=models.PROTECT)
    action = models.CharField(blank=True, null=True, max_length=30, choices=event_action)
    subject = models.CharField(max_length=250, null=True)
    text = models.TextField(null=True, blank=True)
    template = models.ForeignKey(EmailTemplate, null=True, blank=True, on_delete=models.PROTECT)
    sms_template = models.ForeignKey(SMSTemplate, null=True, blank=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name.encode("utf-8")


class SubscribeNotification(models.Model):
    event = models.ForeignKey(NotificationEvent, null=False, on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name="%(class)s_subscribe", null=False, on_delete=models.PROTECT)
    by_email = models.BooleanField(default=False)
    in_system = models.BooleanField(default=False)
    by_sms = models.BooleanField(default=False)
    entity_id = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
