from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from base.models import AppResponse, DocNumber, SysParameter
from django.template import RequestContext
from django.template import Context, Template
from django.template.loader import render_to_string
from django.db import transaction
from auditlog.models import AuditAction
import base.views as base_views
from django.contrib.auth.models import User
from auditlog import views as log_views
from django.core import serializers
from base.util import Util
import json
import unicodedata
from django.conf import settings
import logging
import datetime
from exception_log import manager
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from task.models import Task, task_status, task_priority, TaskType
from task.forms import TaskForm
from post_office.models import EmailTemplate
from mails.views import send_email_by_tmpl, send_mail, send_sms
from django.db import connection
from django.utils.timezone import utc
import psycopg2 as pg
from accounts.models import UserProfile
import pdb
from datetime import date
from stronghold.decorators import public
from django.views.decorators.csrf import csrf_exempt
from messaging.notification_view import subscribe_notifications, user_notification
from messaging.models import Notification
from base import choices
from accounts.services import CompanyService
import os

def tasks(request):
    return render(request, 'task/tasks.html')

def get_tasks(request, app_name=None, model_name=None, entity_id=None):
    try:
        request.POST = Util.get_post_data(request)    
        start = int(request.POST['start'])
        length = int(request.POST['length'])
        sort_col = Util.get_sort_column(request.POST) if 'order' in request.POST else '-id'
        task_filter = request.COOKIES.get('taskFilter')
        if sort_col == 'id' or sort_col == '-task_id':
            sort_col = 'id'
        if sort_col == 'task_id':
            sort_col = '-id'

        query=Q()
        if request.POST.get('model_name') != None:
            model_name = request.POST.get('model_name')
            if model_name == 'Purchase order':
                model_name = 'PurchaseOrder'
            elif model_name == 'Sales order':
                model_name = 'order'
            elif model_name == 'Lead' :
                model_name = 'lead'
            elif model_name == 'Receipt':
                model_name = 'receipt'
            elif model_name == 'Shipment':
                model_name = 'shipment'

        if request.POST.get('name__icontains') != None:
            query.add(Q(name__icontains=str(request.POST.get('name__icontains'))), query.connector)
        if request.POST.get('due_date__date') != None:
            query.add(Q(due_date__date = datetime.datetime.strptime(str(request.POST['due_date__date']), '%d/%m/%Y %H:%M').strftime('%m/%d/%Y %H:%M')), query.connector)
        if request.POST.get('task_type__name__icontains') != None:
            query.add(Q(task_type__name__icontains=str(request.POST.get('task_type__name__icontains'))), query.connector)
        if request.POST.get('status__icontains') != None:
            query.add(Q(status__icontains=str((request.POST.get('status__icontains')).replace(" ", "_"))), query.connector)
        if request.POST.get('priority__icontains') != None:
            query.add(Q(priority__icontains=str(request.POST.get('priority__icontains'))), query.connector)


        
        if app_name != '0' and model_name != '0' and entity_id != '0':
            content_type = ContentType.objects.filter(app_label = app_name.lower(), model = model_name.lower()).first()
            query.add(Q(entity_id = int(entity_id), content_type = content_type), query.connector)
        elif model_name != '0':
            if model_name == 'crm':
                content_type_ids = ContentType.objects.filter(model__in = ['contact', 'lead', 'deal']).values_list('id', flat = True)
                query.add(Q(content_type_id__in = content_type_ids), query.connector)
            if model_name == 'receipt':    
                receipt_ids = TransferOrder.objects.filter(id__in = task_ids, transfer_type__in = ['receipt', 'so_return', 'customer_supplied']).values_list('id', flat=True)
                query.add(Q(entity_id__in = receipt_ids), query.connector)
            elif model_name == 'shipment':
                ship_ids = TransferOrder.objects.filter(id__in = task_ids, transfer_type__in = ['ship', 'purchase_return']).values_list('id', flat=True)
                query.add(Q(entity_id__in = ship_ids), query.connector)
            elif model_name != 'crm':
                content_type = ContentType.objects.filter(model = model_name.lower()).first()
                query.add(Q(content_type = content_type), query.connector)
                # query.add(Q(content_type = content_type__app_label), query.connector)
            else:
                content_type = ContentType.objects.filter(model = 'transferorder').first()
                task_ids = Task.objects.filter(content_type = content_type).values_list('entity_id', flat=True)

        if task_filter:
            if task_filter == 'due_date':
                sort_col = 'due_date'

            if task_filter == 'assign_to':
                sort_col = 'assign_to__first_name'

            if task_filter == 'alphabetical':
                sort_col = 'name'

            if task_filter != 'completed':
                query.add(~Q(status = 'completed'), query.connector)
                if task_filter == 'my' or task_filter == 'my_due':
                    query.add(Q(assign_to_id = request.user.id), query.connector)
            else:
                query.add(Q(status = 'completed'), query.connector)

        else:
            query.add(~Q(status = 'completed'), query.connector)
        
        tasks = Task.objects.filter(query).values('id', 'name', 'description', 'due_date', 'status', 'priority','related_to', 'entity_id',
                            'assign_to_id','assign_to', 'created_by', 'private', 'assign_to_id', 'created_by_id','content_type', 'content_type__model', 'content_type__app_label',
                            'assign_to__first_name', 'assign_to__last_name', 'created_by__first_name', 
                            'created_by__last_name', 'created_on', 'task_type_id', 'task_type__name', 'task_type__icon','remarks').order_by(sort_col)[start: length]

        user_task = Task.objects.filter(assign_to_id = request.user.id).exclude(status = 'completed').count()

        response = {
            # 'draw': request.POST['draw'] if request.POST['draw'] else '',
            'recordsTotal': tasks.count(),
            'recordsFiltered': tasks.count(),
            'user_count': user_task,
            'data': []
        }
        user_id = tasks.values_list('assign_to_id',flat=True)
        print(user_id,'user_id')

        users = UserProfile.objects.filter(user_id__in = user_id).values('user_id', 'profile_image')
        imageurl = {}
        for user in users:
            imageurl[user['user_id']] = user['profile_image']

        for task in tasks:    
            if task['private']:
                if request.user.id != task['created_by_id'] and request.user.id != task['assign_to_id']:
                    continue
            task_obj = get_task_obj(task)
            img_src = Util.get_resource_url('profile', str(imageurl[task['assign_to_id']])) if task['assign_to_id'] in imageurl and imageurl[task['assign_to_id']] else ''
            print(img_src,'img_src')
            task_obj['img_src'] = img_src
            task_obj['due_date_year'] = task['due_date'].strftime('%Y') if task['due_date'] else ''

            task_obj['assign_to_id'] =  request.user.id if task['assign_to_id'] == None  else task['assign_to_id']
            
            if app_name == '0' and model_name == '0' and (task_filter == 'overdue'  or task_filter == 'my_due'):
                if task_obj['is_due']:                    
                    response['data'].append(task_obj)
            else:                       
                response['data'].append(task_obj)

                
        response['recordsTotal'] = len(response['data'])
        response['recordsFiltered'] = len(response['data'])
        return HttpResponse(AppResponse.get(response), content_type='json')

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')    

