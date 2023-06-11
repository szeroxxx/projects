import datetime
import json
import logging
import os
import ssl
import unicodedata
import urllib
import urllib.request
import base.views as base_views
from datetime import datetime
from itertools import chain
from django.contrib.sessions.models import Session
# from os.path import abspath, dirname
from random import randint
from shutil import copy
from uuid import uuid4
from accounts.forms import ProfileForm
from accounts.models import ContentPermission, Group, GroupPermission, PagePermission, RoleGroup, UserGroup, UserProfile, MainMenu
from accounts.services import UserService
from auditlog import views as log_views
from auditlog.models import AuditAction
from base.models import AppResponse, Currency, CurrencyRate, SysParameter
from base.scheduler_view import insert_defualt_scheduler
from base.util import Util
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.core.files.storage import FileSystemStorage
from django.db import connection, transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import Context, Template
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from exception_log import manager
from post_office.models import EmailTemplate
from pws.models import ActiveOperators, Company, CompanyUser, Operator, OperatorLogs
from sqlalchemy import null
from pws.views import skill_data_auto_assign_to_login
# from accounts.forms import UserRoleForm
# from production.models import Labour
from sparrow.decorators import check_view_permission
from stronghold.decorators import public

from . import profile_image_generator
from .forms import GroupForm
import ipaddress

# from tenant_schemas.utils import schema_context


imguuid = str(uuid4())


@public
def signin(request):
    return render(request, "accounts/signin.html")


