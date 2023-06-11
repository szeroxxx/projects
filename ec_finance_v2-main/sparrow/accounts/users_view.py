import json
import logging

from auditlog import views as log_views
from auditlog.models import AuditAction
from base import views as base_views
from base.models import AppResponse
from base.util import Util
from django.conf import settings
from django.contrib.sessions.models import Session
from django.db import transaction
from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render
from exception_log import manager

from accounts.models import MainMenu, User, UserGroup, UserProfile
from accounts.services import UserService

# from production.models import Labour
# from sparrow.decorators import check_view_permission


def get_permitted_menu(user_id, is_superuser):
    menu_ids = []
    main_menu_ids = []

    user_perms_objs = Util.get_user_permissions(user_id)
    for user_perms_obj in user_perms_objs:
        if user_perms_obj["page_permission__act_code"] in ["view", "can_view"]:
            menu_ids.append(user_perms_obj["page_permission__menu_id"])

    parent_menu_query = Q()
    child_menu_query = Q()

    if not is_superuser:
        parent_menu_query.add(Q(parent_id_id__in=menu_ids), parent_menu_query.connector)

    child_menus = MainMenu.objects.filter(parent_menu_query).values_list("id", flat=True)

    menu_ids += child_menus
    if not is_superuser:
        child_menu_query.add(Q(id__in=menu_ids, parent_id_id__isnull=False), child_menu_query.connector)

    sub_parent_menus = MainMenu.objects.filter(child_menu_query).values_list("parent_id_id", flat=True).distinct()

    menu_ids += sub_parent_menus

    for menu_id in menu_ids:
        if menu_id is not None:
            main_menu_ids.append(menu_id)

    return ",".join(map(str, main_menu_ids))


# @check_view_permission([{"admin_tools": "accounts_users"}])
def users(request):
    return render(request, "accounts/users.html")


