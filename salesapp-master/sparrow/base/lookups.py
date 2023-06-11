from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from accounts.models import User
from django.core import serializers
from base.util import Util
from base.models import AppResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from base.util import Util
from django.core.cache import cache
import json
from django.conf import settings
import ast
from accounts.models import UserProfile 
from stronghold.decorators import public
from sparrow.dbengine import DBEngine
from sqlalchemy.sql import text
from django.db import connection

@public
@csrf_exempt
def lookups(request, model):
    q = request.POST.get('query')
    bid = request.POST.get('bid') #base id passed when dropdown is dependent on base field
    selectedId = request.POST.get('id',False)
    selectedIds = []
    if selectedId and selectedId.find(","):
        selectedIds = [int(x) for x in selectedId.split(",")]

    if model == "users":
        from django.contrib.auth.models import User
        response = []
        query = Q()
        query.add(Q(user__is_active = True, is_deleted=False, user_type = 1), query.connector)
        query.add(Q(user__first_name__icontains = q) | Q(user__last_name__icontains = q), query.connector)
        
        if selectedId and selectedId !='':
            selected_record = UserProfile.objects.filter(user_id =selectedId).values('user__first_name','user__last_name', 'user_id').first()
            response.append({'name': selected_record['user__first_name'] + ' ' + selected_record['user__last_name'], 'id' : selected_record['user_id']})
        user_profiles = UserProfile.objects.filter(query).values('user__first_name','user__last_name', 'user_id').order_by('user__first_name')[:10]
        
        for user_profile in user_profiles:
            response.append({'name': user_profile['user__first_name']+ ' ' + user_profile['user__last_name'], 'id' : user_profile['user_id']})
        return HttpResponse(AppResponse.get(response), content_type='json')
    
    if model == "group":
        from accounts.models import Group
        user_roles = Group.objects.filter().order_by('name')[:10]
        response = []
        for user_role in user_roles:
            response.append({'name': user_role.name, 'id' : user_role.id})
        if selectedIds:
            selected_records = Group.objects.filter(id__in = selectedIds)
            for selected_record in selected_records:
                response.append({'name': selected_record.name, 'id' : selected_record.id})
        return HttpResponse(AppResponse.get(response), content_type='json')