@public
@csrf_exempt
def authcheck(request):
    try:
        if request.method == "POST":
            username = request.POST["data[1][value]"]
            password = request.POST["data[2][value]"]
            redirect_url = request.POST["url_data"]

            # client = ClientService()

            user = authenticate(username=username, password=password)

            if user is None:
                return HttpResponse(AppResponse.msg(0, "Login failed, Invalid Username/Password, or your account may be inactive"), content_type="json")

            # subscription_expiration = client.is_subscription_expired("public")

            # if subscription_expiration:
            #     return HttpResponse(AppResponse.msg(0, "Your subscription is expired. Please contact to Intellial to re-activate subscription."), content_type="json")
            profile = UserProfile.objects.filter(user_id=user.id).first()
            if profile:
                if profile.is_deleted is True:
                    return HttpResponse(AppResponse.msg(0, "Failed to authenticate"), content_type="json")
                if profile.ip_restriction:
                    allowed_ips = SysParameter.objects.filter(para_code="ALLOWED_PUBLIC_IPS").values("para_value").first()
                    allowed_ips = json.loads(allowed_ips["para_value"])
                    ips = []
                    for allowed_ip in allowed_ips:
                        ips.append(allowed_ip["ip_name"])
                    my_ip_address = base_views.get_client_ip(request)
                    if my_ip_address not in ips and my_ip_address.rsplit(".", 1)[0] not in ips:
                        manager.create_from_text("User login failed due to IP restriction. Username:" + username + " User IP:" + my_ip_address)
                        return HttpResponse(AppResponse.msg(0, "You are not authorized to sign in from this location."), content_type="json")
            login(request, user)
            operator = Operator.objects.filter(user_id=user.id).values("id", "shift")
            if operator:
                excluded_order_status = ["cancel", "finished"]
                active_operator = ActiveOperators.objects.filter(~Q(reserved_order_id__order_status__in=excluded_order_status), operator_id_id=operator[0]["id"])
                if active_operator:
                    OperatorLogs.objects.filter(operator_id_id=operator[0]["id"]).update(logged_in_time=timezone.now(), shift_id=operator[0]["shift"], logged_out_time=None)
                    ActiveOperators.objects.filter(operator_id_id=operator[0]["id"]).update(logged_in_time=timezone.now(), shift_id=operator[0]["shift"])
                else:
                    OperatorLogs.objects.create(operator_id_id=operator[0]["id"], logged_in_time=timezone.now(), shift_id=operator[0]["shift"])
                    ActiveOperators.objects.create(operator_id_id=operator[0]["id"], logged_in_time=timezone.now(), shift_id=operator[0]["shift"])
            UserProfile.objects.filter(user_id=user.id, is_deleted=False).update(session_key=request.session.session_key)
            session = request.session
            session["username"] = username
            session["userid"] = user.id
            session["display_name"] = user.first_name + " " + user.last_name
            decimal_parameter = Util.get_sys_paramter("decimalpoint")
            currency_parameter = Currency.objects.filter(is_base=True, is_deleted=False).first()
            decimal_place = 4
            company = Company.objects.prefetch_related("companyuser_set").filter(companyuser__user__username=username).first()
            base_currency = ""
            if decimal_parameter is not None:
                decimal_place = int(decimal_parameter.para_value) if decimal_parameter.para_value not in (None, "") else 4
            if currency_parameter is not None:
                base_currency = currency_parameter.symbol

            session["decimal_point"] = decimal_place
            session["base_currency"] = base_currency
            # session["company_county"] = company["country_id"]
            # session["timezone"] = company["timezone"]
            session["profile_image"] = str(profile.profile_image) if profile.profile_image else ""
            session["color_scheme"] = profile.color_scheme
            session["bg_image"] = profile.image_name
            session["partner_id"] = profile.partner_id
            session.save()

            # def_page = profile.default_page if profile.default_page is not None else ""
            url_page = "/b/#/task/messages/"
            if company:
                url_page = "/b/#/pws_portal/dashboard/"
            if redirect_url != "":
                redirect_url = urllib.request.unquote(redirect_url)
                url_page = "/b/" + redirect_url
            skill_data_auto_assign_to_login(request, operator)
            return HttpResponse(AppResponse.msg(1, url_page), content_type="json")
        else:
            return HttpResponse(AppResponse.msg(0, "Failed to authenticate"), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def signup(request):
    try:

        if request.method == "POST":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password != confirm_password:
                return HttpResponse(AppResponse.msg(0, "Password do not match."), content_type="json")
            if User.objects.filter(email__iexact=email).count() > 0:
                return HttpResponse(AppResponse.msg(0, "A user with this email already exists."), content_type="json")

            # partner_id = Partner.objects.filter(is_hc=True).values("id").first()
            user = UserService.create_user(first_name, last_name, email, True, True, True, False)
            user.password = make_password(password)
            user.save()
            # form = UserForm(request.POST)
            # if form.is_valid():
            #     email = str(request.POST["email"]).strip()
            #     if request.POST["password"] != request.POST["confirm_password"]:
            #         return HttpResponse(AppResponse.msg(0, "Password do not match."), content_type="json")
            #     if User.objects.filter(email__iexact=email).count() > 0:
            #         return HttpResponse(AppResponse.get({"code": 0, "msg": "User already exist."}), content_type="json")
            #     nuser = form.save(commit=False)
            #     nuser.password = make_password(form.cleaned_data["password"])
            #     nuser.username = email
            #     nuser.is_active = False

            #     nuser = form.save()
            return HttpResponse(AppResponse.msg(1, "Thank you, you will receive a notification once your account is activated."), content_type="json")
            # else:
            #     return HttpResponse(AppResponse.msg(0, "Invalid input"), content_type="json")
        else:
            return render(request, "accounts/signup.html")
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def signout(request):
    operator = OperatorLogs.objects.filter(operator_id__user_id=request.user.id).values("id")
    if operator:
        ActiveOperators.objects.filter(operator_id__user_id=request.user.id).update(logged_in_time=None)
        OperatorLogs.objects.filter(operator_id__user_id=request.user.id).update(logged_in_time=None, logged_out_time=timezone.now())
    user = User.objects.get(id=request.user.id)
    logout(request)
    if operator:
        [s.delete() for s in Session.objects.all() if s.get_decoded().get('username') == user.username]
    response = HttpResponseRedirect("/accounts/signin/")
    # response.delete_cookie('loc_history')
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
        color_scheme = profile.color_scheme if profile.color_scheme is not None else ""
        color_scheme_data = {}
        if color_scheme != "":
            color_scheme = unicodedata.normalize("NFKD", color_scheme)
            # color_scheme_data = {}
            for param in color_scheme.split(","):
                scheme_data = param.split(":")
                if scheme_data != "":
                    color_scheme_data[scheme_data[0].strip()] = scheme_data[1].strip()
        bg_color = color_scheme_data["bg_color"] if color_scheme != "" else "#042853"
        button_color = color_scheme_data["button_color"] if color_scheme != "" else "#042853"
        link_color = color_scheme_data["link_color"] if color_scheme != "" else "#1f1bc1"
        row_color = color_scheme_data["row_color"] if "row_color" in color_scheme_data else "#e4e4e4"
        db_bg_color = color_scheme_data["db_bg_color"] if "db_bg_color" in color_scheme_data else "#d5e3f4"

        # notification_events = (
        #     NotificationEvent.objects.filter(is_active=True).exclude(group__in=["hrm", "others", "production", "maintenances"]).values("id", "group", "name").order_by("group")
        # )
        # subscribe_notifications = (
        #     SubscribeNotification.objects.filter(user_id=user.id, entity_id__isnull=True).values("event__id", "by_email", "in_system", "by_sms").order_by("event__group")
        # )

        sub_group_data = []
        # notifications_by_group = []
        # event_group_name = ""

        # for notification_event in notification_events:
        #     if event_group_name != notification_event["group"]:
        #         notifications_by_group = []
        #         event_group_name = notification_event["group"]
        #         sub_group_data.append(
        #             {"group_name": dict(choices.event_group)[notification_event["group"]], "group": notification_event["group"], "notifications": notifications_by_group}
        #         )

        #     sub_notifications = [subscribe_not for subscribe_not in subscribe_notifications if subscribe_not["event__id"] == notification_event["id"]]

        #     notifications_by_group.append(
        #         {
        #             "event_name": notification_event["name"],
        #             "event_code": notification_event["name"].replace(" ", "_").lower(),
        #             "by_email": False if len(sub_notifications) == 0 else sub_notifications[0]["by_email"],
        #             "in_system": False if len(sub_notifications) == 0 else sub_notifications[0]["in_system"],
        #             "by_sms": False if len(sub_notifications) == 0 else sub_notifications[0]["by_sms"],
        #         }
        #     )

        # if profile.comment_type_id:
        #     selected_remark = CommentType.objects.filter(id=profile.comment_type_id).values("id", "name").first()
        #     remark_types = CommentType.objects.all().exclude(id=profile.comment_type_id)
        # else:
        #     remark_types = CommentType.objects.all()
        form = ProfileForm(data, request.POST, request.FILES)
        can_edit_app_pref = False
        user = User.objects.get(id=request.user.id)
        perms = ["can_view_application_preference"]
        permission = Util.get_permission_role(user, perms)
        if permission["can_view_application_preference"] is True:
            can_edit_app_pref = True
        context = {}
        img_src = Util.get_resource_url("profile", str(profile.profile_image)) if profile.profile_image else ""
        context["form"] = form
        context["profile_image"] = img_src
        context["image_name"] = profile.image_name if profile.image_name is not None else ""
        context["image_url"] = settings.AWS_S3_HANDLER + str(profile.image_name) if profile.image_name is not None else ""
        context["notification_email"] = None
        context["notification_mob"] = None
        context["bg_color"] = bg_color
        context["button_color"] = button_color
        context["link_color"] = link_color
        context["row_color"] = row_color
        context["db_bg_color"] = db_bg_color
        context["columns"] = ["first_name", "last_name"]
        context["sub_group_data"] = sub_group_data
        context["first_name"] = user.first_name
        context["last_name"] = user.last_name
        context["email"] = user.email
        context["default_page"] = profile.default_page if profile.default_page else ""
        context["display_row"] = profile.display_row
        context["menu_launcher"] = profile.menu_launcher
        context["remark_types"] = ""
        context["selected_remark_type_id"] = None
        context["selected_remark_type"] = None
        context["can_edit_app_pref"] = can_edit_app_pref
        context["ftr_sms_service"] = (
            True if Util.get_sys_paramter("ftr_sms_service") is not None and Util.get_sys_paramter("ftr_sms_service").para_value.lower() == "true" else False
        )

        return render(request, "accounts/profile.html", context)


def save_profile(request):
    try:
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES)
            session = SessionStore(session_key=request.session.session_key)
            user = User.objects.get(username=request.session.get("username").strip())
            profile = UserProfile.objects.get(user=user)
            color_scheme = profile.color_scheme if profile.color_scheme is not None else ""
            if form.is_valid():
                user = User.objects.get(username=session.get("username").strip())
                user.first_name = str(request.POST["first_name"]).strip()
                user.last_name = str(request.POST["last_name"]).strip()
                remark_type = int(request.POST.get("profile_remark_type")) if request.POST.get("profile_remark_type") is not None else None
                display_row = int(request.POST["display_row"])
                is_file = request.FILES.get("profile_image", False)
                bg_color = str(request.POST["theme"]).strip()
                theme = Util.get_sys_paramter("THEMES").descr
                theme_active = eval(theme)
                if bg_color != "None":
                    theme_property = theme_active.get(bg_color.replace("_active", ""))
                    apply_theme = theme_property.split(",")
                    bg_color = apply_theme[0].replace("bg_color:", "")
                    button_color = apply_theme[1].replace("button_color:", "")
                    link_color = apply_theme[2].replace("link_color:", "")
                    row_color = apply_theme[3].replace("row_color:", "")
                    db_bg_color = apply_theme[4].replace("db_bg_color:", "")
                else:
                    user_ = User.objects.get(username=request.session.get("username").strip())
                    profile = UserProfile.objects.get(user=user_)
                    previous_theme = profile.color_scheme.split(",")
                    pre_bg_color = previous_theme[0].replace("bg_color:", "")
                    pre_button_color = previous_theme[1].replace("button_color:", "")
                    pre_link_color = previous_theme[2].replace("link_color:", "")
                    pre_row_color = previous_theme[3].replace("row_color:", "")
                    pre_db_bg_color = previous_theme[3].replace("db_bg_color:", "")
                    button_color = pre_button_color
                    link_color = pre_link_color
                    row_color = pre_row_color
                    bg_color = pre_bg_color
                    db_bg_color = pre_db_bg_color

                bg_image = request.POST.get("bgImage")
                user_full_name = user.first_name + " " + user.last_name
                new_image = ""
                color_scheme = (
                    "bg_color:" + bg_color + ",button_color:" + button_color + ",link_color:" + link_color + ",row_color:" + row_color + ",db_bg_color:" + db_bg_color + ""
                )
                profile = UserProfile.objects.get(user=user)
                if remark_type:
                    profile.comment_type_id = remark_type
                    profile.save()
                if remark_type == 0:
                    UserProfile.objects.filter(user=user).update(comment_type=None)
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
                if bg_image is not None:
                    profile = UserProfile.objects.get(user=user)
                    profile.image_name = bg_image
                    profile.save()
                    session["bg_image"] = bg_image
                if display_row is not None:
                    profile = UserProfile.objects.get(user=user)
                    profile.display_row = display_row
                    profile.save()
                    session["display_row"] = display_row

                if user_full_name is not None:
                    profile.user_full_name = user_full_name
                    session["display_name"] = user_full_name
                if profile.notification_email is not None:
                    session["notification_email"] = profile.notification_email

                # profile.default_page = default_page
                # profile.menu_launcher = menu_launcher
                profile.save()
                session["profile_image"] = str(profile.profile_image)
                # session["default_page"] = default_page
                session.save()
                user.save()
                if new_image != "":
                    return HttpResponse(json.dumps({"code": 1, "msg": "Profile Updated.", "avatar": new_image, "bg_color": bg_color}), content_type="json")
                return HttpResponse(AppResponse.get({"code": 1, "msg": "Profile Updated.", "bg_color": bg_color}), content_type="json")
            else:
                return HttpResponse(AppResponse.msg(0, str(form.errors)), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        # logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_password(request):
    try:
        user_id = request.POST.get("id") if request.POST.get("id") else request.user.id
        user = User.objects.get(id=user_id)
        user.password = make_password(str(request.POST["password"]).strip())
        user.save()
        is_reload = True if user.id == request.user.id else False
        return HttpResponse(json.dumps({"code": 1, "msg": "Password updated.", "is_reload": is_reload}), content_type="json")

    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_background_images(request):
    try:
        # parent = dirname(dirname(abspath(__file__)))
        response = []
        bg_images = UserService.get_background_images_list("sparrow-bg")
        for image in bg_images:
            response.append({"name": image["Key"], "src": settings.AWS_S3_HANDLER + str(image["Key"])})
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"roles": "accounts_roles"}])
def roles(request):
    return render(request, "accounts/roles.html")


