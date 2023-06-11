import base64
import datetime
import json
import logging
import os
import random
import socket
import ssl
import string
import tempfile
import time
import unicodedata
import urllib
import urllib.request
from io import BytesIO, StringIO
from itertools import chain
from os.path import abspath, dirname
from random import randint
from shutil import copy
from socket import timeout
from urllib.request import HTTPError, URLError
from uuid import uuid4

import base.views as base_views
import requests
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import choices
from base.models import AppResponse, AuthToken, DocNumber, SysParameter
from base.util import Util
from base.views import vertical_menu_context
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.db import connection, transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from exception_log import manager
from mails.views import send_email_by_tmpl, send_sms
from messaging.models import NotificationEvent, SubscribeNotification
from PIL import Image
from post_office.models import EmailTemplate
from sparrow.decorators import check_view_permission
from stronghold.decorators import public

from accounts.forms import ProfileForm
from accounts.models import Company, ContentPermission, Group, GroupPermission, MainMenu, PagePermission, Permission, User, UserGroup, UserProfile
from accounts.services import CompanyService, UserService

from . import profile_image_generator
from .forms import GroupForm, UserForm

imguuid = str(uuid4())


@public
def signin(request):
    bg_images = UserService.get_background_images_list()
    image_name = random.choice(bg_images)
    black_wall = False if "w" in image_name else True
    if Util.get_sys_paramter("AWS_S3_HANDLER").para_value:
        bg_image_url = Util.get_sys_paramter("AWS_S3_HANDLER").para_value + str(image_name)
    if Util.get_sys_paramter("COMPANY_LOGO").para_value:
        company_logo = Util.get_sys_paramter("COMPANY_LOGO").para_value
    return render(request, "accounts/signin.html", {"bg_image_url": bg_image_url, "black_wall": black_wall, "company_logo": company_logo})