def get_task_calendar(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        task_filter = request.COOKIES.get('taskFilter')
        user_id = request.user.id
        model_name = request.POST.get('model_name')
        if task_filter:
            if task_filter != 'completed':
                query.add(~Q(status = 'completed'), query.connector) 
                if task_filter == 'my' or task_filter == 'my_due':
                    query.add(Q(assign_to_id = request.user.id), query.connector)
            else:
                query.add(Q(status = 'completed'), query.connector)
        else:
            query.add(~Q(status = 'completed'), query.connector)
            query.add(Q(assign_to_id = request.user.id), query.connector)

        current_month = int(request.POST.get('current_month'))
        query.add(Q(due_date__month = current_month), query.connector)
        response = {
            'data': []
        }

        if model_name == 'crm':
            content_type_ids = ContentType.objects.filter(model__in = ['contact', 'lead', 'deal']).values_list('id', flat = True)
            query.add(Q(content_type_id__in = content_type_ids), query.connector)

        tasks = Task.objects.filter(query).values('id', 'name', 'description', 'due_date', 'status', 'priority','related_to',
                            'assign_to', 'created_by', 'private', 'assign_to_id', 'created_by_id',
                            'assign_to__first_name', 'assign_to__last_name', 'created_by__first_name', 
                            'created_by__last_name', 'created_on', 'task_type_id', 'task_type__name', 'task_type__icon','remarks')

        assign_ids = tasks.values_list('assign_to_id', flat = True)

        users = UserProfile.objects.filter(user_id__in = assign_ids).values('user_id', 'profile_image')

        imageurl = {}
        for user in users:
            imageurl[user['user_id']] = user['profile_image']

        for task in tasks:
            if task['private']:
                if user_id != task['created_by_id'] and user_id != task['assign_to_id']:
                    continue
            img_src = Util.get_resource_url('profile', str(imageurl[task['assign_to_id']])) if task['assign_to_id'] and imageurl[task['assign_to_id']] else ''
            if task_filter == 'overdue' or task_filter == 'my_due':
                if Util.get_local_time(task['due_date'], True) and Util.get_local_time(datetime.datetime.utcnow(), True) > Util.get_local_time(task['due_date'], True):
                    response['data'].append({
                        'id': task['id'],
                        'title': task['name'],
                        'start': Util.get_local_time(task['due_date'], True, '%Y-%m-%dT%H:%M'),
                        'imageurl': img_src,
                        'color': '#FFA500',
                    })
            else:
                response['data'].append({
                        'id': task['id'],
                        'title': task['name'],
                        'start': Util.get_local_time(task['due_date'], True, '%Y-%m-%dT%H:%M'),
                        'imageurl': img_src,
                        'color': '#FFA500',
                    })
        return HttpResponse(AppResponse.get(response), content_type='json')

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception('Something went wrong.')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def task_kanban_data(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        task_filter = request.COOKIES.get('taskFilter')
        start_length = request.POST.get('start_length')
        end_length = request.POST.get('end')
        model_name = request.POST.get('model_name')
        response = {
            'data': []
        }

        all_task_status = [key for key in dict(task_status).keys()]
        temp = all_task_status[2]
        all_task_status[2] = all_task_status[1]
        all_task_status[1] = temp
        task_status_list = []
        status_name = request.POST.get('status_name', None)
        if status_name == None:
            task_status_list = all_task_status 
        else:
            task_status_list = [status_name]

        response['all_task_status'] = all_task_status
        
        status_class = {}
        for status in all_task_status:
            if status == 'completed':
                status_class[status] = 'completed'
            elif status == 'in_progress':
                status_class[status] = 'inProgress'
            elif status == 'not_started':
                status_class[status] = 'notStarted'
        
        if task_filter:
            if task_filter != 'completed':
                if task_filter == 'my' or task_filter == 'my_due':
                    query.add(Q(assign_to_id = request.user.id), query.connector)
            else:
                query.add(Q(status = 'completed'), query.connector)
        else:
            query.add(Q(assign_to_id = request.user.id), query.connector)

        if model_name == 'crm':
            content_type_ids = ContentType.objects.filter(model__in = ['contact', 'lead', 'deal']).values_list('id', flat = True)
            query.add(Q(content_type_id__in = content_type_ids), query.connector)

        assign_ids = Task.objects.filter(query).values_list('assign_to_id', flat = True)
        users = UserProfile.objects.filter(user_id__in = assign_ids).values('user_id', 'profile_image')
        imageurl = {}
        for user in users:
            imageurl[user['user_id']] = user['profile_image']

        for status in task_status_list:
            item = []
            tasks = Task.objects.filter(query, status = status).values('id', 'name','created_by_id', 'due_date', 'private','assign_to_id', 'assign_to__first_name', 'assign_to__last_name','remarks').order_by('-id')[int(start_length): int(end_length)]
            for task in tasks:
                if task['private']:
                    if request.user.id != task['created_by_id'] and request.user.id != task['assign_to_id']:
                        continue
                color = 'gray'
                if Util.get_local_time(task['due_date'], True) and Util.get_local_time(datetime.datetime.utcnow(), True) > Util.get_local_time(task['due_date'], True):
                    color = '#EF7878'
                img_src = Util.get_resource_url('profile', str(imageurl[task['assign_to_id']])) if task['assign_to_id'] and task['assign_to_id'] in imageurl and imageurl[task['assign_to_id']] else ''
                assign_info = '<img id="taskUserImg" src="'+ img_src  +'" width="22" height="22" title="'+task['assign_to__first_name']+' '+task['assign_to__last_name']+'" style="float:right">' if img_src else ''
                assign_info += '<span class="icon-message-3-write" style="color: #989898;float:right;padding:3px;font-size:18px;margin-right: 5px;"></span>' if task['remarks'] else''
                # assign_info += '<span class="assignName">'+task['assign_to__first_name']+' '+task['assign_to__last_name']+'</span>' if task['assign_to_id'] else ''
                due_date = task['due_date'].strftime("%d, %b") if task['due_date'] else ''
                assign_info += ' <span class="kanbanDueDate" style="color:'+color+';float:left;margin-top: 2px;"> Due on '+due_date+'</span>' if due_date else ''
                item.append({
                    'id': str(task['id']),
                    'title': '<div>'+ task['name'] +'</div><div style="margin-top: 12px;">'+assign_info+'</div>'
                })
            response['data'].append({
                'id': status,
                'title': dict(task_status)[status],
                'item': item,
                'class': status_class[status] if status != 'cancelled' else ''
            })
        return HttpResponse(AppResponse.get(response), content_type='json')
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception('Something went wrong.')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def change_task_status(request):
    try:
        task_id = int(request.POST.get('task_id'))
        task_status = request.POST.get('status_name')
        task = Task.objects.filter(id = task_id).update(status = task_status)
        task = Task.objects.filter(id = task_id).values('id', 'name', 'description', 'due_date', 'status','related_to',
                'priority', 'assign_to', 'created_by', 'assign_to__first_name', 'assign_to__last_name','entity_id', 
                'created_by__first_name', 'created_by__last_name', 'created_on', 'task_type_id','content_type__model','content_type__app_label',
                'task_type__name', 'task_type__icon','remarks').first()
        task_obj = get_task_obj(task)

        if task_obj['status'] == 'Completed':
            send_notification(request, task_obj, 'completed')

        return HttpResponse(AppResponse.msg(1, ''), content_type = 'json')
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception('Something went wrong.')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def change_event_date(request):
    try:
        task_id = request.POST.get('task_id')
        change_date = request.POST.get('drop_date').replace('T', ' ')
        change_date = datetime.datetime.strptime(change_date, "%Y-%m-%d %H:%M:%S").strftime('%d/%m/%Y %H:%M')
        change_date = Util.get_utc_datetime(change_date)
        Task.objects.filter(id = task_id).update(due_date = change_date)
        return HttpResponse(AppResponse.msg(1, 'Date changed'), content_type='json')

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')


def get_task_obj(task):
    first_name = task['assign_to__first_name'] if task['assign_to'] else ''
    last_name = task['assign_to__last_name'] if task['assign_to'] else ''
    cfirst_name = task['created_by__first_name'] if task['created_on'] else ''
    clast_name = task['created_by__last_name'] if task['created_on'] else ''
    is_due = False
    
    if Util.get_local_time(task['due_date']) and str(date.today()) > task['due_date'].strftime('%Y-%m-%d'):
        is_due = True

    model_type = ''

    if task['content_type__app_label']=='partners':
        if task['content_type__model']=='partner':
            partner = Partner.objects.filter(id=task['entity_id']).values('is_supplier','is_customer').first()

            if partner['is_supplier']:
                model_type = 'supplier'

            if partner['is_customer']:
                model_type = 'customer'
    
    if task['content_type__app_label']=='logistics':
        if task['content_type__model']=='transferorder':
            trasfer_type=TransferOrder.objects.filter(id=task['entity_id']).values('transfer_type').first()

            if trasfer_type['transfer_type']=='ship':
                model_type ='shipment'

            if trasfer_type['transfer_type']=='customer_supplied':
                model_type ='receipt'

    return {
        'id': task['id'],
        'task_id': task['id'],
        'name': task['name'],
        'description' : task['description'],
        'related_to': task['related_to'],
        'due_date' : Util.get_local_time(task['due_date'], True) if task['due_date'] is not None else '',
        'is_due' :is_due,
        'task_type__name': task['task_type__name'],
        'task_type__icon': task['task_type__icon'],
        'status': dict(task_status).get(task['status']),
        'priority' : dict(task_priority).get(task['priority']),
        'assign_to' :  first_name+ ' '+ last_name,
        'created_by' :  cfirst_name+ ' '+ clast_name,
        'created_on' : Util.get_local_time(task['created_on'], True),
        'remarks':task['remarks'] if task['remarks'] != None else '',
        'entityId': task['entity_id'],
        'modelName':task['content_type__model'],
        'appName':task['content_type__app_label'],
        'type':model_type,
    }

def task(request):
    try:
        if request.method == 'POST':
            task_id = request.POST.get('id')
            tz_offset = CompanyService.get_root_compnay()['timezone_offset']
            time_frmt =  '{:02d}:{:02d}' if tz_offset < 0 else '+{:02d}:{:02d}'
            tz_info = time_frmt.format(*divmod(tz_offset, 60))
            task_status = json.dumps(dict(choices.task_status))
            task_priority = json.dumps(dict(choices.task_priority))
            show_private = False
            show_public=True
            if task_id != None and task_id !=  "0":
                task = Task.objects.get(id = int(task_id))
                if task.created_by_id == request.user.id:
                    show_private = True
                    show_public=True
                return HttpResponse(render_to_string('task/task.html', {'task' : task,'tz_info':tz_info, 'show_private':show_private,'task_status':task_status,'task_priority':task_priority,'is_remark':True}))
            else:
                return HttpResponse(render_to_string('task/task.html', {'tz_info':tz_info, 'assign_to_id': request.user.id, 'new_task': True, 'show_private':True,'task_status':task_status,'task_priority':task_priority,'is_remark':False}))

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')


def save_task(request):    
    try:
        with transaction.atomic():
            if request.method == 'POST':
                form = None
                action = AuditAction.UPDATE
                task_id = request.POST.get('task_id')
                entity_id = request.POST.get('entity_id')
                related_to = request.POST.get('related_to')
                if related_to == 'undefined':
                    related_to = None
                app_name = request.POST.get('app_name').lower()
                model_name = request.POST.get('model_name').lower()
                print(model_name if model_name != 'crm' else 'deal')
                model_name = model_name if model_name != 'crm' else 'deal'
                app_name = app_name if app_name != '0' and model_name != 'deal' else 'campaign'
                c_ip = base_views.get_client_ip(request)
                user_id = request.user.id
                user = User.objects.get(id = user_id)
                create_scheduler = 0
                is_new = True

                if task_id is None or (Util.is_integer(task_id) and int(task_id) in [0,-1]):
                    # if user.has_perm('task.add_task') == False:
                    #     return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type='json')
                    action = AuditAction.INSERT
                    form = TaskForm(request.POST)
                    is_new = True
                else:
                    # if user.has_perm('task.change_task') == False:
                    #     return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type='json')
                    task = Task.objects.get(id = int(task_id))
                    form = TaskForm(request.POST, instance=task)
                    is_new = False
                reminder_on = request.POST.get('reminder_on', None)

                request.POST._mutable = True

                request.POST['reminder_on_text'] = reminder_on
                if request.POST['due_date'] is not None and request.POST['due_date']!='':
                    request.POST['due_date'] = Util.get_utc_datetime(str(request.POST['due_date']), True)

                if reminder_on and request.POST['reminder_on'] == 'OTHER':
                    if request.POST['due_date_reminder']:
                        create_scheduler = 1
                        request.POST['reminder_on'] = Util.get_utc_datetime(str(request.POST['due_date_reminder']), True)
                    else:
                        request.POST['reminder_on'] = None
                elif reminder_on and request.POST['due_date'] and request.POST['reminder_on']:
                    reminder_on = request.POST.get('reminder_on')
                    minutes = 0
                    if reminder_on == '30_MIN_BFR':
                        minutes = 30
                    elif reminder_on == '1_HR_BFR':
                        minutes = 60
                    elif reminder_on == '3_HR_BFR':
                        minutes = 180
                    elif reminder_on == '6_HR_BFR':
                        minutes = 360
                    elif reminder_on == '24_HR_BFR':
                        minutes = 1440

                    if minutes:
                        create_scheduler = 1
                        request.POST['reminder_on'] = request.POST['due_date'] - datetime.timedelta(minutes=minutes)
                request.POST._mutable = False
                       
                if form.is_valid():
                    task = form.save(commit = False)

                    if action == AuditAction.INSERT:
                        content_type = ContentType.objects.filter(app_label = app_name.lower(), model = model_name.lower()).first()
                        task.created_by_id = request.user.id
                        if entity_id == '0':
                            entity_id = None
                        task.entity_id = entity_id
                        task.content_type = content_type
                        task.related_to = related_to

                    task = form.save()
                    log_views.insert("task", "task", [task.id], action, request.user.id, c_ip, log_views.getLogDesc(task.name, action))
                    is_notification = False
                    email_to = []
     
                    if task.email_notification:
                        is_notification = True
                        if action == AuditAction.INSERT:
                            if task.assign_to and task.created_by_id != task.assign_to_id:
                                email_to = [task.assign_to.email]
                        else:
                            if request.user.id != task.created_by_id:
                                email_to = [task.created_by.email]
                                if task.assign_to and task.created_by.email != task.assign_to.email:
                                    email_to = [task.created_by.email, task.assign_to.email]
                            if task.assign_to and task.created_by_id != task.assign_to_id:
                                if request.user.id == task.created_by_id:
                                    email_to = [task.assign_to.email]
                                if request.user.id == task.assign_to_id:
                                    email_to = [task.created_by.email]
                    
                    task = Task.objects.filter(id = task.id).values('id', 'name', 'description', 'due_date', 'status','related_to','entity_id',
                            'priority', 'assign_to', 'created_by', 'assign_to__first_name', 'assign_to__last_name','content_type',
                            'created_by__first_name', 'created_by__last_name', 'created_on', 'task_type_id','content_type__app_label','content_type__model',
                            'task_type__name', 'task_type__icon','remarks').first()

                    task_obj = get_task_obj(task)

                    if is_new:
                        send_notification(request, task_obj, 'created')

                    if task_obj['status'] == 'Completed':
                        send_notification(request, task_obj, 'completed')

                    # DON'T REMOVE BELOW CODE, IT WILL BE IN FUTURE VERSION.
                    if create_scheduler:
                        schedule = {}
                        title = task_obj['name']
                        url = 'task/task_reminder/?task_id='+str(task_obj['id'])
                        notification_email = ''
                        start_date = request.POST['reminder_on'].date().strftime("%d/%m/%Y")
                        start_time = request.POST['reminder_on'].time().strftime("%H:%M")
                        schedule['start_date'] = start_date
                        schedule['start_time'] = start_time
                        schedule['recur_type'] = 'once'
                        create_task_scheduler(title, url, json.dumps(schedule), notification_email, user_id, c_ip)

                    return HttpResponse(AppResponse.msg(1, 'Task saved.'), content_type='json')
                else:
                    return HttpResponse(AppResponse.msg(0, form.errors), content_type='json')
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception('Something went wrong.')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def send_notification(request, task_obj, notification_type):

    subscribe_notifications(
        request.user.id, 'others', 'task', 'new', task_obj['id'],
        id = task_obj['id'], 
        related_to = task_obj['related_to'],
        task_name = task_obj['name'],
        user_name = task_obj['created_by'],
        due_date = task_obj['due_date'],
        status = task_obj['status'],
        priority = task_obj['priority'],
        assign_to = task_obj['assign_to'],
        description = task_obj['description'],
        subject = task_obj['name']+' '+notification_type)

    user_notification(request,
        request.user.id, 'others', 'task', 'new', task_obj['id'],
        id = task_obj['id'], 
        related_to = task_obj['related_to'],
        task_name = task_obj['name'],
        user_name = task_obj['created_by'],
        due_date = task_obj['due_date'],
        status = task_obj['status'],
        priority = task_obj['priority'],
        assign_to = task_obj['assign_to'],
        description = task_obj['description'],
        subject = task_obj['name']+' '+notification_type)


def task_delete(request):
    try:
        with transaction.atomic():
            task_id = int(request.POST.get('id'))
            c_ip = base_views.get_client_ip(request)
            task = Task.objects.filter(id = int(task_id)).first()
            user = User.objects.get(id = request.user.id)

            # if user.has_perm('task.delete_task') == False:
            #     return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type='json')

            task.delete()
            log_views.insert("task", "task", [task_id], AuditAction.DELETE, request.user.id, c_ip, 'Task deleted.')
            return HttpResponse(AppResponse.msg(1, 'Task deleted.'), content_type='json')
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')


def reminder_for_task():
    with schema_context(settings.PURCHASE_PLAN_SCHEMA):
        try:
            query = Q()
            time_now = datetime.datetime.utcnow().replace(tzinfo=utc)
            
            furure_time_age = datetime.timedelta(minutes = 31)
            future_time = time_now + furure_time_age
            
            past_time_age = datetime.timedelta(minutes = -31)          
            past_time = time_now + past_time_age

            query.add(Q(due_date__range = (past_time, future_time), due_mail_sent_time__isnull = True, email_notification = True), query.connector)
            query.add(~Q(status__in = ['completed', 'cancelled']), query.connector)
            
            tasks = Task.objects.filter(query)
            
            template = EmailTemplate.objects.filter(name__icontains = 'tasks_overdue').values('id')
            
            assign_to_ids = []
            created_by_ids = []

            dbname = settings.DATABASES['default']['NAME']
            user = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            port = settings.DATABASES['default']['PORT']
            db = pg.connect(dbname=dbname,user=user,password=password,host=host,port=port)       
            cursor = db.cursor()
            cursor.execute(''' select domain_url from clients_client where schema_name ='%s' ''' %(settings.PURCHASE_PLAN_SCHEMA))
            domain = cursor.fetchone()[0]
            db.close()

            if 'http://' not in domain or 'https://' not in domain:
                    domain = 'http://'+ domain
            
            url = domain + '/b/#/task/tasks/'

            due_email_data = []

            for task in tasks:
                profile_assign_obj = UserProfile.objects.filter(user_id__in = [task.assign_to_id,task.created_by_id]).values('user_id','notification_email')
                email_of_assign = ''
                email_of_created = ''
                for email in profile_assign_obj:
                    if email['user_id'] == task.assign_to_id:
                        email_of_assign =  email['notification_email']
                    elif email['user_id'] == task.created_by_id:
                        email_of_created = email['notification_email']
                
                has_assign_data = False
                has_created_data = False

                for due_data in due_email_data:
                    if due_data['email'] == email_of_assign :
                        has_assign_data = True
                    
                    if due_data['email'] == email_of_created :
                        has_created_data = True

                if has_assign_data == False and email_of_assign != None:
                    context_task = list(filter(lambda n:(n['assign_to_id'] == task.assign_to_id or n['created_by_id'] == task.assign_to_id), tasks.values('id','name','created_by_id','assign_to_id')))
                    
                    context = {
                       'user' : task.assign_to.first_name,
                       'count' : len(context_task),
                       'task_overdue_url' : url,
                       'tasks' : list(context_task[:10])
                    }
                    
                    due_email_data.append({
                        'email' : email_of_assign,
                        'context': context
                    })
                
                if has_created_data == False and email_of_created != None:
                    context_task = list(filter(lambda n:(n['assign_to_id'] == task.created_by_id or n['created_by_id'] == task.created_by_id), tasks.values('id','name','created_by_id','assign_to_id')))
                    
                    context = {
                       'user' : task.created_by.first_name,
                       'count' : len(context_task),
                       'task_overdue_url' : url,
                       'tasks' : list(context_task[:10])
                    }
                    
                    due_email_data.append({
                        'email' : email_of_created,
                        'context': context
                    })
            
            for email_data in due_email_data:
                send_email_by_tmpl(True, settings.PURCHASE_PLAN_SCHEMA, [email_data['email']], template[0]['id'], email_data['context'])
            
            for task in tasks:
                task.due_mail_sent_time = datetime.datetime.utcnow()
                task.save()
            
        except Exception as e:
            manager.create_from_exception(e)
            return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

@public
@csrf_exempt
def task_reminder(request, scheduler_key):
    try:
        task_id = int(request.GET.get('task_id'))
        if scheduler_key == settings.SCHEDULER_KEY :
            task = Task.objects.filter(id = task_id, has_reminder_sent = False).values('id', 'name', 'due_date', 'reminder_on', 'assign_to_id', 'assign_to__first_name', 'assign_to__last_name','created_by_id', 'created_by__first_name', 'created_by__last_name', 'related_to', 'status', 'priority', 'description').first()
            if task:
                assign_to_contact = UserProfile.objects.filter(user_id = task['assign_to_id']).values('user_id','notification_email', 'notification_mob').first()
                created_by_contact = UserProfile.objects.filter(user_id = task['created_by_id']).values('user_id','notification_email', 'notification_mob').first()
                send_email_to = {}
                send_sms_to = {}
                send_email_to[assign_to_contact['user_id']] = assign_to_contact['notification_email']
                send_email_to[created_by_contact['user_id']] = created_by_contact['notification_email']
                send_sms_to[assign_to_contact['user_id']] = assign_to_contact['notification_mob']
                send_sms_to[created_by_contact['user_id']] = created_by_contact['notification_mob']
                template = EmailTemplate.objects.filter(name = 'task_reminder').first().id
                mail_context= {
                    'task_name': task['name'],
                    'user_name': task['created_by__first_name'] + ' '+ task['created_by__last_name'],
                    'related_to': task['related_to'],
                    'due_date': Util.get_local_time(task['due_date'], True),
                    'status': dict(task_status).get(task['status']),
                    'priority' : dict(task_priority).get(task['priority']),
                    'assign_to': task['assign_to__first_name'] +' '+task['assign_to__last_name'],
                    'description': task['description']
                }
                sms_context = {
                    'task_name': task['name']
                }
                if task['assign_to_id']:
                    send_email_by_tmpl(False, 'public', [send_email_to[task['assign_to_id']]], template, mail_context)
                    Notification.objects.create(subject = task['name'], text = task['name'], user_id = task['assign_to_id'])
                    if send_sms_to[task['assign_to_id']]:
                        send_sms([send_sms_to[task['assign_to_id']]], 'task_reminder', sms_context)
                send_email_by_tmpl(False, 'public', [send_email_to[task['created_by_id']]], template, mail_context)
                Notification.objects.create(subject = task['name'], text = task['name'], user_id = task['created_by_id'])
                if send_sms_to[task['created_by_id']]:
                    send_sms([send_sms_to[task['created_by_id']]], 'task_reminder', sms_context)
                Task.objects.filter(id = task['id']).update(has_reminder_sent = True)
                
                url = 'task/task_reminder/?task_id='+str(task['id'])
                task = TaskScheduler.objects.filter(url = url).first()
                print(task,'task')
                log_views.insert("base", "taskscheduler", [task.id] , AuditAction.DELETE , admin_user['user_id'], c_ip, log_views.getLogDesc(task.title, AuditAction.DELETE))
                task.delete()
        return HttpResponse(AppResponse.msg(1, ''), content_type='json')
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception('Something went wrong')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')