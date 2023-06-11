import json
import logging

import base.views as base_views
from auditlog import views as log_views
from auditlog.models import AuditAction, Auditlog
from base.models import AppResponse
from base.util import Util
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core import serializers
from django.db import transaction
from django.db.models import CharField, Q
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, response
from django.shortcuts import redirect, render
from exception_log import manager
from sparrow.decorators import check_view_permission

from accounts.forms import CreateUserForm
from accounts.models import (Group, GroupPermission, MainMenu, Permission,
                             User, UserGroup, UserProfile)

from . import profile_image_generator


@check_view_permission([{'admin_tools':'accounts_users'},{'admin_tools': 'customer_users'},{'admin_tools':'supplier_users'}])
def users(request):
    defaultRole = UserGroup.objects.filter(user_id=request.user.id).first()
    return render(request, 'accounts/users.html', {"defaultRole": defaultRole.group.id})


def users_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST['start'])
        length = int(request.POST['length'])
        sort_col = Util.get_sort_column(request.POST)
        recordsTotal = 0
        query = Q()

        if request.POST.get('first_name__icontains') != None:
            query.add(Q(first_name__icontains=str(request.POST.get('first_name__icontains').strip())),query.connector)

        if request.POST.get('last_name__icontains') != None:
            query.add(Q(last_name__icontains=str(request.POST.get('last_name__icontains').strip())),query.connector)

        if request.POST.get('email__icontains') != None:
            query.add(Q(email__icontains=str(request.POST.get('email__icontains').strip())),query.connector)

        if request.POST.get('role__icontains') != None:
            #TODO:
            #Issue: All the user ids taken from UserGroup
            #Fix: User inner join with user and take data. This inner joing would be dynamic becasue this condition is only checked when user search role.
            user_ids = UserGroup.objects.filter(group__name__icontains = str(request.POST.get('role__icontains').strip())).values_list('user_id', flat=True).distinct()
            query.add(Q(id__in=user_ids),query.connector)

        # TODO:
        # Issue: All userprofile data is selected and then user id used as in inside user table.
        # Fix: Use inner join on user and userprofile table and exclude is_delete data
        user_profiles = UserProfile.objects.filter(is_deleted = False)
        recordsTotal = User.objects.filter(query).filter(id__in=user_profiles.values_list('user_id',flat=True).distinct()).count()
        users = User.objects.filter(query).filter(id__in=user_profiles.values_list('user_id',flat=True).distinct()).order_by(sort_col)[start: (start+length)]

        response = {
            'draw': request.POST['draw'],
            'recordsTotal': recordsTotal,
            'recordsFiltered': recordsTotal,
            'data': [],
        }

        for user in users:
            #TODO:
            #Issue: Query is executed on UserGroup table insider for loop.
            #Fix: Get all user role outside for loop using single query. Make dict where user id will be key and value would be comma seperated role name.
            user_role_obj = UserGroup.objects.filter(user_id = user.id).values_list('group__name', flat=True).distinct()

            response['data'].append({
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'is_active': "Yes" if user.is_active else "No",
                        'user_role_obj': ','.join(str(x) for x in user_role_obj)
                    });
        return HttpResponse(AppResponse.get(response), content_type='json')
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception('Something went wrong.')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