@public
@csrf_exempt
def authcheck(request):
    try:
        if request.method == "POST":
            username = request.POST["data[1][value]"].lower()
            password = request.POST["data[2][value]"]
            device_id = request.POST["data[3][value]"]
            redirect_url = request.POST["url_data"]
            email_id = ""

            default_role_id = Util.get_sys_paramter("Default_role_id").para_value
            role_id = Group.objects.filter(id=default_role_id).first().id
            # api call using above username & password
            url = settings.EC_DOMAIN + "shop/salesappapi/salesapp/userauth"
            payload = '{\r\n   "Username": "' + username + '",\r\n   "Password":"' + password + '",\r\n   "DeviceId":"' + device_id + '"\r\n}'

            headers = {"Content-Type": "application/json"}

            response = requests.request("GET", url, headers=headers, data=payload, timeout=5)
            api_result = json.loads(response.text)
            # breakpoint()
            if api_result["result"] == "0":
                return HttpResponse(AppResponse.msg(0, "Failed to authenticate"), content_type="json")
            ec_user_id = api_result["userid"]  # it ECC user
            two_fact_auth = api_result["tfaRequired"]
            user_name = api_result["username"].lower()
            user = User.objects.filter(username__iexact=user_name).first()
            profile = None
            if user is None:
                user = User(username=user_name, first_name=api_result["firstName"], last_name=api_result["lastName"], email=api_result["username"])
                user.save()
                profile = UserProfile(user_id=user.id, ec_user_id=ec_user_id)
                profile.save()
                UserGroup.objects.create(user_id=user.id, group_id=role_id)
            else:
                user.first_name = api_result["firstName"]
                user.last_name = api_result["lastName"]
                user.save()
            profile = UserProfile.objects.filter(user_id=user.id).first()
            profile.ec_user_id = ec_user_id
            profile.save()
            if profile.is_deleted == True:
                return HttpResponse(AppResponse.msg(0, "Failed to authenticate"), content_type="json")
            if profile.ip_restriction:
                my_ip_address = Util.get_public_ip_address()
                allowed_ips = settings.ALLOWED_PUBLIC_IPS if hasattr(settings, "ALLOWED_PUBLIC_IPS") else []
                if my_ip_address not in allowed_ips and my_ip_address.rsplit(".", 1)[0] not in allowed_ips:
                    return HttpResponse(AppResponse.msg(0, "You are not authorized to sign in from this location."), content_type="json")

            if two_fact_auth == True:
                email_id = api_result["emailId"]
                device_id = api_result["deviceId"]
            else:
                session_save(request, api_result, user, profile)

            if profile.user_type == 2 or profile.user_type == 3:
                return HttpResponse(AppResponse.msg(1, "/"), content_type="json")
            else:
                url_page = ""
                if redirect_url != "":
                    url_page = "/b/" + redirect_url
                else:
                    url_page = "/b/#/"
                return HttpResponse(
                    json.dumps({"code": 1, "url_page": url_page, "two_fact_auth": two_fact_auth, "device_id": device_id, "relationId": ec_user_id, "email_id": email_id}),
                    content_type="json",
                )
        else:
            return HttpResponse(AppResponse.msg(0, "Failed to authenticate"), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def signout(request):
    username = request.user.username if request.user.username is not None else ""
    token = request.session['AuthToken'] if 'AuthToken' in request.session else ""
    app = 'EC_SALESAPP'
    session_id = request.session.session_key if request.session.session_key is not None else ""
    url = settings.EC_PORTAL_DOMAIN + "clear_app_sessions/"
    try:
        requests.request("POST", url, data={"token": token, "username": username, "app": app, "session_id":session_id}, timeout=5)
    except:
        pass
    logout(request)
    response = HttpResponseRedirect("/accounts/signin/")
    return response


def profile(request):
    if "username" not in request.session:
        return redirect("/accounts/signin/")
    else:
        user = User.objects.get(username=request.session.get("username").strip())
        profile = UserProfile.objects.get(user=user)

        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "display_row": profile.display_row,
            "default_page": profile.default_page if profile.default_page else "",
            "menu_launcher": profile.menu_launcher,
        }
        color_scheme = profile.color_scheme if profile.color_scheme != None else ""

        color_scheme_data = {}
        if color_scheme != "":
            color_scheme = unicodedata.normalize("NFKD", color_scheme)
            # color_scheme_data = {}
            for param in color_scheme.split(","):
                scheme_data = param.split(":")
                if scheme_data != "":
                    color_scheme_data[scheme_data[0].strip()] = scheme_data[1].strip()
        bg_color = color_scheme_data["bg_color"] if color_scheme != "" else "#2A3F54"
        button_color = color_scheme_data["button_color"] if color_scheme != "" else "#337ab7"
        link_color = color_scheme_data["link_color"] if color_scheme != "" else "#266EBB"
        row_color = color_scheme_data["row_color"] if "row_color" in color_scheme_data else "#FFFFCC"

        notification_events = NotificationEvent.objects.filter(is_active=True).values("id", "group", "name").order_by("group")
        subscribe_notifications = (
            SubscribeNotification.objects.filter(user_id=user.id, entity_id__isnull=True).values("event__id", "by_email", "in_system", "by_sms").order_by("event__group")
        )

        sub_group_data = []
        notifications_by_group = []
        event_group_name = ""

        for notification_event in notification_events:
            if event_group_name != notification_event["group"]:
                notifications_by_group = []
                event_group_name = notification_event["group"]
                sub_group_data.append(
                    {"group_name": dict(choices.event_group)[notification_event["group"]], "group": notification_event["group"], "notifications": notifications_by_group}
                )

            sub_notifications = [subscribe_not for subscribe_not in subscribe_notifications if subscribe_not["event__id"] == notification_event["id"]]

            notifications_by_group.append(
                {
                    "event_name": notification_event["name"],
                    "event_code": notification_event["name"].replace(" ", "_").lower(),
                    "by_email": False if len(sub_notifications) == 0 else sub_notifications[0]["by_email"],
                    "in_system": False if len(sub_notifications) == 0 else sub_notifications[0]["in_system"],
                    "by_sms": False if len(sub_notifications) == 0 else sub_notifications[0]["by_sms"],
                }
            )

        form = ProfileForm(data, request.POST, request.FILES)
        context = {}
        img_src = Util.get_resource_url("profile", str(profile.profile_image)) if profile.profile_image else ""
        context["form"] = form
        context["profile_image"] = img_src
        context["image_name"] = profile.image_name if profile.image_name != None else ""
        context["image_url"] = Util.get_sys_paramter("AWS_S3_HANDLER").para_value + str(profile.image_name) if profile.image_name is not None else ""
        context["notification_email"] = profile.notification_email if profile.notification_email != None else None
        context["notification_mob"] = profile.notification_mob if profile.notification_mob != None else None
        context["bg_color"] = bg_color
        context["button_color"] = button_color
        context["link_color"] = link_color
        context["row_color"] = row_color
        context["columns"] = ["first_name", "last_name"]
        context["sub_group_data"] = sub_group_data
        context["first_name"] = user.first_name
        context["last_name"] = user.last_name
        context["email"] = user.email
        context["default_page"] = profile.default_page if profile.default_page else ""
        context["display_row"] = profile.display_row
        context["menu_launcher"] = profile.menu_launcher
        context["ftr_sms_service"] = True if Util.get_sys_paramter("ftr_sms_service") != None and Util.get_sys_paramter("ftr_sms_service").para_value.lower() == "true" else False

        return render(request, "accounts/profile.html", context)