def roles_search(request, q=None):
    request.POST = Util.get_post_data(request)
    start = int(request.POST["start"])
    length = int(request.POST["length"])
    sort_col = Util.get_sort_column(request.POST)

    query = Q()

    if request.POST.get("group__name") is not None:
        query.add(Q(group__name__icontains=str(request.POST.get("group__name"))), query.connector)

    recordsTotal = RoleGroup.objects.filter(Q(is_deleted=False), Q(query)).count()
    # recordsTotal = Group.objects.filter(query).count()
    # user_roles = Group.objects.filter(query).order_by(sort_col)[start : (start + length)]

    response = {
        "draw": request.POST["draw"],
        "recordsTotal": recordsTotal,
        "recordsFiltered": recordsTotal,
        "data": [],
    }

    # user_role_name = [user_role.name for user_role in user_roles]
    # description = RoleGroup.objects.filter(group__name__in=user_role_name).values("group__name", "description")
    # descriptions = Util.get_dict_from_quryset("group__name", "description", description)
    user_roles_ = RoleGroup.objects.filter(Q(is_deleted=False), Q(query)).values("group_id", "group__name", "description").order_by(sort_col)[start : (start + length)]

    # for user_role in user_roles:
    #     response["data"].append({"id": user_role.id, "name": user_role.name, "description": descriptions[user_role.name]})

    for user_role in user_roles_:
        response["data"].append({"id": user_role["group_id"], "group__name": user_role["group__name"], "description": user_role["description"]})

    return HttpResponse(AppResponse.get(response), content_type="json")