def user(request, users_id = None):
    try:
        with transaction.atomic():
            if request.method == 'POST':
                id = request.POST.get('id')
                c_ip = base_views.get_client_ip(request)
                form = CreateUserForm(request.POST)
                action = AuditAction.UPDATE
                user_id = request.user.id
                user = User.objects.get(id = user_id)
                if form.is_valid():
                    first_name = str(request.POST['first_name']).strip()
                    last_name = str(request.POST['last_name']).strip()
                    email = str(request.POST['email']).strip()
                    active = str(request.POST.get('active')).strip()
                    ip_restriction = 'ip_restriction' in request.POST
                    user_role_ids = request.POST.get('user_role_ids', False)
                    role_ids = []
                    if user_role_ids:
                        role_ids = [int(x) for x in user_role_ids.split(',')]

                    if id == None or id == "0":
                        if Util.has_perm("can_add_accounts_users",user) == False:
                            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type='json')
                        if User.objects.filter(email__iexact = email).count() > 0:
                            return HttpResponse(AppResponse.get({'code' : 0, 'msg': 'Email already exist.'}), content_type='json')

                        action = AuditAction.INSERT
                        user = User(first_name= first_name, last_name= last_name, email = email,  username = email)
                        user.save()

                        profile = UserProfile(user=user, color_scheme = settings.DEFAULT_COLOR_SCHEME, ip_restriction = ip_restriction)
                        profile.save()
                        profile_image = profile_image_generator.GenerateCharacters(first_name[0].upper()+''+last_name[0].upper(), profile.id)
                        profile.profile_image = profile_image
                        profile.save()

                        for role_id in role_ids:
                            UserGroup.objects.create(user_id = user.id, group_id = role_id)

                        is_reload = True
                    else:
                        if Util.has_perm("can_update_accounts_users",user) == False:
                            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type='json')

                        user = User.objects.get(id = int(id))
                        if User.objects.filter(username__iexact = email, is_active = True).exclude(username__iexact = user.email, is_active = True).count() > 0:
                            return HttpResponse(AppResponse.get({'code' : 0, 'msg': 'Email already exist.'}), content_type='json')

                        user.first_name = first_name
                        user.last_name = last_name
                        user.email = email
                        user.username = email
                        is_reload = False
                        if active == "on":
                            user.is_active = True
                        else:
                            user.is_active = False
                            session_key = UserProfile.objects.filter(user_id = user.id).values('session_key').first()
                            Session.objects.filter(session_key=session_key['session_key']).delete()

                        user.save()
                        profile = UserProfile.objects.filter(user_id = user.id).first()
                        profile.ip_restriction = ip_restriction
                        if profile == None:
                            profile = UserProfile(user=user, color_scheme=settings.DEFAULT_COLOR_SCHEME, avatar='', ip_restriction= ip_restriction)
                        profile.save()

                        exist_role_ids = UserGroup.objects.filter(user_id = user.id).values_list('group_id', flat=True).distinct()
                        for role_id in role_ids:
                            if role_id not in exist_role_ids:
                                UserGroup.objects.create(user_id = user.id, group_id = role_id)

                        delete_role_ids = [x for x in exist_role_ids if x not in role_ids]
                        UserGroup.objects.filter(user_id = user.id, group_id__in = delete_role_ids).delete()
                        if len(delete_role_ids) > 0:
                            UserGroup.objects.filter(user_id = user.id, group_id__in = delete_role_ids).delete()
                        is_reload = True if user.id == request.user.id and user.username != request.session['username'] else False
                        if is_reload:
                            del request.session['username']

                    log_views.insert("accounts", "userprofile", [user.id], action, user_id, c_ip, log_views.getLogDesc("User", action))

                    return HttpResponse(json.dumps({'code': 1, 'msg': 'Data saved', 'id': user.id, 'is_reload': is_reload}), content_type='json')
                else:
                    return HttpResponse(AppResponse.msg(0, "Please enter valid email format."), content_type='json')

            else:
                if users_id != None and users_id !=  "0":
                    user_profile =  UserProfile.objects.filter(user_id = users_id).first()
                    user = User.objects.get(id = users_id)
                    ip_restriction = user_profile.ip_restriction

                    user_role_obj = UserGroup.objects.filter(user_id = users_id).values_list('group_id', flat=True).distinct()

                    return render(request, 'accounts/user.html', {
                        'first_name':user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'active': user.is_active,
                        'ip_restriction': ip_restriction,
                        'user_role_obj': ','.join(str(x) for x in user_role_obj)
                    })
                else:
                    fields = ['email','password','confirm_password']
                    users_form = CreateUserForm()

                    return render(request, 'accounts/user.html', {'form': users_form,'fields' : fields, 'ip_restriction': False, 'user_role_obj': None})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception('Something went wrong.')
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')


def users_del(request, usersid=None):
    try:
        with transaction.atomic():
            post_ids = request.POST.get('ids') if request.POST.get('ids') else request.POST.get('id')
            user_id = request.user.id
            user = User.objects.get(id = user_id)
            query = Q()
            users_name = ''
            is_history = False

            if Util.has_perm("can_delete_accounts_users",user) == False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type='json')

            if not post_ids:
                return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type='json')

            ids = [int(x) for x in post_ids.split(",")]

            for data_id in ids:
                user_history = Auditlog.objects.filter(action_by_id = data_id).first()
                if user_history:
                    user_data = User.objects.get(id = data_id)
                    users_name = users_name  + user_data.first_name + ','
                    is_history = True

            if is_history:
                error_msg = "User has transaction(s) " + users_name[:-1] + '.'
                return HttpResponse(AppResponse.msg(0, error_msg), content_type='json')

            else:
                UserProfile.objects.filter(user_id__in = ids).delete()
                Labour.objects.filter(user_id__in = ids).delete()
                UserGroup.objects.filter(user_id__in = ids).delete()
                User.objects.filter(id__in = ids).delete()

            return HttpResponse(AppResponse.msg(1, "Data removed"), content_type='json')
    except ProtectedError:
        return HttpResponse(AppResponse.msg(0,'User has transaction(s)'),content_type="json")
    except Exception as e:
        logging.exception('Something went wrong')
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')