def save_profile(request):
    try:
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES)
            session = SessionStore(session_key=request.session.session_key)
            if form.is_valid():
                notification_events = NotificationEvent.objects.filter(is_active=True)
                user = User.objects.get(username=session.get("username").strip())
                user.first_name = str(request.POST["first_name"]).strip()
                user.last_name = str(request.POST["last_name"]).strip()
                display_row = int(request.POST["display_row"])
                is_file = request.FILES.get("profile_image", False)
                bg_color = str(request.POST["background-theme-color"]).strip()
                button_color = str(request.POST["button-color"]).strip()
                link_color = str(request.POST["link-color"]).strip()
                row_color = str(request.POST["row-color"]).strip()
                bg_image = request.POST.get("bgImage")
                user_full_name = user.first_name + " " + user.last_name
                new_image = ""
                default_page = str(request.POST["default_page"])
                menu_launcher = form.cleaned_data["menu_launcher"]

                for event in notification_events:
                    event_code = event.name.replace(" ", "_").lower()
                    by_email = True if "by_email_" + event.group + "_" + event_code in request.POST else False
                    by_sms = True if "by_sms_" + event.group + "_" + event_code in request.POST else False
                    in_system = True if "in_system_" + event.group + "_" + event_code in request.POST else False
                    subscribe_notifications = SubscribeNotification.objects.filter(user_id=user.id, event_id=event.id, entity_id__isnull=True).first()
                    if subscribe_notifications == None:
                        subscribe_notifications = SubscribeNotification.objects.create(user_id=user.id, event_id=event.id, created_by_id=user.id)
                    subscribe_notifications.by_email = by_email
                    subscribe_notifications.by_sms = by_sms
                    subscribe_notifications.in_system = in_system
                    subscribe_notifications.save()

                if default_page != "":
                    default_page_list = default_page.split("/")
                    for word in default_page_list:
                        if word == "#":
                            del default_page_list[0 : default_page_list.index(word) + 1]
                    default_page = "/".join(default_page_list)
                color_scheme = "bg_color:" + bg_color + ",button_color:" + button_color + ",link_color:" + link_color + ",row_color:" + row_color + ""
                profile = UserProfile.objects.get(user=user)

                if is_file:
                    profile = UserProfile.objects.get(user=user)
                    profile.profile_image = request.FILES["profile_image"]
                    profile.save()
                    session["profile_image"] = str(profile.profile_image)

                if color_scheme != "":
                    profile = UserProfile.objects.get(user=user)
                    profile.color_scheme = color_scheme
                    profile.save()
                    session["color_scheme"] = color_scheme
                if bg_image != None:
                    profile = UserProfile.objects.get(user=user)
                    profile.image_name = bg_image
                    profile.save()
                    session["bg_image"] = bg_image
                if display_row != None:
                    profile = UserProfile.objects.get(user=user)
                    profile.display_row = display_row
                    profile.save()
                    session["display_row"] = display_row

                if user_full_name != None:
                    profile.user_full_name = user_full_name
                    session["display_name"] = user_full_name
                if profile.notification_email != None:
                    session["notification_email"] = profile.notification_email

                profile.default_page = default_page
                profile.menu_launcher = menu_launcher
                profile.save()
                session["profile_image"] = str(profile.profile_image)
                session["default_page"] = default_page
                session.save()
                user.save()
                if new_image != "":
                    return HttpResponse(json.dumps({"code": 1, "msg": "Profile Updated.", "avatar": new_image}), content_type="json")
                return HttpResponse(AppResponse.msg(1, "Profile Updated."), content_type="json")
            else:
                return HttpResponse(AppResponse.msg(0, str(form.errors)), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_password(request):
    try:
        user_id = request.POST.get("id") if request.POST.get("id") else request.user.id
        password = request.POST["password"]
        user = User.objects.get(id=user_id)
        user.password = make_password(str(request.POST["password"]).strip())
        user.save()
        is_reload = True if user.id == request.user.id else False
        return HttpResponse(json.dumps({"code": 1, "msg": "Password updated.", "is_reload": is_reload}), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_background_images(request):
    try:
        response = []
        bg_images = UserService.get_background_images_list()
        for image in bg_images:
            response.append({"name": image, "src": Util.get_sys_paramter("AWS_S3_HANDLER").para_value + str(image)})
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @check_view_permission({'admin_tools':'roles'})
def roles(request):
    return render(request, "accounts/roles.html")


def roles_search(request, q=None):
    request.POST = Util.get_post_data(request)
    start = int(request.POST["start"])
    length = int(request.POST["length"])
    sort_col = Util.get_sort_column(request.POST)

    query = Q()

    if request.POST.get("name__icontains") != None:
        query.add(Q(name__icontains=str(request.POST.get("name__icontains"))), query.connector)

    recordsTotal = Group.objects.filter(query).count()
    user_roles = Group.objects.filter(query).order_by(sort_col)[start : (start + length)]

    response = {
        "draw": request.POST["draw"],
        "recordsTotal": recordsTotal,
        "recordsFiltered": recordsTotal,
        "data": [],
    }

    for user_role in user_roles:
        response["data"].append({"id": user_role.id, "name": user_role.name})

    return HttpResponse(AppResponse.get(response), content_type="json")


def role(request, role_id=None):
    try:
        with transaction.atomic():
            if request.method == "POST":
                id = request.POST.get("id")
                name = request.POST["name"].strip()
                action = AuditAction.UPDATE
                user_id = request.user.id
                user = User.objects.get(id=user_id)
                c_ip = base_views.get_client_ip(request)

                if id == None or id == "0":
                    if name != "" and Group.objects.filter(name__iexact=name).count() > 0:
                        return HttpResponse(AppResponse.get({"code": 0, "msg": "User role name already exist."}), content_type="json")
                    action = AuditAction.INSERT
                    if Util.has_perm("can_add_roles", user) == False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    form = GroupForm(request.POST)
                else:
                    if Util.has_perm("can_update_roles", user) == False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    group = Group.objects.get(id=int(id))
                    if name != "" and name.lower() != group.name.lower() and Group.objects.filter(name__iexact=name).count() > 0:
                        return HttpResponse(AppResponse.get({"code": 0, "msg": "User role name already exist."}), content_type="json")
                    form = GroupForm(request.POST, instance=group)

                if form.is_valid() == False:
                    return HttpResponse(AppResponse.msg(0, "Invalid form"), content_type="json")

                group = form.save()
                group_id = group.id
                permission_ids = str(request.POST["role_assi_perm"]).strip()
                new_permissions = []
                if permission_ids != "":
                    new_permissions = [int(x) for x in permission_ids.split(",")]
                    role_permissions = GroupPermission.objects.filter(group_id=group_id, page_permission_id__isnull=False).values_list("page_permission_id", flat=True).distinct()
                    for perm in new_permissions:
                        if perm not in role_permissions:
                            GroupPermission.objects.create(group_id=group_id, page_permission_id=perm, created_by_id=request.user.id)
                    perms_to_del = []
                    for perm in role_permissions:
                        if perm not in new_permissions:
                            perms_to_del.append(perm)
                    if len(perms_to_del) > 0:
                        GroupPermission.objects.filter(page_permission_id__in=perms_to_del, group_id=group_id).delete()
                else:
                    GroupPermission.objects.filter(group_id=group_id, page_permission_id__isnull=False).delete()

                Util.clear_cache("public", "ROLES" + str(group_id))

                log_views.insert("auth", "group", [group_id], action, user_id, c_ip, log_views.getLogDesc("Role", action))

                return HttpResponse(AppResponse.get({"code": 1, "msg": "Data saved", "id": group_id}), content_type="json")

            list_data = []
            perms = []

            content_permissions = ContentPermission.objects.all().order_by("sequence")
            for content_permission in content_permissions:
                index = next((index for index, item in enumerate(list_data) if item["content_group"] == content_permission.content_group), None)
                if index == None:
                    content_name = add_perm_list(content_permission.content_group, [])
                    list_data.append({"content_group": content_permission.content_group, "content_name": content_name})

            avail_perms = PagePermission.objects.filter(content__isnull=False).values("menu_id", "act_name", "act_code", "id", "content_id")
            if role_id != "0" and role_id != None:
                group = Group.objects.filter(id=role_id).first()
                for lists in list_data:
                    for permission in lists["content_name"]:
                        applied_perms = GroupPermission.objects.filter(page_permission__content__id=permission["id"], group_id=role_id).values_list("page_permission_id", flat=True)
                        perms = list(chain(perms, applied_perms))
                return render(request, "accounts/role.html", {"permissions": avail_perms, "applied_perms": perms, "lists": list_data, "group": group})
            else:
                return render(request, "accounts/role.html", {"group": None, "permissions": avail_perms, "applied_perms": perms, "lists": list_data})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def add_perm_list(content_group, list_data):
    content_groups = ContentPermission.objects.filter(content_group=content_group).order_by("sequence")
    for content_group in content_groups:
        list_data.append({"id": content_group.id, "content_name": content_group.content_name})
    return list_data


def role_del(request):
    try:
        role_ids = request.POST.get("ids")
        if not role_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_delete_roles", user) == False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        ids = [int(x) for x in role_ids.split(",")]
        assigned_roles = ""

        roles = UserGroup.objects.filter(group_id__in=ids).values("group_id").distinct()

        for role in roles:
            assigned_obj = Group.objects.filter(id=role["group_id"]).first()
            assigned_roles = assigned_roles + assigned_obj.name + ", "

        if assigned_roles != "":
            return HttpResponse(AppResponse.msg(0, 'Role "' + assigned_roles[:-2] + '" is assigned to some users. Action cannot be performed. '), content_type="json")
        GroupPermission.objects.filter(group_id__in=ids).delete()
        Group.objects.filter(id__in=ids).delete()
        return HttpResponse(AppResponse.msg(1, "Record deleted."), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_notification_token(request):
    try:
        with transaction.atomic():
            if request.method == "POST":
                is_email = True if request.POST.get("is_email") == "true" else False
                is_mobile_no = True if request.POST.get("is_mobile_no") == "true" else False
                email = request.POST.get("email")
                mobile_no = request.POST.get("mobile_no")
                user_id = request.user.id
                user = User.objects.get(id=user_id)
                token = str(randint(1000, 9999))
                expire_on = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
                AuthToken.objects.create(user_id=user_id, token=token, expire_on=expire_on)
                context = {"user_name": user.first_name, "token": token}
                if is_email:
                    template = EmailTemplate.objects.filter(name__iexact="email_verification").values("id").first()
                    send_email_by_tmpl(False, "public", [email], template["id"], context)

                if is_mobile_no:
                    send_sms([mobile_no], "mobile_verification", context)

                return HttpResponse(json.dumps({"code": 1, "msg": ""}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def notification_authentication(request):
    try:
        with transaction.atomic():
            user_id = request.user.id
            token = request.POST.get("otp")
            is_email = True if request.POST.get("is_email") == "true" else False
            is_mobile_no = True if request.POST.get("is_mobile_no") == "true" else False
            email = request.POST.get("email")
            mobile_no = request.POST.get("mobile_no")
            auth_token = AuthToken.objects.filter(token=token, user_id=user_id, is_used=False).first()
            if auth_token:
                expire_on = auth_token.expire_on.replace(tzinfo=None)
                current_time = datetime.datetime.utcnow()
                if expire_on >= current_time:
                    auth_token.is_used = True
                    auth_token.save()
                    if is_email:
                        UserProfile.objects.filter(user_id=user_id).update(notification_email=email)
                    if is_mobile_no:
                        UserProfile.objects.filter(user_id=user_id).update(notification_mob=mobile_no)
                    return HttpResponse(json.dumps({"code": 1, "msg": "Data saved."}), content_type="json")
                else:
                    return HttpResponse(json.dumps({"code": 0, "msg": "Failed to authenticate."}), content_type="json")
            return HttpResponse(json.dumps({"code": 0, "msg": "Failed to authenticate."}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def notification_delete(request):
    try:
        c_ip = base_views.get_client_ip(request)
        user_id = request.user.id
        notification = request.POST["notification"]
        email = ""
        mobile_no = ""

        if notification == "mail":
            UserProfile.objects.filter(user_id=user_id).update(notification_email=email)

        if notification == "mobile":
            UserProfile.objects.filter(user_id=user_id).update(notification_mob=mobile_no)
        return HttpResponse(json.dumps({"code": 1, "msg": "Record deleted."}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def company(request):
    try:
        if request.method == "POST":
            time_zone_now = request.POST.get("time_zone_now")
            name = request.POST["name"].strip()
            email = request.POST["email"].strip()
            website = request.POST["website"].strip()
            phone = request.POST["phone"].strip()
            mobile = request.POST["mobile"].strip()
            is_file = request.FILES.get("company_img", False)
            time_zone = request.POST.get("time_zone")

            if Util.has_perm("can_update_company", request.user) == False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")

            company = CompanyService.get_root_compnay_object()
            new_image = ""
            if is_file:
                path = default_storage.save(imguuid + ".png", ContentFile(request.FILES["company_img"].read()))
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                with open(tmp_file, "rb") as image_file:
                    image = Image.open(image_file)
                    size = (256, 256)
                    image.thumbnail(size, Image.ANTIALIAS)
                    background = Image.new("RGBA", size, (255, 255, 255, 0))
                    box_width = int((size[0] - image.size[0]) / 2)
                    box_height = int((size[1] - image.size[1]) / 2)
                    box = (box_width, box_height)
                    background.paste(image, box)
                    buffer = BytesIO()
                    image.save(buffer, format="png")
                    encoded_string = base64.b64encode(buffer.getvalue())
                    image_input = encoded_string.decode("utf-8")
                os.remove(tmp_file)
                if encoded_string != "":
                    company.company_img = new_image = image_input

            company.name = name
            company.email = email
            company.website = website
            company.phone = phone
            company.mobile = mobile
            company.timezone_offset = time_zone
            company.timezone = time_zone_now
            company.save()

            if new_image != "":
                return HttpResponse(json.dumps({"code": 1, "msg": "Company Updated.", "company_img": image_input}), content_type="json")
            return HttpResponse(AppResponse.msg(1, "Company Updated."), content_type="json")
        else:
            company = CompanyService.get_root_compnay()
            return render(request, "accounts/company.html", {"company": company})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_user_role(request):
    try:
        user_id = request.POST["user_id"]
        role_id = request.POST["role_id"]
        user_grp = UserGroup.objects.filter(user_id=user_id).first()
        if role_id is not None:
            user_grp.group_id = int(role_id)
            user_grp.save()
        return HttpResponse(AppResponse.msg(1, "saved."), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def tfa_page(request):
    try:
        context_data = json.loads(request.POST["auth_data"])
        device_id = request.POST["device_id"]
        context_data.update({"device_key": device_id})
        return render(request, "accounts/two_fact_auth_page.html", context_data)
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, e.message), content_type="json")


@public
def two_fact_auth(request):
    try:
        url = settings.EC_DOMAIN + "shop/salesappapi/salesapp/verify2FactorAuth"
        payload = (
            '{\r\n   "UserId": "' + request.POST["relationId"] + '",\r\n   "OTP":"' + request.POST["user_otp"] + '",\r\n   "DeviceId":"' + request.POST["device_id"] + '"\r\n}'
        )
        headers = {"Content-Type": "application/json"}
        response = requests.request("GET", url, headers=headers, data=payload, timeout=5)
        api_result = json.loads(response.text)
        otp_result = api_result["result"]
        if otp_result == "1":
            user_name = api_result["username"].lower()
            user = User.objects.filter(username__iexact=user_name).first()
            profile = UserProfile.objects.filter(user_id=user.id).first()
            session_save(request, api_result, user, profile)

        response = HttpResponse(AppResponse.msg(1, otp_result), content_type="json")
        return response
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def session_save(request, api_result, user, profile):
    login(request, user)
    permissions = True
    Util.set_cache("public", "user_permissions_" + str(user.id), permissions)
    decimal_parameter = None
    currency_parameter = None
    decimal_place = 4
    base_currency = ""
    if decimal_parameter != None:
        decimal_place = int(decimal_parameter.para_value) if decimal_parameter.para_value != None else 4
    if currency_parameter != None:
        base_currency = currency_parameter.symbol
    session = request.session
    session["user_permissions_" + str(user.id)] = permissions
    session["username"] = api_result["username"].lower()
    session["user_id"] = user.id
    session["ec_user_id"] = api_result["userid"] if "userid" in api_result else 0
    session["display_name"] = user.first_name + " " + user.last_name
    session["decimal_point"] = decimal_place
    session["base_currency"] = base_currency
    session["profile_image"] = str(profile.profile_image) if profile.profile_image else ""
    session["color_scheme"] = profile.color_scheme
    session["bg_image"] = profile.image_name
    session["list_display_row"] = profile.display_row
    session["two_fact_auth"] = api_result["tfaRequired"]
    if profile.user_type == 2 or profile.user_type == 3:
        session["is_external"] = True
    else:
        session["is_external"] = False
    session.save()