# @check_view_permission([{"admin_tools": "roles"}])
def role(request, role_id=None):
    try:
        with transaction.atomic():
            if request.method == "POST":
                id = request.POST.get("id")
                name = request.POST["name"].strip()
                description = request.POST["description"]
                user_id = request.user.id
                user = User.objects.get(id=user_id)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.UPDATE
                role_opera_user = request.POST.get("role_opera_user")
                operator = ""
                customer_user = ""
                if role_opera_user == "operator":
                    operator = True
                else:
                    operator = False

                if role_opera_user == "customer user":
                    customer_user = True
                else:
                    customer_user = False
                if id is None or id == "0":
                    if name != "" and Group.objects.filter(name__iexact=name).count() > 0:
                        return HttpResponse(AppResponse.get({"code": 0, "msg": "User role name already exist."}), content_type="json")
                    if Util.has_perm("can_add_roles", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    form = GroupForm(request.POST)
                    action = AuditAction.INSERT
                else:
                    if Util.has_perm("can_update_roles", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    group = Group.objects.get(id=int(id))
                    rolegroup = RoleGroup.objects.filter(group_id=group.id).values("id").first()
                    RoleGroup.objects.filter(id=rolegroup["id"]).update(user=customer_user, operator=operator, description=description)
                    if name != "" and name.lower() != group.name.lower() and Group.objects.filter(name__iexact=name).count() > 0:
                        return HttpResponse(AppResponse.get({"code": 0, "msg": "User role name already exist."}), content_type="json")
                    form = GroupForm(request.POST, instance=group)

                if form.is_valid():
                    group = form.save()
                    if not RoleGroup.objects.filter(group__name__iexact=name):
                        RoleGroup.objects.create(group_id=group.id, user=customer_user, operator=operator, description=description)
                    group_id = group.id
                    permission_ids = str(request.POST["role_assi_perm"]).strip()
                    new_permissions = []

                    if permission_ids != "":
                        new_permissions = [int(x) for x in permission_ids.split(",")]
                        role_permissions = (
                            GroupPermission.objects.filter(group_id=group_id, page_permission_id__isnull=False).values_list("page_permission_id", flat=True).distinct()
                        )
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
                    if action == AuditAction.INSERT:
                        log_views.insert("auth", "group", [group_id], action, user_id, c_ip, "Role has been created")
                        return HttpResponse(json.dumps({"code": 1, "msg": "Role has been created", "id": group_id}), content_type="json")
                    else:
                        log_views.insert("auth", "group", [group_id], action, user_id, c_ip, "Role has been updated")
                        return HttpResponse(AppResponse.msg(1, "Role details update"), content_type="json")
                else:
                    return HttpResponse(AppResponse.msg(0, "Invalid form"), content_type="json")

            list_data = []
            perms = []

            content_permissions = (
                ContentPermission.objects.all()
                .exclude(content_group__in=["CRM", "Planning", "Production", "Human resources", "Maintenances", "Others", "All Reports", "EDA"])
                .order_by("sequence")
            )
            for content_permission in content_permissions:
                index = next((index for index, item in enumerate(list_data) if item["content_group"] == content_permission.content_group), None)
                if index is None:
                    content_name = add_perm_list(content_permission.content_group, [])
                    list_data.append({"content_group": content_permission.content_group, "content_name": content_name})

            avail_perms = PagePermission.objects.filter(content__isnull=False).values("menu_id", "act_name", "act_code", "id", "content_id", "content__content_group")
            groups = PagePermission.objects.filter(content__isnull=False).values("menu__name", "menu__menu_code", "menu__is_operator", "menu__is_customer_user", "content__content_group")
            customer_group_dict = {}
            operator_group_dict = {}
            for group in groups:
                if group["menu__is_customer_user"]:
                    customer_group_dict[group["menu__menu_code"]] = group["content__content_group"]
                if group["menu__is_operator"]:
                    operator_group_dict[group["menu__menu_code"]] = group["content__content_group"]
            customer_group = []
            operator_group = []
            for customer in customer_group_dict.values():
                if customer not in customer_group:
                    customer_group.append(customer)
            for operator in operator_group_dict.values():
                if operator not in operator_group:
                    operator_group.append(operator)
            all_menu = MainMenu.objects.all().values("name", "is_operator", "is_customer_user").order_by("sequence")
            # customer_group = ["Order Tracking", "Exception", "Place order", "Dashboard", "Reports"]
            # operator_group = ["Settings", "Other Utilities", "Reports", "Exceptions", "Admin tools", "Job Processing", "Documents", "Message", "Bug Report"]
            if role_id != "0" and role_id is not None:
                group = Group.objects.filter(id=role_id).first()
                rolegroup = RoleGroup.objects.filter(group_id=role_id).first()
                for lists in list_data:
                    for permission in lists["content_name"]:
                        applied_perms = GroupPermission.objects.filter(page_permission__content__id=permission["id"], group_id=role_id).values_list("page_permission_id", flat=True)
                        perms = list(chain(perms, applied_perms))
                return render(
                    request,
                    "accounts/role.html",
                    {
                        "permissions": avail_perms,
                        "applied_perms": perms,
                        "lists": list_data,
                        "group": group,
                        "rolegroup": rolegroup,
                        "customer_group": customer_group,
                        "operator_group": operator_group,
                        "all_menu": all_menu,
                    },
                )
            else:
                return render(
                    request,
                    "accounts/role.html",
                    {
                        "group": None,
                        "permissions": avail_perms,
                        "applied_perms": perms,
                        "lists": list_data,
                        "rolegroup": None,
                        "customer_group": customer_group,
                        "operator_group": operator_group,
                        "all_menu": all_menu,
                    },
                )
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def add_perm_list(content_group, list_data):
    content_groups = ContentPermission.objects.filter(content_group=content_group).order_by("sequence")
    for content_group in content_groups:
        main_menu = MainMenu.objects.filter(name=content_group.content_name).values("name", "is_operator", "is_customer_user").first()
        list_data.append({"id": content_group.id, "content_name": content_group.content_name, "is_operator": main_menu["is_operator"] if main_menu else None, "is_customer_user": main_menu["is_customer_user"] if main_menu else None})
    return list_data


def role_del(request):
    try:
        role_ids = request.POST.get("ids")
        if not role_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_delete_roles", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        ids = [int(x) for x in role_ids.split(",")]
        assigned_roles = ""
        roles = UserGroup.objects.filter(group_id__in=ids).values("group__name", "user__username", "user")
        for role in roles:
            operator_is_deleted = Operator.objects.filter(user=role["user"]).values("is_deleted").first()
            if operator_is_deleted:
                op_delete = operator_is_deleted["is_deleted"]
            else:
                op_delete = None
            customer_user_is_deleted = CompanyUser.objects.filter(user=role["user"]).values("is_deleted").first()
            if customer_user_is_deleted:
                cu_delete = customer_user_is_deleted["is_deleted"]
            else:
                cu_delete = None
            if op_delete is False or cu_delete is False:
                assigned_roles = assigned_roles + role["group__name"] + ", "
            # assigned_roles = assigned_roles + role["group__name"] + ", "

        if assigned_roles != "":
            return HttpResponse(AppResponse.msg(0, 'Role "' + assigned_roles[:-2] + '" is assigned to some users. Action cannot be performed. '), content_type="json")

        # GroupPermission.objects.filter(group_id__in=ids).delete()
        # Group.objects.filter(id__in=ids).delete()
        RoleGroup.objects.filter(group_id__in=ids).update(is_deleted=True)
        return HttpResponse(AppResponse.msg(1, "Role has been deleted "), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong!")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@csrf_exempt
@public
@transaction.atomic
def sparrow_setup(request):
    try:
        user_data = json.loads(request.POST["data"])
        c_ip = base_views.get_client_ip(request)
        diff = datetime.timedelta(days=720)
        valid_until = datetime.datetime.now() + diff
        new_port = user_data["domain"].split(":")[1]
        dump_schema_and_data(user_data["dbschema"], user_data["domain"], valid_until, user_data["username"])

        set_sparrow_default_values(user_data, c_ip)

        return HttpResponse(json.dumps({"code": 1, "msg": "Completed", "port": new_port}), content_type="json")

    except Exception as e:
        logging.exception("Something went wrong!")
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@transaction.atomic
def dump_schema_and_data(schema, domain, valid_until, user_name):
    with transaction.atomic():
        commands = []
        command = ""
        db_schema_file = os.path.join(settings.BASE_DIR, "db_schema.sql")
        with open(db_schema_file) as fp:
            for line in fp:
                if line[0] == "-" or line[0] == "\n":
                    continue

                if line.startswith("CREATE SCHEMA") or line.startswith("ALTER SCHEMA"):
                    line = line.replace(" ec", " " + schema)

                if line.startswith("SET"):
                    pass
                elif line.startswith("ALTER TABLE"):
                    line = line.replace("nextval('ec.", "nextval('" + schema + ".")
                    line = line.replace(" ec.", " " + schema + ".")
                else:
                    line = line.replace(" ec.", " " + schema + ".")
                command += line

                if line.endswith(";\n"):
                    commands.append(command)
                    command = ""
            fp.close()
        warehouse = "insert into " + schema + ".inventory_warehouse(id,name,is_deleted,code) values(1,'Warehouse',False,'WH1');"
        cursor = connection.cursor()
        cursor.execute("select * from clients_client order by -id limit 1 ")
        row = cursor.fetchone()
        client_id = row[0] + 1
        cursor.execute("SET search_path TO " + schema + ",public")
        cursor.execute(
            """ INSERT INTO clients_client(id,domain_url,schema_name,name,on_trial,paid_until,created_on) VALUES ('%s','%s','%s','%s','%s','%s','%s') """
            % (client_id, domain, schema, schema, False, valid_until, datetime.datetime.now())
        )
        for command in commands:
            cursor.execute(command)
        cursor.execute(warehouse)
        cursor.execute("update " + schema + ".base_sysparameter set para_value = '" + str(client_id) + "' where para_code='company_code';")
        cursor.execute("update " + schema + ".base_sysparameter set para_value = 'true' where para_code='ENFORCE_INVENTORY';")
        cursor.execute("update " + schema + ".base_sysparameter set para_value = 'false' where para_code='ftr_sms_service';")
        cursor.execute("update " + schema + ".base_sysparameter set para_value = 'false' where para_code='quotation_approval';")
        cursor.execute("update " + schema + ".base_sysparameter set para_value = '" + user_name + "' where para_code='HRM_LEAVE_REQUEST_MAIL';")
        cursor.execute("update " + schema + ".base_sysparameter set para_value = 5 where para_code='SALES_CONTRACT_DEFAULT_SUPPLIERS';")
        cursor.execute(
            "update "
            + schema
            + """.accounts_mainmenu set is_active = 'f' where menu_code
            in ('logistics_mycronic','po_external_category','so_external_category',
            'sparrow_test','spw_test_employee_addresses','employees')"""
        )


@transaction.atomic
def set_sparrow_default_values(user_data, c_ip):
    try:
        schema = user_data["dbschema"]
        with schema_context(schema):
            with transaction.atomic():
                user = User.objects.create_superuser(
                    username=user_data["username"], password=user_data["password"], email=user_data["username"], first_name=user_data["firstName"], last_name=user_data["lastName"]
                )
                user_id = user.id

                Currency.objects.filter(is_base=True).update(is_base=False)
                currency_obj = Currency.objects.filter(symbol=user_data["currency"]).first()
                if currency_obj:
                    currency_obj.is_base = True
                    currency_obj.save()
                if not currency_obj:
                    currency_obj = Currency.objects.create(symbol=user_data["currency"], name=user_data["currency_name"], is_deleted=False, is_base=True)
                currency_rate_obj = [CurrencyRate(currency_id=currency_obj.id, factor=1, created_by_id=user_id, reference_date=datetime.datetime.now())]
                cur_and_rate = {}
                cur_and_rate["EUR"] = user_data["eur"]
                cur_and_rate["GBP"] = user_data["gbp"]
                cur_and_rate["USD"] = user_data["usd"]

                req_cur = [sym for sym in cur_and_rate]
                all_cur = Currency.objects.filter(symbol__in=req_cur).values("id", "symbol")

                for cur in all_cur:
                    if cur["symbol"] != user_data["currency"]:
                        currency_rate_obj.append(
                            CurrencyRate(currency_id=cur["id"], factor=1 / float(cur_and_rate[cur["symbol"]]), created_by_id=user_id, reference_date=datetime.datetime.now())
                        )
                CurrencyRate.objects.bulk_create(currency_rate_obj)

                country_obj = Country.objects.filter(code=user_data["country"]).first()
                if not country_obj:
                    country_obj = Country.objects.create(name=user_data["country_name"], code=user_data["country"])

                partner = Partner.objects.create(
                    name=user_data["companyName"],
                    is_hc=True,
                    currency_id=currency_obj.id,
                    timezone_offset=user_data["time_zone"],
                    country_id=country_obj.id,
                    email=user_data["username"],
                    tax_status="standard",
                )

                user_profile = UserProfile.objects.create(user_id=user_id, partner_id=partner.id, user_type=1, notification_email=user_data["username"])
                Labour.objects.create(name=user_data["firstName"] + " " + user_data["lastName"], user_id=user_id, created_by_id=user_id)
                characters = user_data["firstName"][0] + user_data["lastName"][0]
                profile_image_name = profile_image_generator.GenerateCharacters(characters, user_profile.id)
                user_profile.profile_image = profile_image_name
                user_profile.save()
                email_from_query = "update " + schema + ".base_sysparameter set para_value = '" + user_data["companyName"] + "' where para_code='email_from_name';"
                insert_defualt_scheduler(c_ip, user_id)

                new_logo_path = Util.get_resource_path("", "")
                if not os.path.exists(new_logo_path):
                    os.makedirs(new_logo_path)
                new_logo_path = os.path.join(new_logo_path, "doc_logo.png")
                logo_file = os.path.join(settings.BASE_DIR, "base", "static", "base", "images", "sparrow-logo.jpg")
                copy(logo_file, new_logo_path)
                cursor = connection.cursor()
                cursor.execute(email_from_query)

                demo_data_file = os.path.join(settings.BASE_DIR, "insertDemoData.sql")
                with open(demo_data_file) as fp:
                    cursor.execute("SET search_path TO " + schema + ",public")
                    for line in fp:
                        cursor.execute(line)
                    fp.close()
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
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
                expire_on = datetime.datetime.utcnow() + datetime.timedelta(seconds=120)
                AuthToken.objects.create(user_id=user_id, token=token, expire_on=expire_on)
                context = {"user_name": user.first_name, "token": token}
                if is_email:
                    template = EmailTemplate.objects.filter(name__iexact="email_verification").values("id").first()
                    send_email_by_tmpl(False, "public", [email], template["id"], context)

                if is_mobile_no:
                    send_sms([mobile_no], "mobile_verification", context)

                return HttpResponse(json.dumps({"code": 1, "msg": ""}), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
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
            # auth_token = AuthToken.objects.filter(token=token, user_id=user_id, is_used=False).first()
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


def submit_sparrow_issue(request):
    try:
        if request.method == "POST":
            title = "Sparrow support: " + request.POST["title"]
            request_type = request.POST["request_type"]
            partner_id = request.session["partner_id"]
            # company_name = Partner.objects.filter(id=partner_id).values("name").first()
            user_full_name = request.session["display_name"]
            custom_value = company_name["name"] + "_$" + user_full_name + "_$" + request_type + "_$"

            fields = {
                "customerId": "i010",
                "fromEmail": request.POST["from_email"],
                "fromName": user_full_name,
                "subject": title,
                "msg": request.POST["details"],
                "custom_value": custom_value,
            }

            multi_params = []
            from poster.encode import MultipartParam, multipart_encode

            for name, value in fields.items():
                multi_params.append(MultipartParam(name, value, filetype="text/plain"))

            if request.FILES:
                file = request.FILES["file"]
                temp_path = os.path.join(settings.RESOURCES_ROOT, "temp")
                fs = FileSystemStorage(location=temp_path)

                filename = fs.save(file.name, file)
                file_path = os.path.join(temp_path, filename)

                multi_file_param = MultipartParam.from_file("attach", file_path)

                multi_params.append(multi_file_param)

            datagen, headers = multipart_encode(multi_params)

            request = urllib.request.Request(settings.SPARROW_SUPPORT_URL, "".join(datagen).encode(), headers)
            context = ssl._create_unverified_context()
            response = urllib.request.urlopen(request, context=context, timeout=10)
            res = response.read()

            res = AppResponse.msg(1, "")
            return HttpResponse(res, content_type="json")
        else:
            user_id = request.session["userid"]
            user_email = request.session["username"]

            notification_email = UserProfile.objects.filter(user_id=user_id).values("notification_email").first()
            email = notification_email if notification_email is not None else user_email

            return render(request, "accounts/support.html", {"email": email["notification_email"]})
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def notification_delete(request):
    try:
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
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def customer_registration(request):
    try:
        with transaction.atomic():
            if request.method == "POST":
                email = str(request.POST["email"]).strip()
                first_name = request.POST["first_name"]
                last_name = request.POST["last_name"]
                job_title = request.POST["job_title"]
                company = request.POST["company"]
                no_of_employees = request.POST["no_of_employees"]
                phone = request.POST["phone"]
                country = request.POST["country"]
                if User.objects.filter(email__iexact=email).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "A user with this email already exists."}), content_type="json")
                # country_obj = Country.objects.filter(name=country).first()
                # Partner.objects.create(name=company, email=email, is_company=True, phone=phone, country=country_obj, is_hc=True)
                # partner_id = Partner.objects.filter(is_hc=True).values("id").first()
                user = UserService.create_user(first_name, last_name, email, False, True, False, partner_id["id"], False)
                to_email = Util.get_sys_paramter("INTELLIAL_INFO_MAIL").para_value
                admin_template = EmailTemplate.objects.filter(name__iexact="intellial_customer_registration_notification").first()
                admin_context = Context(
                    {
                        "username": user.first_name + " " + user.last_name,
                        "email": user.email,
                        "job_title": job_title,
                        "no_of_employees": no_of_employees,
                        "company": company,
                        "phone": phone,
                        "country": country,
                    }
                )
                # send email to admin(Intellial)
                admin_template_content = Template(admin_template.html_content).render(admin_context)
                # send_mail(False, "public", [to_email], admin_template.subject, admin_template_content, "")
                # send email to user
                user_template = EmailTemplate.objects.filter(name__iexact="customer_registration").first()
                user_context = Context({"username": first_name + " " + last_name})
                user_template_content = Template(user_template.html_content).render(user_context)
                # send_mail(False, "public", [email], user_template.subject, user_template_content, "")

                return HttpResponse(AppResponse.msg(1, "Thank you, you will receive activation mail once your account has been activated."), content_type="json")
            else:
                return render(request, "accounts/customer_registration.html")
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @check_view_permission([{"Others": "allowed_ip"}])
def whitelist_ips(request):
    try:
        allowed_ips = SysParameter.objects.filter(para_code="ALLOWED_PUBLIC_IPS").values("para_value").first()
        user_ids = []
        ips = json.loads(allowed_ips["para_value"]) if allowed_ips["para_value"] != "" else []

        for data in ips:
            if data["user_id"] not in user_ids:
                user_ids.append(data["user_id"])

        user_ids.append(request.session["userid"])
        users = UserProfile.objects.filter(user__id__in=user_ids).values("user__id", "user__first_name", "user__last_name")
        user_data = {}
        for user in users:
            user_data[user["user__id"]] = user["user__first_name"] + " " + user["user__last_name"]

        perms = ["can_add_ip", "can_delete_ip", "can_update_ip"]
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        permissions = Util.get_permission_role(user, perms)
        return render(
            request,
            "accounts/whitelisting_ip.html",
            {"allowed_ips": ips, "login_user_data": json.dumps({"id": request.session["userid"]}), "user_data": json.dumps(user_data), "permissions": json.dumps(permissions)},
            content_type="json",
        )

    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_whitelist_ip(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_update_ip", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        ip_data = request.POST["ip_data"]
        msg = "Record deleted." if request.POST["type"] == "delete" else "Record saved."
        SysParameter.objects.filter(para_code="ALLOWED_PUBLIC_IPS").update(para_value=ip_data)
        return HttpResponse(json.dumps({"code": 1, "msg": msg}), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# customer master


def customer_masters(request):
    return render(request, "accounts/customer_masters.html")


def customer_masters_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        recordsTotal = 0
        query = Q()

        if request.POST.get("first_name__icontains") is not None:
            query.add(
                Q(first_name__icontains=str(request.POST.get("first_name__icontains").strip())),
                query.connector,
            )

        if request.POST.get("last_name__icontains") is not None:
            query.add(
                Q(last_name__icontains=str(request.POST.get("last_name__icontains").strip())),
                query.connector,
            )

        if request.POST.get("email__icontains") is not None:
            query.add(
                Q(email__icontains=str(request.POST.get("email__icontains").strip())),
                query.connector,
            )

        if request.POST.get("role__icontains") is not None:
            user_ids = UserGroup.objects.filter(group__name__icontains=str(request.POST.get("role__icontains").strip())).values_list("user_id", flat=True).distinct()
            query.add(Q(id__in=user_ids), query.connector)
        user_datas = UserProfile.objects.filter(is_deleted=False).values("user_id").distinct()
        user_ids = [id["user_id"] for id in user_datas]
        query.add(Q(id__in=user_ids, is_superuser=False), query.connector)
        recordsTotal = User.objects.filter(query).count()
        users = User.objects.filter(query).values("id", "first_name", "last_name", "email", "is_active", "last_login").order_by(sort_col)[start : (start + length)]

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        user_ids = [user["id"] for user in users]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")

        role_data = {}
        for user_role in user_roles:
            role_name = user_role["group__name"]
            if user_role["user_id"] in role_data:
                role_name = role_name + ", " + role_data[user_role["user_id"]]
            role_data[user_role["user_id"]] = role_name

        for user in users:
            remark_type = ""
            response["data"].append(
                {
                    "id": user["id"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "email": user["email"],
                    "is_active": "Yes" if user["is_active"] else "No",
                    "user_role_obj": role_data[user["id"]] if user["id"] in role_data else "",
                    "remark_type": remark_type,
                    "last_login": user["last_login"].strftime("%y-%m-%d %a %H:%M:%S") if user["last_login"] is not None else "",
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
