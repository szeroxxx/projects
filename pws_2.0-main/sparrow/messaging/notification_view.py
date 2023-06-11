import json

from django.conf import settings
from django.db import connection
from django.http import HttpResponse

from accounts.models import UserProfile
from base.util import Util
from mails.views import send_email_by_tmpl, send_sms
from messaging.models import Notification, NotificationEvent, SubscribeNotification


def get_unread_count(request):
    notification_count = Notification.objects.filter(is_read=False, user_id__isnull=True).count()
    user_notification_count = Notification.objects.filter(is_read=False, user_id=request.user.id).count()
    user_notification_data = []
    user_notifications = Notification.objects.filter(user_id=request.user.id, is_read=False, push_notify=False).values("id", "subject")
    for user_notification in user_notifications:
        user_notification_data.append({"user_notification_id": user_notification["id"], "notification_subject": user_notification["subject"]})
    return HttpResponse(
        json.dumps({"notification_count": notification_count, "user_notification_count": user_notification_count, "user_notifications": user_notification_data}),
        content_type="json",
    )


def update_push_notify(request):
    notification_ids = json.loads(request.POST.get("user_notification_ids"))
    Notification.objects.filter(id__in=notification_ids, user_id=request.user.id).update(push_notify=True)
    return HttpResponse(json.dumps({"code": 1}), content_type="json")


def subscribe_notifications(user_id, group, model, action, entity_id, **kwargs):
    if Util.get_sys_paramter("ftr_notification").para_value == "SXFP-CHYK-ONI6-S89U":
        event = NotificationEvent.objects.filter(group=group, model__model=model, action=action).first()
        if event is not None:
            subject = event.subject
            text = event.text
            if kwargs is not None:
                for key, value in kwargs.items():
                    subject = subject.replace("#" + key + "$", str(value)) if "#" + key + "$" in subject else subject
                    text = text.replace("#" + key + "$", str(value)) if "#" + key + "$" in text else text

            gen_sub_notifications = SubscribeNotification.objects.filter(event_id=event.id, entity_id=int(entity_id), in_system=True, user_id__isnull=False).exclude(
                user_id=int(user_id)
            )
            sub_notifications = (
                SubscribeNotification.objects.filter(event_id=event.id, in_system=True, user_id__isnull=False, entity_id__isnull=True)
                .exclude(
                    event_id__in=gen_sub_notifications.values_list("event_id", flat=True).distinct(), user_id__in=gen_sub_notifications.values_list("user_id", flat=True).distinct()
                )
                .exclude(user_id=int(user_id))
            )

            for sub_notification in gen_sub_notifications:
                Notification.objects.create(subject=subject, text=text, user_id=sub_notification.user_id, entity_id=entity_id)

            for sub_notification in sub_notifications:
                Notification.objects.create(subject=subject, text=text, user_id=sub_notification.user_id)

            gen_sub_notifications = SubscribeNotification.objects.filter(event_id=event.id, entity_id=int(entity_id), by_email=True, user_id__isnull=False).exclude(
                user_id=int(user_id)
            )
            sub_notifications = (
                SubscribeNotification.objects.filter(event_id=event.id, by_email=True, user_id__isnull=False, entity_id__isnull=True)
                .exclude(
                    event_id__in=gen_sub_notifications.values_list("event_id", flat=True).distinct(), user_id__in=gen_sub_notifications.values_list("user_id", flat=True).distinct()
                )
                .exclude(user_id=int(user_id))
            )

            emails = []
            for sub_notification in gen_sub_notifications:
                noti_profile = UserProfile.objects.filter(user_id=sub_notification.user_id).first()
                emails.append(noti_profile.notification_email)

            for sub_notification in sub_notifications:
                noti_profile = UserProfile.objects.filter(user_id=sub_notification.user_id).exclude(notification_email=None).first()
                if noti_profile is not None:
                    emails.append(noti_profile.notification_email)

            if len(emails) > 0:
                send_email_by_tmpl(True, "public", emails, event.template_id, kwargs)
            if event.sms_template is not None and settings.IS_LIVE:
                gen_sub_notifications = SubscribeNotification.objects.filter(event_id=event.id, entity_id=int(entity_id), by_sms=True, user_id__isnull=False).exclude(
                    user_id=int(user_id)
                )
                sub_notifications = (
                    SubscribeNotification.objects.filter(event_id=event.id, by_sms=True, user_id__isnull=False, entity_id__isnull=True)
                    .exclude(
                        event_id__in=gen_sub_notifications.values_list("event_id", flat=True).distinct(),
                        user_id__in=gen_sub_notifications.values_list("user_id", flat=True).distinct(),
                    )
                    .exclude(user_id=int(user_id))
                )

                notification_mob = []
                for sub_notification in gen_sub_notifications:
                    noti_profile = UserProfile.objects.filter(user_id=sub_notification.user_id).first()
                    if noti_profile.notification_mob is not None and noti_profile.notification_mob != "":
                        notification_mob.append(noti_profile.notification_mob)

                for sub_notification in sub_notifications:
                    noti_profile = UserProfile.objects.filter(user_id=sub_notification.user_id).first()
                    if noti_profile.notification_mob is not None and noti_profile.notification_mob != "":
                        notification_mob.append(noti_profile.notification_mob)
                if len(notification_mob) > 0:
                    send_sms(notification_mob, event.sms_template, kwargs)


def user_notification(request, user_id, group, model, action, entity_id, **kwargs):
    if Util.get_sys_paramter("ftr_notification").para_value == "SXFP-CHYK-ONI6-S89U":
        event = NotificationEvent.objects.filter(group=group, model__model=model, action=action).first()
        if event is not None:
            subject = event.subject
            text = event.text
            if kwargs is not None:
                for key, value in kwargs.items():
                    subject = subject.replace("#" + key + "$", str(value)) if "#" + key + "$" in subject else subject
                    text = text.replace("#" + key + "$", str(value)) if "#" + key + "$" in text else text

            subscribe_notification = SubscribeNotification.objects.filter(event_id=event.id, in_system=True, user_id=user_id, entity_id__isnull=True).first()
            if subscribe_notification is not None:
                Notification.objects.create(subject=subject, text=text, user_id=user_id, entity_id=entity_id)

            subscribe_notification = SubscribeNotification.objects.filter(event_id=event.id, entity_id__isnull=True, by_email=True, user_id=user_id).first()
            if subscribe_notification is not None:
                notification_email = UserProfile.objects.filter(user_id=subscribe_notification.user_id).first().notification_email
                send_email_by_tmpl(True, "public", [notification_email], event.template_id, kwargs)

            if event.sms_template is not None and settings.IS_LIVE:
                subscribe_notification = SubscribeNotification.objects.filter(event_id=event.id, entity_id__isnull=True, by_sms=True, user_id=user_id).first()
                if subscribe_notification is not None:
                    user_profile = UserProfile.objects.filter(user_id=subscribe_notification.user_id).values("notification_mob").first()
                    if user_profile["notification_mob"]:
                        send_sms([user_profile["notification_mob"]], event.sms_template, kwargs)
