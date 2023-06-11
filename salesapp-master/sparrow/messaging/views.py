from django.shortcuts import render
from django.http import HttpResponse, response
from base.models import AppResponse
from auditlog.models import AuditAction
from messaging.forms import Messaging
from messaging.forms import MessageForm
from messaging.models import Messaging, MessageRecipient, Notification
from accounts.models import User, UserProfile
from base import views as base_views
from django.db import transaction
from base.util import Util
from django.template.loader import render_to_string
from django.template import RequestContext
from auditlog import views as log_views
from django.db.models import Q
import logging
import datetime
import json

def create_message(request):
    try:
        if request.method == 'POST':
            form = None
            action = AuditAction.UPDATE
            c_ip = base_views.get_client_ip(request)
            username = request.session.get('username').strip()
            form = MessageForm(request.POST)
            parent_msg_id = None
            if form.is_valid():
                user = form.save(commit = False)
                if request.POST['action'] == 'compose':
                    to_user = User.objects.filter(id = request.POST['to_user']).first()
                    parent_msg_id = Messaging.objects.filter(id = request.user.id).first()
                else:
                    to_user = User.objects.filter(email = request.POST['to_user']).first()
                    parent_msg_id = request.POST['parent_id']
               
                user.to_user = User.objects.filter(first_name__iexact = to_user.first_name).first()
                user.created_by = User.objects.filter(username__iexact = username).first()
                user.parent_msg_id_id = parent_msg_id
                user = form.save()
                response = {
                    'id': user.id,
                    'code': 1,
                    'msg': 'Send mail'
                }
                MessageRecipient.objects.create(msg_id = user.id, recipient_id = to_user.id)
                log_views.insert("messaging", "messaging", [user.id], action, request.user.id, c_ip, log_views.getLogDesc(to_user.first_name, action))
                return HttpResponse(AppResponse.get(response), content_type='json')
            else:
                return HttpResponse(AppResponse.msg(0, "Invalid form"), content_type='json')
        else:
            return render(request, 'messaging/sendmessage.html')
    except Exception as e:
        logging.exception('Something went wrong')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def get_messages(request):
    try:      
        messagesdata = []
        recipient_messages = Messaging.objects.filter(~Q(parent_msg_id_id = None)).order_by('id')
        messages = Messaging.objects.filter(Q(parent_msg_id_id = None)).order_by('-id')
        for message in messages:
            recipient_id = MessageRecipient.objects.filter(msg_id = message.id).first()
            if message.created_by.id == request.user.id or request.user.id == recipient_id.recipient_id:
                user_profile = UserProfile.objects.get(user = message.created_by)
                is_recipient = True
                if message.created_by == request.user:
                    is_recipient = False
                parent_msg = {'message': message, 'recipient_id': recipient_id, 'profile': user_profile, 'is_recipient': is_recipient}
                child_msgs = []
                for recipient_message in  recipient_messages:
                    if recipient_message.parent_msg_id_id == message.id:
                        recipient_profile = UserProfile.objects.get(user = recipient_message.created_by)
                        child_msgs.append({'message': recipient_message, "recipient_id": None, 'profile': recipient_profile})
                messagesdata.append({'parent_msg':parent_msg, 'child_msgs':child_msgs})
        return render(request, 'messaging/messages.html',{'messagesdata': messagesdata})
    except Exception as e:
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def sendmessage(request):
    return render(request, 'messaging/sendmessage.html')

def notifications(request):
    try:        
        if request.method == 'POST':
            start = 0
            length = 25
            increment = 10
            count = int(request.POST['count'])
            user_id = request.user.id

            if count != 0:
                start = length + ((count - 1) * increment)
                length = start + increment
          
            notifications = Notification.objects.filter(user_id__isnull = True, is_read=False).order_by('is_read', '-created_on')[start: length] 
            user_notifications = Notification.objects.filter(user_id = user_id, is_read=False).order_by('is_read', '-created_on')[start: length] 
            general_record = Notification.objects.filter(user_id__isnull = True, is_read=False).count()
            user_record = Notification.objects.filter(user_id=user_id, is_read=False).count()

            response = {
                'notifications': [],
                'user_notifications': [],
                'count': count,
                'user_record' : user_record,
                'general_record' : general_record
            }

            for user_notification in user_notifications:
                created_on = Util.get_local_time(user_notification.created_on,True) if user_notification.created_on is not None else ''
                response['user_notifications'].append({
                    'id': user_notification.id, 
                    'subject': user_notification.subject, 
                    'is_read': user_notification.is_read, 
                    'created_on': created_on,
                });

            for notification in notifications:
                created_on = Util.get_local_time(notification.created_on,True) if notification.created_on is not None else ''
                response['notifications'].append({
                    'id': notification.id, 
                    'subject': notification.subject, 
                    'is_read': notification.is_read, 
                    'created_on': created_on,
                });
              
            return HttpResponse(AppResponse.get(response), content_type='json')
        else:
            return render(request, 'messaging/notifications.html')            
    except Exception as e:
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')
    
def mark_as_read(request):
    try:
        with transaction.atomic():
            post_ids = request.POST.get('ids')
            if not post_ids:
                notifications = Notification.objects.filter(is_read=False)
            else:
                ids = [int(x) for x in post_ids.split(",")]

                notifications = Notification.objects.filter(id__in = ids)
            data = []
            read_by = request.user.first_name + " " + request.user.last_name
            read_on = datetime.datetime.utcnow().strftime('%d-%m-%Y')

            for notification in notifications:
                notification.is_read = True
                notification.read_by_id = request.user.id
                notification.read_on = datetime.datetime.utcnow()
                notification.save()
                data.append({'id': notification.id, 'read_by': read_by, 'read_on': read_on})

            # notification_count = Notification.objects.filter(is_read = False).count()
            notification_count = Notification.objects.filter(is_read = False, user_id__isnull = True).count()
            user_notification_count = Notification.objects.filter(is_read = False, user_id = request.user.id).count()
            response = {
                'code': 1,
                'msg': 'Selected logs marked read.',
                'notification_count': notification_count,
                'notifications': data,
                'user_notification_count': user_notification_count
            }
            return HttpResponse(AppResponse.get(response), content_type='json')
    except Exception as e:
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def mark_as_all_read(request):
    try:
        with transaction.atomic():
            user_id =  request.user.id
            is_user_nots = True if request.POST.get('is_user_notifications') =='true' else False
            if is_user_nots:
                notifications = Notification.objects.filter(is_read=False, user_id=user_id).update(is_read = True, read_by_id = request.user.id, read_on = datetime.datetime.utcnow())
            else:
                notifications = Notification.objects.filter(is_read = False, user_id__isnull = True).update(is_read = True, read_by_id = request.user.id, read_on = datetime.datetime.utcnow())

            notification_count = Notification.objects.filter(is_read = False, user_id__isnull = True).count()
            user_notification_count = Notification.objects.filter(is_read = False, user_id = request.user.id).count()
            total_count = notification_count + user_notification_count
            response = {
                'code': 1,
                'msg': 'Data saved.',
                'notification_count' : notification_count,
                'total_count' : total_count
            }
            return HttpResponse(AppResponse.get(response), content_type='json')
    except Exception as e:
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')