def users_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        recordsTotal = 0
        query = Q()

        if request.POST.get("first_name__icontains") is not None:
            query.add(
                Q(first_name__icontains=str(request.POST.get("first_name__icontains").strip())), query.connector,
            )

        if request.POST.get("last_name__icontains") is not None:
            query.add(
                Q(last_name__icontains=str(request.POST.get("last_name__icontains").strip())), query.connector,
            )

        if request.POST.get("email__icontains") is not None:
            query.add(
                Q(email__icontains=str(request.POST.get("email__icontains").strip())), query.connector,
            )

        if request.POST.get("role__icontains") is not None:
            user_ids = UserGroup.objects.filter(group__name__icontains=str(request.POST.get("role__icontains").strip())).values_list("user_id", flat=True).distinct()
            query.add(Q(id__in=user_ids), query.connector)
        user_ids = UserProfile.objects.filter(is_deleted=False).values_list("user_id", flat=True).distinct()
        query.add(Q(id__in=user_ids, is_superuser=False), query.connector)
        recordsTotal = User.objects.filter(query).count()
        users = User.objects.filter(query).order_by(sort_col)[start : (start + length)]

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        user_ids = [user.id for user in users]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")

        role_data = {}
        for user_role in user_roles:
            role_name = user_role["group__name"]
            if user_role["user_id"] in role_data:
                role_name = role_name + ", " + role_data[user_role["user_id"]]
            role_data[user_role["user_id"]] = role_name

        for user in users:
            response["data"].append(
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "is_active": "Yes" if user.is_active else "No",
                    "user_role_obj": role_data[user.id] if user.id in role_data else "",
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @check_view_permission([{"admin_tools": "accounts_users"}])
def user(request, users_id):
    try:
        with transaction.atomic():
            if request.method == "POST":
                id = int(request.POST.get("id"))
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.UPDATE
                user_id = request.user.id
                user = User.objects.get(id=user_id)
                first_name = str(request.POST["first_name"]).strip()
                last_name = str(request.POST["last_name"]).strip()
                email = str(request.POST["email"]).strip()
                active = str(request.POST.get("active")).strip()
                ip_restriction = "ip_restriction" in request.POST
                user_role_ids = request.POST.get("user_role_ids", False)
                role_ids = []
                if user_role_ids:
                    role_ids = [int(x) for x in user_role_ids.split(",")]

                if id == 0:

                    if Util.has_perm("can_add_accounts_users", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")

                    if User.objects.filter(email__iexact=email).count() > 0:
                        return HttpResponse(AppResponse.get({"code": 0, "msg": "Email already exist."}), content_type="json",)

                    action = AuditAction.INSERT

                    # allow_to_create_user = client.subscription_users_count(connection.tenant.schema_name)

                    # if allow_to_create_user is False:
                    #     return HttpResponse(AppResponse.msg(0, "Your limit is exceed to create new user."), content_type="json")

                    partner_id = request.session["partner_id"]
                    is_active = True if active == "on" else False
                    user = UserService.create_user(first_name, last_name, email, False, True, is_active, partner_id, ip_restriction)

                    for role_id in role_ids:
                        UserGroup.objects.create(user_id=user.id, group_id=role_id)

                    log_views.insert(
                        "accounts", "userprofile", [user.id], action, user_id, c_ip, log_views.getLogDesc("User", action),
                    )
                    return HttpResponse(json.dumps({"code": 1, "msg": "Data saved", "id": user.id, "is_reload": True}), content_type="json",)
                else:
                    if Util.has_perm("can_update_accounts_users", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    user = User.objects.get(id=id)
                    if User.objects.filter(username__iexact=email, is_active=True).exclude(username__iexact=user.email, is_active=True).count() > 0:
                        return HttpResponse(AppResponse.get({"code": 0, "msg": "Email already exist."}), content_type="json",)

                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.username = email
                    is_reload = False
                    if active == "on":
                        user.is_active = True
                    else:
                        user.is_active = False
                        session_key = UserProfile.objects.filter(user_id=user.id).values("session_key").first()
                        Session.objects.filter(session_key=session_key["session_key"]).delete()

                    user.save()
                    if id == request.user.id:
                        session = request.session
                        session["display_name"] = first_name + " " + last_name
                    profile = UserProfile.objects.filter(user_id=user.id).first()
                    profile.ip_restriction = ip_restriction
                    if profile is None:
                        profile = UserProfile(user=user, user_type=1, color_scheme=settings.DEFAULT_COLOR_SCHEME, avatar="", ip_restriction=ip_restriction,)
                    profile.save()
                    exist_role_ids = UserGroup.objects.filter(user_id=user.id).values_list("group_id", flat=True).distinct()
                    for role_id in role_ids:
                        if role_id not in exist_role_ids:
                            UserGroup.objects.create(user_id=user.id, group_id=role_id)

                        delete_role_ids = [x for x in exist_role_ids if x not in role_ids]
                        UserGroup.objects.filter(user_id=user.id, group_id__in=delete_role_ids).delete()
                        if len(delete_role_ids) > 0:
                            UserGroup.objects.filter(user_id=user.id, group_id__in=delete_role_ids).delete()
                        is_reload = True if user.id == request.user.id and user.username != request.session["username"] else False
                        if is_reload:
                            del request.session["username"]

                    log_views.insert(
                        "accounts", "userprofile", [user.id], action, user_id, c_ip, log_views.getLogDesc("User", action),
                    )

                    return HttpResponse(json.dumps({"code": 1, "msg": "Data saved", "id": user.id, "is_reload": is_reload}), content_type="json",)
            else:
                if users_id is not None and users_id != "0":
                    user_profile = UserProfile.objects.filter(user_id=users_id).first()
                    user = User.objects.get(id=users_id)
                    ip_restriction = user_profile.ip_restriction
                    user_role_obj = UserGroup.objects.filter(user_id=users_id).values_list("group_id", flat=True).distinct()

                    return render(
                        request,
                        "accounts/user.html",
                        {
                            "user_id": user.id,
                            "first_name": user.first_name,
                            "active": user.is_active,
                            "email": user.email,
                            "ip_restriction": ip_restriction,
                            "last_name": user.last_name,
                            "user_type": user_profile.user_type,
                            "user_role_obj": ",".join(str(x) for x in user_role_obj),
                        },
                    )
                else:
                    return render(request, "accounts/user.html", {"first_name": None, "last_name": None, "email": None, "ip_restriction": False, "user_role_obj": None},)
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def users_del(request, usersid=None):
    try:
        with transaction.atomic():
            post_ids = request.POST.get("ids") if request.POST.get("ids") else request.POST.get("id")
            user_id = request.user.id
            user = User.objects.get(id=user_id)

            if Util.has_perm("can_delete_accounts_users", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")

            if not post_ids:
                return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json",)

            ids = [int(x) for x in post_ids.split(",")]

            session_key = list(UserProfile.objects.filter(user_id__in=ids).values_list("session_key", flat=True))
            Session.objects.filter(session_key__in=session_key).delete()

            user_emails = list(User.objects.filter(id__in=ids).values_list("email", flat=True))
            for email in user_emails:
                total_user = User.objects.filter(email__icontains=email).count()
                User.objects.filter(email=email).update(email=Concat(Value("(Deleted)" * total_user), F("email")), username=Concat(Value("(Deleted)" * total_user), F("username")))
            UserProfile.objects.filter(user_id__in=ids).update(is_deleted=True)
            return HttpResponse(AppResponse.msg(1, "Data removed"), content_type="json")

    except Exception as e:
        logging.exception("Something went wrong")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
