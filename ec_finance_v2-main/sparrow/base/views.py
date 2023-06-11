import ast
import datetime
import json
import logging

from urllib.request import urlopen
from accounts import users_view
from accounts.models import MainMenu, User, UserGroup, UserProfile
from accounts.services import UserService
from attachment.views import upload_and_save_impersonate
from auditlog import views as log_views
from auditlog.models import AuditAction
from base.forms import CurrencyRateForm, SysParameterForm
from base.models import (AppResponse, CommentType, CurrencyRate, FavoriteView,
                         Remark, Remark_Attachment, SysParameter, UISettings)
from base.util import Util
from django.conf import settings as project_settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.clickjacking import xframe_options_exempt
from exception_log import manager
from mails.views import send_email_by_tmpl, send_sms
from messaging.models import (Notification, NotificationEvent,
                              SubscribeNotification)
from stronghold.decorators import public
import base64
from .backend import EmailAuthBackend
import requests
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from task.models import Message
from django.http import HttpResponseRedirect



@public
def robots(request):
    return render(request, "base/robots.txt", content_type="text/plain")


def get_currency_rate(currency_id):
    currency_rate = CurrencyRate.objects.filter(currency_id=currency_id).order_by("-id")[:1]
    if len(currency_rate) == 0:
        raise ValueError("Currency rate is not defined.")

    return currency_rate[0]


def clear_cache(request):
    Util.clear_cache("public", "get_main_child_menu")
    return HttpResponse(AppResponse.msg(1, "Cache cleard."), content_type="json")


def index(request):
    permissions = ''
    if "username" not in request.session:
        return redirect("/accounts/signin/")
    user_perms = User.objects.get(id=request.user.id)
    perms = ["can_view_message", "can_view_bug_report"]
    permissions = Util.get_permission_role(user_perms, perms)
    username = request.session["username"]
    user_email_ = user_perms.email
    sample_string_bytes = user_email_.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    user_email = base64_bytes.decode("ascii")
    user_full_name = User.objects.filter(id=request.user.id).values("first_name", "last_name")
    profile_name = user_full_name[0]["first_name"][0:1]+user_full_name[0]["last_name"][0:1]
    user_full_name = request.session["display_name"]
    profile_image = request.session.get("profile_image", False)
    mob_mode = request.session["mob_mode"] if "mob_mode" in request.session else ""
    check_expiration = Util.get_sys_paramter("CHECK_CURRENCY_EXPIRATION")
    if check_expiration.para_value == "True":
        currency_rates = check_currency_expiration()
        if currency_rates:
            return render(
                request,
                "accounts/exchangerate.html",
                {"currencyrates": currency_rates, "base_currency": request.session["base_currency"]},
            )

    theme_info = UserService.get_theme_info(request.session.get("color_scheme", None))
    user = UserProfile.objects.filter(user_id=request.user.id).values("menu_launcher").first()
    bg_image = request.session["bg_image"]
    user_role = UserGroup.objects.filter(user=request.user).values("user_id", "group__name").first()
    is_engineer = False
    if user_role:
        if user_role["group__name"] in ["Engineer", "Engineer_A"]:
            is_engineer = True
    is_leader = False
    if user_role:
        if user_role["group__name"] in ["Leader", "Admin", "Group Leader"]:
            is_leader = True
    perm_menu_str = users_view.get_permitted_menu(request.user.id, request.user.is_superuser)

    vertical_menu = []
    horizontal_menu = []
    horizontal_launcher = False

    if str(mob_mode) == "True":
        user["menu_launcher"] = True

    if user["menu_launcher"] is True:
        horizontal_menu = horizontal_menu_context(username, perm_menu_str)
        horizontal_launcher = True
    else:
        vertical_menu = vertical_menu_context(username, perm_menu_str, False)
    favoriteViews = FavoriteView.objects.filter(created_by_id=request.user.id)
    context = {"websocket_endpoint": ""}
    if Util.get_sys_paramter("app_eda").para_value:
        context["app_eda"] = Util.get_sys_paramter("app_eda").para_value
    context["username"] = username
    context["userid"] = request.session["userid"]
    context["user_full_name"] = user_full_name
    context["profile_image"] = Util.get_resource_url("profile", str(profile_image)) if profile_image else ""
    context["admin"] = request.user.is_superuser
    context["bg_color"] = theme_info["bg_color"]
    context["button_color"] = theme_info["button_color"]
    context["link_color"] = theme_info["link_color"]
    context["bg_image"] = None if bg_image == "" else bg_image
    context["bg_image_url"] = project_settings.AWS_S3_HANDLER + str(bg_image) if bg_image is not None else None
    context["is_white_bg_image"] = True if bg_image and "w" in bg_image else False
    context["favoriteViews"] = favoriteViews
    context["menu_context"] = horizontal_menu
    context["vertical_menu"] = vertical_menu
    context["launcher"] = horizontal_launcher
    context["row_color"] = theme_info["row_color"] if "row_color" in theme_info else "#FFFFCC"
    context["profile_name"] = profile_name
    context["permissions"] = permissions
    context["user_email"] = user_email
    context["CLICKUPAPI"] = project_settings.CLICK_UP_API
    context["is_leader"] = is_leader
    context["is_engineer"] = is_engineer
    return render(request, "base/index.html", context)


def dashboard(request):
    context = {"menus": []}
    perm_menu_str = users_view.get_permitted_menu(request.user.id, request.user.is_superuser)
    if perm_menu_str == "":
        return render(request, "base/dashboard.html", context)

    permitted_ids = perm_menu_str.split(",")
    child_menus = (
        MainMenu.objects.filter(launcher_menu=True, id__in=permitted_ids)
        .exclude(name__in=["Manufacturing orders", "Purchase plans"])
        .values("id", "name", "parent_id_id", "parent_id__name", "icon", "parent_id__parent_id__name", "url", "menu_code", "is_master", "launcher_add_url")
        .order_by("launcher_sequence")
    )
    for menu in child_menus:
        title = (
            menu["parent_id__parent_id__name"] + " - " + menu["parent_id__name"]
            if menu["parent_id__parent_id__name"] is not None
            else menu["parent_id__name"] + " - " + menu["name"]
        )
        menu["title"] = title
    context["menus"] = child_menus
    return render(request, "base/dashboard.html", context)


def check_currency_expiration():

    currency_rate_ids = CurrencyRate.objects.exclude(currency__is_base=True).values_list("id", flat=True).distinct("currency_id").order_by("currency_id", "-id")
    currency_rates = CurrencyRate.objects.filter(id__in=currency_rate_ids, expire_date__lt=datetime.datetime.utcnow())
    return currency_rates


def add_exchange_rate(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_add_exchange_rate", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        data = json.loads(request.POST["data"])
        exchange_ids = data[-2]["ids"]
        currency_ids = data[-1]["c_ids"]
        currency_rate_ids = []
        timezone = request.session["timezone"]
        for index in range(len(exchange_ids)):
            exchange_rate = data[index]["exchange_rate"]
            expire_on = Util.get_utc_datetime(data[index]["expire_on"], True, timezone)
            currency_rate = CurrencyRate.objects.create(
                currency_id=currency_ids[index], factor=exchange_rate, expire_date=expire_on, reference_date=datetime.datetime.utcnow(), created_by_id=request.user.id
            )
            currency_rate_ids.append(currency_rate.id)
        log_views.insert("base", "currencyrate", currency_rate_ids, AuditAction.INSERT, request.user.id, get_client_ip(request), "Currency rate added.")
        return HttpResponse(AppResponse.msg(1, "Data saved."), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def horizontal_menu_context(username, perm_menu_str):
    all_menu = []
    child_menu = []
    user = User.objects.get(username=username)
    if user.is_superuser is True:
        perm_menu_ids = MainMenu.objects.filter(parent_id_id__isnull=False).values_list("id", flat=True)
    else:
        perm_menu_ids = [int(x) for x in perm_menu_str.split(",")]
    parent_menus = (
        MainMenu.objects.filter(parent_id_id__isnull=True, is_active=True, is_external=False)
        .values("id", "name", "parent_id_id", "icon", "url", "menu_code", "is_master")
        .order_by("sequence")
    )

    def add_menu(menu_id, all_menus):
        menus = (
            MainMenu.objects.filter(id__in=perm_menu_ids, parent_id_id=menu_id, is_active=True, is_external=False)
            .values("id", "name", "parent_id_id", "url", "is_master")
            .order_by("sequence")
        )
        for menu in menus:
            sub_parent_menus = (
                MainMenu.objects.filter(parent_id_id=menu["id"], is_active=True, is_external=False).values("id", "name", "parent_id_id", "url", "is_master").order_by("sequence")
            )
            if len(sub_parent_menus) > 0:
                for sub_parent_menu in sub_parent_menus:
                    menu_name = menu["name"] + " - " + sub_parent_menu["name"]
                    all_menus.append(
                        {
                            "id": sub_parent_menu["id"],
                            "name": menu_name,
                            "parent_id_id": menu["parent_id_id"],
                            "url": sub_parent_menu["url"],
                            "is_master": sub_parent_menu["is_master"],
                        }
                    )
            else:
                all_menus.append({"id": menu["id"], "name": menu["name"], "parent_id_id": menu["parent_id_id"], "url": menu["url"], "is_master": menu["is_master"]})
        return all_menus

    for parent_menu in parent_menus:
        menus = MainMenu.objects.filter(parent_id_id=parent_menu["id"]).order_by("sequence")
        if len(menus) > 0:
            child_menu = add_menu(parent_menu["id"], [])
        else:
            child_menu = []
        all_menu.append(
            {
                "id": parent_menu["id"],
                "name": parent_menu["name"],
                "parent_id_id": parent_menu["parent_id_id"],
                "url": parent_menu["url"],
                "icon": parent_menu["icon"],
                "menu_code": parent_menu["menu_code"],
                "child_menus": child_menu,
            }
        )
    return all_menu


def get_main_child_menu(username, perm_menu_str):
    # Hide EDA menu if it's disable
    app_eda = True if Util.get_sys_paramter("app_eda").para_value == "True" else False
    show_aproval_menu = True if Util.get_sys_paramter("quotation_approval").para_value.lower() == "true" else False

    # Hide production menu if it's disable
    app_production = True if Util.get_sys_paramter("app_production").para_value == "True" else False

    # Hide To be approved menu if it's disable
    quotation_approval = Util.get_sys_paramter("quotation_approval")
    to_be_approved_menu = MainMenu.objects.filter(name__icontains="To be approved").first()
    supplier_user = MainMenu.objects.filter(name__icontains="Supplier users").first()
    company_code_val = Util.get_sys_paramter("company_code")
    ecommerce_app = Util.get_sys_paramter("app_ecommerce").para_value

    user = User.objects.filter(username=username).first()
    user_profile = UserProfile.objects.filter(user_id=user.id).first()

    child_menus = None
    if Util.get_cache("public", "get_main_child_menu") is None:
        child_menus = (
            MainMenu.objects.filter(is_active=True, is_external=False, parent_id__is_active=True)
            .values("id", "url", "company_code", "name", "parent_id_id", "icon", "sequence", "on_click", "menu_code", "is_master")
            .exclude(parent_id__isnull=True)
            .order_by("sequence")
        )
        Util.set_cache("public", "get_main_child_menu", child_menus, 3600)
    else:
        child_menus = Util.get_cache("public", "get_main_child_menu")

    permitted_menus = []
    if perm_menu_str != "" or user.is_superuser:
        perms = []
        if user.is_superuser is False:
            perms = [int(x) for x in perm_menu_str.split(",")]
        for menu in child_menus:
            if menu["id"] in perms or user.is_superuser:
                if "#/eda/" in menu["url"] and app_eda is False:
                    continue
                if menu["menu_code"] == "approval_rules" and not show_aproval_menu:
                    continue
                if "#/production/" in menu["url"] and app_production is False:
                    continue
                if to_be_approved_menu is not None and menu["id"] == to_be_approved_menu.id and quotation_approval.para_value.lower() != "true":
                    continue
                if supplier_user is not None and menu["id"] == supplier_user.id and user_profile.user_type == 1 and ecommerce_app.lower() != "true":
                    continue
                if menu["company_code"] is not None:
                    if company_code_val.para_value.isdigit() and int(company_code_val.para_value) != menu["company_code"]:
                        continue
                    if not company_code_val.para_value.isdigit():
                        continue
                permitted_menus.append(menu)
    return permitted_menus


def vertical_menu_context(username, perm_menu_str, exculde_menu):
    child_menus = get_main_child_menu(username, perm_menu_str)
    query = Q()
    query.add(Q(parent_id_id__isnull=True, is_active=True), query.connector)
    user = User.objects.filter(username=username).first()
    if user.is_superuser is False:
        if perm_menu_str != "":
            perm_menu_ids = [int(x) for x in perm_menu_str.split(",")]
        else:
            perm_menu_ids = []
        query.add(Q(id__in=perm_menu_ids, is_active=True), query.connector)

    parent_menu = (
        MainMenu.objects.filter(query)
        .values("id", "url", "company_code", "name", "parent_id_id", "icon", "sequence", "on_click", "is_active", "is_external", "menu_code", "is_master")
        .order_by("sequence")
    )

    def get_menu_obj(obj, exclude_menu=False):
        all_items = []

        ExcludeMenuCode = [
            "customer_invoices_cancelled",
            "customer_invoices_closed",
            "customer_invoices_pending",
            "financial_out_cancel",
            "financial_out_closed",
            "supplier_invoices_pending",
            "sales_orders_cancelled",
            "sales_orders_pending",
            "sales_orders_shipped",
            "purchase_orders_cancelled",
            "purchase_orders_received",
            "purchase_orders_pending",
            "purchase_plans_pending",
            "purchase_plans_finished",
            "mo_pending",
            "mo_finished",
            "mo_cancelled",
            "logistics_shipments_cancelled",
            "logistics_receipts_cancelled",
            "logistics_shipments_pending",
            "logistics_receipts_pending",
            "logistics_shipments_shipped",
            "logistics_receipts_received",
        ]

        def add_menu(menu):
            if menu["parent_id_id"] is None:
                menu["parent_id_id"] = 0
            menu_data = {
                "id": menu["id"],
                "name": menu["name"],
                "parent_id_id": menu["parent_id_id"],
                "url": menu["url"],
                "icon": menu["icon"],
                "sequence": menu["sequence"],
                "on_click": menu["on_click"],
                "menu_code": menu["menu_code"],
                "is_master": menu["is_master"],
                menu["id"]: [],
            }
            all_items.append(menu_data)

        def append_child(item):
            for i, parent in enumerate(all_items):
                if item["parent_id_id"] in parent:
                    obj = all_items[i][item["parent_id_id"]]
                    obj.append(item)
                    obj = sorted(obj, key=lambda x: x["sequence"])
                    all_items[i][item["parent_id_id"]] = obj
                    all_items.remove(item)

        for menus in obj:
            for menu in menus:
                if exclude_menu and menu["menu_code"] in ExcludeMenuCode:
                    continue
                add_menu(menu)

        all_items = sorted(all_items, key=lambda x: x["parent_id_id"])
        for item in all_items[::-1]:
            append_child(item)
        return all_items

    hierarchy_menu_list = get_menu_obj([parent_menu, child_menus], exculde_menu)
    return json.dumps(hierarchy_menu_list)


@xframe_options_exempt
def iframe_index(request):
    if "username" not in request.session and "client_user" not in request.session:
        return redirect("/accounts/signin/")

    color_scheme = request.session.get("color_scheme", False)
    color_scheme = color_scheme if color_scheme else ""
    color_scheme_data = {}
    if color_scheme:
        for param in color_scheme.split(","):
            scheme_data = param.split(":")
            if scheme_data != "":
                color_scheme_data[scheme_data[0].strip()] = scheme_data[1].strip()

    button_color = color_scheme_data["button_color"] if color_scheme else "#337ab7"
    link_color = color_scheme_data["link_color"] if color_scheme else "#266EBB"

    context = {}
    context["button_color"] = button_color
    context["link_color"] = link_color
    context["client_user"] = True if "client_user" in request.session and request.session["client_user"] else False
    context["row_color"] = color_scheme_data["row_color"] if "row_color" in color_scheme_data else "#FFFFCC"

    return render(request, "base/iframe_index.html", context)


@public
@xframe_options_exempt
def open_iframe_index(request):
    return render(request, "base/open_iframe_index.html", {})


def getCurrentUser(request):
    user = User.objects.get(id=request.session["userid"])
    return user


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].split(":")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_public_ip_address():
    my_ip_address = json.loads(urlopen('http://jsonip.com').read())['ip']
    return my_ip_address


def get_ui_settings(user_id):
    col_settings = []
    if Util.get_cache("public", "columns_ui_settings" + str(user_id)) is None:
        col_settings = UISettings.objects.filter(user_id=user_id).values("url", "table_index", "col_settings")
        Util.set_cache("public", "columns_ui_settings" + str(user_id), col_settings, 3600)
    else:
        col_settings = Util.get_cache("public", "columns_ui_settings" + str(user_id))

    return col_settings


@public
def get_app_data(request):
    try:
        display_row = 10
        decimal_point = 4
        user_col_settings = []
        user_email = ""
        if "username" in request.session:
            user_email = request.session["username"] if "client_user" not in request.session else request.session["client_username"]
        company_code = Util.get_sys_paramter("company_code").para_value
        theme_info = UserService.get_theme_info(request.session.get("color_scheme", None))

        if "userid" in request.session:
            decimal_point = Util.get_sys_paramter("decimalpoint").para_value
            user_profile_obj = UserProfile.objects.filter(user_id=request.session["userid"]).values("display_row").first()
            display_row = user_profile_obj["display_row"] if user_profile_obj["display_row"] else 10
            user_col_settings = get_ui_settings(request.session["userid"])
        return HttpResponse(
            json.dumps(
                {
                    "button_color": theme_info["button_color"],
                    "user_col_settings": list(user_col_settings),
                    "decimal_point": decimal_point,
                    "display_row": display_row,
                    "row_color": theme_info["row_color"],
                    "company_code": company_code,
                    "user_name": user_email,
                }
            ),
            content_type="json",
        )
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @check_view_permission([{"admin_tools": "system_parameters"}])
def sysparameters(request):
    try:
        return render(request, "base/sysparameters.html")
    except Exception as e:
        logging.exception("Something went wrong!")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def sysparameter_search(request, q=None):
    request.POST = Util.get_post_data(request)
    start = int(request.POST["start"])
    length = int(request.POST["length"])
    sort_col = Util.get_sort_column(request.POST)

    query = Q()

    if request.POST.get("para_code__icontains") is not None:
        query.add(Q(para_code__icontains=str(request.POST.get("para_code__icontains"))), query.connector)
    if request.POST.get("descr__icontains") is not None:
        query.add(Q(descr__icontains=str(request.POST.get("descr__icontains"))), query.connector)
    if request.POST.get("para_value__icontains") is not None:
        query.add(Q(para_value__icontains=str(request.POST.get("para_value__icontains"))), query.connector)
    if request.POST.get("para_group__icontains") is not None:
        query.add(Q(para_group__icontains=str(request.POST.get("para_group__icontains"))), query.connector)
    if q is not None:
        query.add(Q(type__in=[q]), query.connector)

    if not request.user.is_superuser:
        query.add(Q(for_system=False), query.connector)

    recordsTotal = SysParameter.objects.filter(query).count()
    sysparameters = SysParameter.objects.filter(query).order_by(sort_col)[start : (start + length)]

    response = {"draw": request.POST["draw"], "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": []}

    for sysparameter in sysparameters:
        response["data"].append(
            {"id": sysparameter.id, "para_code": sysparameter.para_code, "descr": sysparameter.descr, "para_value": sysparameter.para_value, "para_group": sysparameter.para_group}
        )

    return HttpResponse(AppResponse.get(response), content_type="json")


# @user_passes_test(lambda u: u.is_staff, login_url='/accounts/signin/')
# @user_passes_test(lambda u: u.has_perm("base.add_sysparameter"), login_url="/accounts/signin/")
def sysparameter(request, sysparameterid=None):
    try:
        with transaction.atomic():
            if request.method == "POST":
                form = None
                action = AuditAction.UPDATE
                id_fv = request.POST.get("id")
                user_id = request.user.id
                user = User.objects.get(id=user_id)

                if id_fv is None or (Util.is_integer(id_fv) and int(id_fv) in [0, -1]):
                    action = AuditAction.INSERT
                    if Util.has_perm("can_add_system_parameters", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    form = SysParameterForm(request.POST)
                else:
                    if Util.has_perm("can_update_system_parameters", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    sysparameter = SysParameter.objects.get(id=int(id_fv))
                    form = SysParameterForm(request.POST, instance=sysparameter)

                if form.is_valid():
                    sysparameter = form.save()
                    Util.clear_cache("public", Util.sys_param_key)
                    if action == AuditAction.INSERT:
                        return HttpResponse(json.dumps({"code": 1, "msg": "System parameter saved.", "id": sysparameter.id}), content_type="json")
                    else:
                        return HttpResponse(AppResponse.msg(1, "System parameter saved."), content_type="json")
                else:
                    return HttpResponse(AppResponse.msg(0, form.errors), content_type="json")
            else:
                sysparameterdata = SysParameter.objects.filter(id=sysparameterid).first()
                is_edit = True
                if sysparameterdata is None:
                    is_edit = False

                return render(request, "base/sysparameter.html", {"sysparameterdata": sysparameterdata, "is_edit": is_edit})
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def sysparameter_del(request):
    try:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        post_ids = request.POST.get("ids")
        if Util.has_perm("can_update_system_parameters", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        if not post_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")

        ids = [int(x) for x in post_ids.split(",")]

        SysParameter.objects.filter(pk__in=ids).delete()
        Util.clear_cache("public", Util.sys_param_key)
        return HttpResponse(AppResponse.msg(1, "Data removed"), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def add_page_favorite(request):
    try:
        name = request.POST.get("name")
        url = request.POST.get("url")
        url_without_domain = url.split("/#")[1]
        url_without_domain = "/b/#" + url_without_domain
        favoriteView = FavoriteView.objects.create(name=name, url=url_without_domain, created_by_id=request.user.id)
        return HttpResponse(json.dumps({"favorite_view_id": favoriteView.id, "url": url_without_domain}), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_page_favorite(request):
    try:
        url = request.POST.get("url")
        favorite_view_id = request.POST.get("favorite_view_id")
        if favorite_view_id:
            favoriteView = FavoriteView.objects.filter(id=favorite_view_id, created_by_id=request.user.id).first()
        else:
            url_without_domain = url.split("/#")[1]
            url_without_domain = "/b/#" + url_without_domain
            favoriteView = FavoriteView.objects.filter(url=url_without_domain, created_by_id=request.user.id).first()
        favorite_view_id = favoriteView.id
        favoriteView.delete()
        return HttpResponse(json.dumps({"favorite_view_id": favorite_view_id}), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def release_note(request, note_id):
#     try:
#         if note_id and note_id != "undefined":
#             company_code = Util.get_sys_paramter("company_code").para_value
#             release_note = ReleaseNotes.objects.filter(id=note_id).values("note", "version", "created_on").first()
#             response = render(
#                 request,
#                 "base/release_note.html",
#                 {"created_on": release_note["created_on"], "note": release_note["note"], "latest_version_id": release_note["version"], "company_code": company_code},
#             )
#             return response
#     except Exception as e:
# manager.create_from_exception(e)
#         logging.exception("Something went wrong.")
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @check_view_permission([{"admin_tools": "release_notes"}])
# def release_notes(request):
#     return render(request, "base/release_notes.html")


# def search_release_notes(request):
#     try:
#         query = Q()
#         request.POST = Util.get_post_data(request)
#         start = int(request.POST["start"])
#         length = int(request.POST["length"])
#         sort_col = Util.get_sort_column(request.POST)
#         recordsTotal = ReleaseNotes.objects.filter().count()
#         release_notes = ReleaseNotes.objects.filter(query).values("id", "version", "created_on").order_by(sort_col)[start : (start + length)]
#         all_notes = {"draw": request.POST["draw"], "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": []}
#         for release_note in release_notes:
#             created_on = Util.get_local_time(release_note["created_on"], True)
#             all_notes["data"].append({"id": release_note["id"], "version": release_note["version"], "created_on": created_on, "latest": "red"})
#         return HttpResponse(AppResponse.get(all_notes), content_type="json")
#     except Exception as e:
# manager.create_from_exception(e)
#         logging.exception("Something went wrong.")
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def save_release_note(request):
#     try:
#         with transaction.atomic():
#             release_version = request.POST["release_version"]
#             release_note = request.POST["release_note"]
#             release_note_id = int(request.POST["id"])
#             release_date = request.POST.get("release_date")
#             user_id = request.user.id
#             if release_date == "" and release_version == "":
#                 return HttpResponse(json.dumps({"code": 0, "msg": "Please enter release version & date"}), content_type="json")
#             if release_date == "":
#                 return HttpResponse(json.dumps({"code": 0, "msg": "Please enter release date"}), content_type="json")
#             if release_version == "":
#                 return HttpResponse(json.dumps({"code": 0, "msg": "Please enter release version"}), content_type="json")
#             if release_date is not None and release_note != "":
#                 release_date = datetime.datetime.strptime(str(request.POST.get("release_date") + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M")
#             if release_version is None or release_version == "":
#                 return HttpResponse(json.dumps({"code": 0, "msg": "Please enter release version"}), content_type="json")
#             if release_note_id == 0:
#                 if release_date == "":
#                     return HttpResponse(json.dumps({"code": 0, "msg": "Please enter release date"}), content_type="json")
#                 ReleaseNotes.objects.create(version=release_version, note=release_note, created_on=release_date, created_by_id=user_id)
#                 return HttpResponse(json.dumps({"code": 1, "msg": "Release note saved"}), content_type="json")
#             else:
#                 ReleaseNotes.objects.filter(id=release_note_id).update(version=release_version, note=release_note, created_on=release_date, created_by_id=user_id)
#                 return HttpResponse(json.dumps({"code": 1, "msg": "Release note updated"}), content_type="json")

#     except Exception as e:
# manager.create_from_exception(e)
#         logging.exception("Something went wrong.")
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def edit_release_note(request):
#     try:
#         if request.method == "POST":
#             release_note_id = request.POST["id"]
#             release_note = ReleaseNotes.objects.filter(id=release_note_id).first()
#             created_on = Util.get_local_time(release_note.created_on, False)
#             return HttpResponse(
#                 AppResponse.get({"code": 1, "created_on": created_on, "version": release_note.version, "note": release_note.note, "id": release_note.id}), content_type="json",
#             )
#     except Exception as e:
# manager.create_from_exception(e)
#         logging.exception("Something went wrong.")
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def delete_release_note(request):
#     try:
#         with transaction.atomic():
#             post_ids = request.POST.get("ids")
#             release_note_ids = [int(x) for x in post_ids.split(",")]
#             ReleaseNotes.objects.filter(id__in=release_note_ids).delete()
#             return HttpResponse(AppResponse.msg(1, "Release note(s) deleted."), content_type="json")
#     except Exception as e:
# manager.create_from_exception(e)
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def upload_release_note_media(request):
#     try:
#         ACCESS_KEY = "AKIARLZJKCXIHPT3JBX4"
#         SECRET_KEY = "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"
#         bucket = "sparrow-releasenotes"
#         s3 = boto3.client("s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
#         if request.method == "POST":
#             file = request.FILES["image"]
#             if file.name == "":
#                 return HttpResponse(json.dumps({"code": 0, "msg": "NO PIC UPLODED PLEASE TRY AGAIN"}), content_type="json")
#             if file and allowed_file(file.name):
#                 _dot = file.name.find(".")
#                 file.name = str(uuid.uuid4()) + file.name[_dot:]
#                 s3.put_object(Key=file.name, Body=file, Bucket=bucket, ACL="public-read")
#                 return HttpResponse(json.dumps({"code": 1, "filename": file.name}), content_type="json")
#     except Exception as e:
# manager.create_from_exception(e)
#         logging.exception("Something went wrong.")
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# @check_view_permission([{"admin_tools": "exchange_rate"}])
def currencyrates(request):
    return render(request, "base/currencyrates.html")


def currencyrate_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        timezone = request.session["timezone"]

        query = Q()
        if request.POST.get("currency__name__icontains") is not None:
            query.add(Q(currency__name__icontains=str(request.POST.get("currency__name__icontains"))), query.connector)
        if request.POST.get("reference_date__date") is not None:
            query.add(
                Q(
                    reference_date__range=[
                        Util.get_utc_datetime(request.POST["reference_date__date_from_date"].strip(), True, timezone),
                        Util.get_utc_datetime(request.POST["reference_date__date_to_date"].strip(), True, timezone),
                    ]
                ),
                query.connector,
            )

        if request.POST.get("expire_date__date") is not None:
            query.add(
                Q(
                    expire_date__range=[
                        Util.get_utc_datetime(request.POST["expire_date__date_from_date"].strip(), True, timezone),
                        Util.get_utc_datetime(request.POST["expire_date__date_to_date"].strip(), True, timezone),
                    ]
                ),
                query.connector,
            )

        query.add(Q(currency__is_base=False), query.connector)
        recordsTotal = CurrencyRate.objects.filter(query).count()
        currencyrates = CurrencyRate.objects.filter(query).order_by(sort_col)[start : (start + length)]
        response = {"draw": request.POST["draw"], "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": []}

        for currencyrate in currencyrates:
            reference_date = Util.get_local_time(currencyrate.reference_date, True)
            expire_date = Util.get_local_time(currencyrate.expire_date, True)
            response["data"].append(
                {
                    "id": currencyrate.id,
                    "currency": currencyrate.currency.name,
                    "factor": Util.decimal_to_str(request, currencyrate.factor),
                    "reference_date": reference_date,
                    "expire_date": expire_date,
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_currencyrate(request):
    try:
        session = request.session
        base_currency = session["base_currency"]
        currencyrateid = request.POST.get("id")
        currencyratedata = CurrencyRate.objects.filter(id=currencyrateid).first()
        return render(request, "base/currencyrate.html", {"currencyratedata": currencyratedata, "base_currency": base_currency})
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def currencyrate(request, currencyrateid=None):
    try:
        with transaction.atomic():
            c_ip = get_client_ip(request)
            currency_rate_id = request.POST.get("id")
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            timezone = request.session["timezone"]

            form = None
            action = AuditAction.UPDATE

            request.POST._mutable = True  # make the QueryDict mutable
            if request.POST["reference_date"] is not None and request.POST["reference_date"] != "":
                request.POST["reference_date"] = Util.get_utc_datetime(request.POST["reference_date"], True, timezone)
            if request.POST["expire_date"] is not None and request.POST["expire_date"] != "":
                request.POST["expire_date"] = Util.get_utc_datetime(request.POST["expire_date"], True, timezone)
            request.POST._mutable = False  # make QueryDict immutable again

            if currency_rate_id is None or (Util.is_integer(currency_rate_id) and int(currency_rate_id) in [0, -1]):
                action = AuditAction.INSERT
                if Util.has_perm("can_add_exchange_rate", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                form = CurrencyRateForm(request.POST)
                exist_currencyrate = CurrencyRate.objects.filter(currency_id=form["currency"].value(), factor=form["factor"].value(), reference_date=form["reference_date"].value())
            else:
                if Util.has_perm("can_update_exchange_rate", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                currencyrate = CurrencyRate.objects.get(id=int(currency_rate_id))
                form = CurrencyRateForm(request.POST, instance=currencyrate)
                exist_currencyrate = CurrencyRate.objects.filter(
                    currency_id=form["currency"].value(), factor=form["factor"].value(), reference_date=form["reference_date"].value()
                ).exclude(id=currencyrate.id)
            if exist_currencyrate:
                return HttpResponse(AppResponse.msg(0, "Currency having same factor on same date time."), content_type="json")
            if form.is_valid():
                currencyrate = form.save(commit=False)
                if action == AuditAction.INSERT:
                    currencyrate.created_by_id = request.user.id
                currencyrate = form.save()
                log_views.insert("base", "currencyrate", [currency_rate_id], action, request.user.id, c_ip, "Currency rate updated")
                if action == AuditAction.INSERT:
                    return HttpResponse(json.dumps({"code": 1, "msg": "Currency rate saved.", "id": currencyrate.id}), content_type="json")
                else:
                    return HttpResponse(AppResponse.msg(1, "Currency rate saved."), content_type="json")
            else:
                return HttpResponse(AppResponse.msg(0, form.errors), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def del_currencyrates(request):
    try:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        currencyrate_ids = request.POST.get("ids")
        if Util.has_perm("can_delete_exchange_rate", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        if not currencyrate_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")

        currencyrate_ids = [int(x) for x in currencyrate_ids.split(",")]
        CurrencyRate.objects.filter(id__in=currencyrate_ids).delete()
        return HttpResponse(AppResponse.msg(1, "Data removed"), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, "Cannot delete Currencyrate which is in use"), content_type="json")


def create_remark(app_name, model_name, entity_id, remark, remark_type, created_by_id, model_remark_field, remark_type_id, source_info_id, scope_id, prep_by=None, prep_on=None):
    try:
        if not remark_type_id.isdigit():
            remark_type_id = CommentType.objects.filter(code=remark_type_id).values("id", "code").first()
            remark_type_code = remark_type_id["code"]
            remark_type_id = remark_type_id["id"]
        else:
            remark_type_id = CommentType.objects.filter(id=int(remark_type_id)).values("id", "code").first()
            remark_type_code = remark_type_id["code"]
            remark_type_id = remark_type_id["id"]
        content_type = ContentType.objects.filter(app_label=app_name, model=model_name).first()
        remark = remark.replace("dt-options", "")
        prep_section = None
        if app_name == "qualityapp" and model_name == "order":
            order_status = Order.objects.filter(id=entity_id).values("order_status").first()
            if order_status and remark_type_code != "Exception_Order_Remarks":
                prep_section = order_status["order_status"]
            if remark_type_code == "Exception_Order_Remarks":
                prep_section = "exception"
        if scope_id is not None and type(scope_id) == str:
            scope_ids = scope_id.split(",")
            base_remark = None
            for scope in scope_ids:
                base_remark = Remark.objects.create(
                    entity_id=entity_id,
                    content_type_id=content_type.id,
                    remark=remark,
                    remark_type=remark_type,
                    created_by_id=created_by_id,
                    comment_type_id=remark_type_id,
                    prep_by_id=prep_by,
                    prep_on=prep_on,
                    prep_section=prep_section
                )
                # if model_remark_field is not None and model_remark_field != "":
                #     update_model_field_value(app_name, model_name, entity_id, model_remark_field)
                # notification_view.subscribe_notifications(created_by_id, model_name, 'remark', entity_id, remarks=remark)
                base_remark.save()
            return base_remark
        else:
            base_remark = Remark.objects.create(
                entity_id=entity_id,
                content_type_id=content_type.id,
                remark=remark,
                remark_type=remark_type,
                created_by_id=created_by_id,
                comment_type_id=remark_type_id,
                prep_by_id=prep_by,
                prep_on=prep_on,
                prep_section=prep_section
            )
            # if model_remark_field is not None and model_remark_field != "":
            #     update_model_field_value(app_name, model_name, entity_id, model_remark_field)
            # notification_view.subscribe_notifications(created_by_id, model_name, 'remark', entity_id, remarks=remark)
            base_remark.save()
            return base_remark

    except Exception as e:
        raise e


def create_remark_view(request):
    try:
        with transaction.atomic():
            entity_id = request.POST.get("entity_id")
            app_name = request.POST.get("app_name").lower()
            model_name = request.POST.get("model_name").lower()
            model_remark_field = request.POST.get("model_remark_field")
            remarks = request.POST.get("remark")
            mentioned_in = request.POST.get("mentioned_in")
            file_count = int(request.POST.get("fileCount"))
            c_ip = get_client_ip(request)
            remark_type = request.POST.get("remarkType")
            source_info = request.POST.get("sourceOfInfo")
            scope = request.POST.get("scope")
            prep_on = request.POST.get("prep_on")
            remark = create_remark(app_name, model_name, entity_id, remarks, "", request.user.id, model_remark_field, remark_type, source_info, scope, None, prep_on)
            create_date = request.POST.get("create_date")
            query = Q()
            if create_date:
                start_date_ = create_date.split("-")
                start_date = create_date + "-1"
                any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
                next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
                Last_date = next_month - datetime.timedelta(days=next_month.day)
                dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
                last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
                last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                query.add(
                    Q(
                        prep_on__range=[
                            datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query.connector,
                )

            mentionedUsersIds = request.POST.get("mentionedUsers")
            # TODO in EDA latest instence of models is not avilabel so it's handle for now
            if (Util.get_sys_paramter("SYSTEM").para_value).lower() != "eda":
                event = NotificationEvent.objects.filter(group="others", model__model="notification", action="remark").first()
                if mentionedUsersIds != "" and event is not None:
                    commentor_user = User.objects.get(id=request.user.id)
                    commentor_user_name = commentor_user.first_name + " " + commentor_user.last_name
                    mentionedUsers = [int(x) for x in request.POST.get("mentionedUsers").split(",")]
                    if len(mentionedUsers) > 0:
                        for user in mentionedUsers:
                            kwargs = {"user_name": User.objects.get(id=user).first_name, "comment_user_name": commentor_user_name, "mentioned_in": mentioned_in}
                            sub_notifications = SubscribeNotification.objects.filter(event_id=event.id, in_system=True, user_id=user).first()
                            if sub_notifications is not None:
                                Notification.objects.create(
                                    subject="You are mentioned in comment by " + commentor_user_name + " in the " + mentioned_in,
                                    user_id=user,
                                    type="comment_mension",
                                    entity_id=entity_id,
                                )

                            sub_notifications = SubscribeNotification.objects.filter(event_id=event.id, by_email=True, user_id=user).first()
                            if sub_notifications is not None:
                                notification_email = UserProfile.objects.get(user_id=user).notification_email
                                send_email_by_tmpl(True, "public", [notification_email], event.template_id, kwargs)

                            sub_notifications = SubscribeNotification.objects.filter(event_id=event.id, by_sms=True, user_id=user).first()
                            if sub_notifications is not None and event.sms_template is not None:
                                notification_mob = UserProfile.objects.get(user_id=user).notification_mob
                                send_sms([notification_mob], event.sms_template, kwargs)

            attachments = []
            if file_count != 0:
                for i in range(file_count):
                    attachment_ = request.FILES.get("file" + str(i))
                    attachment_name = str(attachment_)
                    attachment_data = attachment_.read()
                    if model_name == "operator":
                        operator = Operator.objects.filter(id=entity_id).values("user__username").first()
                        attachment_folder_name = operator["user__username"]
                    if model_name == "order":
                        order = Order.objects.filter(id=entity_id).values("order_number", "customer_order_nr").first()
                        attachment_folder_name = order["customer_order_nr"]
                    attachment = upload_and_save_impersonate(attachment_data, "base", "Remark_Attachment", remark.id, request.user.id, c_ip, "REMARK", attachment_name, attachment_folder_name, "")
                    attachments.append(attachment)
            response = {"code": 1, "data": []}

            remarks = Remark.objects.filter(query, entity_id=int(entity_id), content_type=remark.content_type.id).order_by("-id")
            for remark in remarks:
                remark_attach = Remark_Attachment.objects.filter(object_id=remark.id, deleted=False)
                remark_obj = get_remark_obj(remark, remark_attach)
                response["data"].append(remark_obj)
            return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_remarks(request):
    try:
        entity_id = request.POST.get("entity_id")
        app_name = request.POST.get("app_name")
        model_name = request.POST.get("model_name").lower()
        create_date = request.POST.get("create_date")
        query = Q()
        if create_date:
            start_date_ = create_date.split("-")
            start_date = create_date + "-1"
            any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
            next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
            Last_date = next_month - datetime.timedelta(days=next_month.day)
            dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
            last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
            last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            query.add(
                Q(
                    prep_on__range=[
                        datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        comment_order = Util.get_sys_paramter("COMMENT_CHRONOLOGICAL_ORDER")
        order_by_id = "id"
        if comment_order.para_value.lower() == "desc":
            order_by_id = "-id"
        content_type = ContentType.objects.filter(app_label=app_name, model=model_name).first()
        remarks = Remark.objects.filter(query, entity_id=entity_id, content_type=content_type).order_by(order_by_id)
        response = {"data": [], "count": remarks.count(), "user": request.user.id}
        # remarks = Remark.objects.filter(entity_id=entity_id, content_type=content_type).values("content_type")
        for remark in remarks:
            remark_attach = Remark_Attachment.objects.filter(object_id=remark.id, deleted=False)

            remark_obj = get_remark_obj(remark, remark_attach)
            response["data"].append(remark_obj)
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong")
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def update_model_field_value(app_name, model_name, entity_id, model_remark_field):
    if model_remark_field is not None:
        model_type = ContentType.objects.get(app_label=app_name, model=model_name)
        last_remark = Remark.objects.filter(entity_id=int(entity_id), content_type_id=model_type.id).order_by("-id").first()
        model_type.model_class().objects.filter(id=int(entity_id)).update(**{model_remark_field: last_remark.remark if last_remark is not None else ""})


def get_remark_obj(remark, remark_attach):
    try:
        attachments = []
        remark_type_id = ""
        profile = UserProfile.objects.filter(user_id=remark.created_by_id).values("profile_image").first()
        # attachment_ids = []
        for attachment in remark_attach:
            attachments.append({"attach_id": attachment.id, "uid": attachment.uid, "name": attachment.name})
        remark_type = ""
        if remark.comment_type_id != "" and remark.comment_type_id is not None:
            remarks = CommentType.objects.filter(id=remark.comment_type_id).values("id", "name").first()
            remark_type = remarks["name"]
            remark_type_id = remarks["id"]

        remark_source = ""
        # if remark.comment_source_of_info_id != "" and remark.comment_source_of_info_id is not None:
        #     remark_source_of_info = CommentSourceOfInformation.objects.filter(id=remark.comment_source_of_info_id).first()
        #     remark_source = remark_source_of_info.name

        remark_scope = ""
        # if remark.comment_scope_id != "" and remark.comment_scope_id is not None:
        #     scope = CommentScope.objects.filter(id=remark.comment_scope_id).first()
        #     remark_scope = scope.name
        response = {
            "id": remark.id,
            "entity_id": remark.entity_id,
            "remark": remark.remark if remark.remark is not None else "",
            "date": Util.get_local_time(remark.created_on, True, "%B %d, %Y %H:%M %p"),
            "user_id": remark.created_by_id,
            "content_model": remark.content_type.model,
            "remark_type": remark_type,
            "remark_type_id": remark_type_id if remark_type_id is not None else "",
            "remark_source": remark_source,
            # "remark_source_id": remark.comment_source_of_info_id if remark.comment_source_of_info_id not in ("", None) else "",
            "remark_scope": remark_scope,
            # "remark_scope_id": remark.comment_scope_id if remark.comment_scope_id not in ("", None) else "",
            "display_name": remark.created_by.first_name + " " + remark.created_by.last_name,
            "display_img": Util.get_resource_url("profile", str(profile["profile_image"])) if profile["profile_image"] else "",
            "attachments": attachments,
            "prep_on": Util.get_local_time(remark.prep_on, True, "%B, %Y"),
        }
        return response
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        # return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def check_edit_remark_perm(request):
    try:
        id = request.POST["id"]
        if id:
            remark_user = Remark.objects.filter(id=id).values("created_by_id").first()
        user = User.objects.get(id=request.user.id)
        perms = ["can_edit_remark"]
        permissions = Util.get_permission_role(user, perms)
        if permissions["can_edit_remark"] is True or remark_user["created_by_id"] == request.user.id:
            response = {"code": 1}
            return HttpResponse(AppResponse.get(response), content_type="json")
        else:
            response = {"code": 0}
            return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def edit_remark(request):
    try:
        remark = request.POST.get("remark")
        # model_name = request.POST.get("model_name").lower()
        content_model = request.POST.get("content_model")
        base_entity_id = request.POST.get("base_entity_id")
        # sourceInfoSelection = request.POST.get("sourceInfoSelection")
        # scopeInfoSelection = request.POST.get("scopeInfoSelection")
        edit_remark_type_id = request.POST.get("edit_remark_type_id")
        id = request.POST.get("id")
        Remark.objects.filter(id=id, content_type__model=content_model).update(remark=remark, comment_type=edit_remark_type_id)
        contect_id = Remark.objects.filter(id=id).values("entity_id").first()
        Order.objects.filter(id=contect_id["entity_id"]).update(remarks=remark)
        create_date = request.POST.get("create_date")
        query = Q()
        if create_date:
            start_date_ = create_date.split("-")
            start_date = create_date + "-1"
            any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
            next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
            Last_date = next_month - datetime.timedelta(days=next_month.day)
            dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
            last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
            last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            query.add(
                Q(
                    prep_on__range=[
                        datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        remarks = Remark.objects.filter(query, entity_id=base_entity_id, content_type__model=content_model).order_by("id")

        response = {"code": 1, "data": [], "count": remarks.count(), "user": request.user.id}
        for remark in remarks:
            remark_attach = Remark_Attachment.objects.filter(object_id=remark.id, deleted=False)
            remark_obj = get_remark_obj(remark, remark_attach)
            response["data"].append(remark_obj)
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_remark(request):
    try:
        remark_id = request.POST.get("remark_id")
        model_remark_field = request.POST.get("model_remark_field")
        entity_id = request.POST.get("entity_id")
        app_name = request.POST.get("app_name").lower()
        model_name = request.POST.get("model_name").lower()
        contect_id = Remark.objects.filter(id=int(remark_id)).values("entity_id").first()
        Order.objects.filter(id=contect_id["entity_id"]).update(remarks="")
        Remark.objects.filter(id=int(remark_id)).delete()
        update_model_field_value(app_name, model_name, entity_id, model_remark_field)
        return HttpResponse(AppResponse.msg(1, "Data removed"), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def check_subscription(request):
    entity_id = request.POST.get("entity_id")
    app_name = request.POST.get("app_name").lower()
    model_name = request.POST.get("model_name").lower()
    model_type = ContentType.objects.get(app_label=app_name, model=model_name)

    if SubscribeNotification.objects.filter(entity_id=int(entity_id), event__model_id=model_type.id, user_id=request.user.id).count() > 0:
        return HttpResponse(AppResponse.get({"subscription": "true"}), content_type="json")
    else:
        return HttpResponse(AppResponse.get({"subscription": "false"}), content_type="json")


def subscribe_item(request):
    try:
        entity_id = request.POST.get("entity_id")
        app_name = request.POST.get("app_name").lower()
        model_name = request.POST.get("model_name").lower()
        group_name = request.POST.get("group_name").lower()
        model_type = ContentType.objects.get(app_label=app_name, model=model_name)
        user = UserProfile.objects.filter(user_id=request.user.id).first()
        if user.notification_email is None or user.notification_email == "":
            return HttpResponse(AppResponse.msg(0, "Notification email address is not available. You can add it in your profile setting."), content_type="json")

        events = NotificationEvent.objects.filter(model_id=model_type.id, group=group_name, is_active=True)
        for event in events:
            SubscribeNotification.objects.create(event_id=event.id, user_id=request.user.id, by_email=True, in_system=True, entity_id=int(entity_id), created_by_id=request.user.id)
        return HttpResponse(AppResponse.msg(1, "Subscribed item."), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def unsubscribe_item(request):
    try:
        entity_id = request.POST.get("entity_id")
        app_name = request.POST.get("app_name").lower()
        model_name = request.POST.get("model_name").lower()
        group_name = request.POST.get("group_name").lower()
        model_type = ContentType.objects.get(app_label=app_name, model=model_name)
        events = NotificationEvent.objects.filter(model_id=model_type.id, group=group_name, is_active=True)

        SubscribeNotification.objects.filter(entity_id=int(entity_id), event_id__in=events.values_list("id", flat=True).distinct(), user_id=request.user.id).delete()
        return HttpResponse(AppResponse.msg(1, "Unsubscribed item."), content_type="json")
    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def add_variable_to_context(request):
    if request.path.startswith("/accounts/setup"):
        return {}

    base_ftr_remark = True if Util.get_sys_paramter("ftr_remark").para_value == "N9TT-9G0A-B7FQ-RANC" else False
    base_ftr_attachment = True if Util.get_sys_paramter("ftr_attachment").para_value == "QK6A-JI6S-7ETR-0A6C" else False
    base_ftr_notification = True if Util.get_sys_paramter("ftr_notification").para_value == "SXFP-CHYK-ONI6-S89U" else False
    base_ftr_task = True if Util.get_sys_paramter("ftr_task").para_value == "M66T-8A00-4RP6-93KA" else False
    base_ftr_task = True if Util.get_sys_paramter("ftr_task").para_value == "M66T-8A00-4RP6-93KA" else False

    return {
        "base_ftr_remark": base_ftr_remark,
        "base_ftr_attachment": base_ftr_attachment,
        "base_ftr_notification": base_ftr_notification,
        "base_ftr_task": base_ftr_task,
        "google_analytic_code": Util.get_sys_paramter("google_analytic_code").para_value,
    }


@transaction.atomic
def set_col_order(request):
    try:
        if request.method == "POST":
            col_settings = {}
            check_col = []
            url = request.POST["url"]
            col_order = [x for x in request.POST["colOrder"].split(",")]
            if len(request.POST["checkOrder"]) > 0:
                check_col = [x for x in request.POST["checkOrder"].split(",")]
            table_index = request.POST["tableColIndex"]
            user_id = request.user.id
            col_settings["col_order"] = col_order
            col_settings["hide_col"] = check_col

            col_order_obj = UISettings.objects.filter(url=url, table_index=table_index, user_id=user_id).first()

            if col_order_obj:
                user_col_order = json.loads(col_order_obj.col_settings)
                if col_order != user_col_order["col_order"] or check_col != user_col_order["hide_col"]:
                    col_order_obj.col_settings = json.dumps(col_settings)
                    col_order_obj.save()

            else:
                UISettings.objects.create(url=url, table_index=table_index, col_settings=json.dumps(col_settings), user_id=user_id)
            Util.clear_cache("public", "columns_ui_settings" + str(user_id))

            return HttpResponse(AppResponse.msg(1, "s"), content_type="json")

    except Exception as e:
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_all_user_list(request):
    try:
        keyword = request.POST["keyword"]
        existUsers = ast.literal_eval(request.POST["existUsers"])
        existUsers.append(request.user.id)
        query = Q()

        query.add(Q(first_name__icontains=keyword) | (Q(last_name__icontains=keyword)), query.connector)
        query.add(Q(is_active=True), query.connector)
        query.add(~Q(id__in=existUsers), query.connector)

        all_users = User.objects.filter(query, id__in=UserProfile.objects.filter(user_type=1).values_list("user_id")).values("id", "first_name", "last_name")[:10]

        response = []

        for user in all_users:
            user_name = '<span class="usr-ref" ref = "' + str(user["id"]) + '">' + user["first_name"] + " " + user["last_name"] + "</span>"
            response.append(user_name)

        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        logging.exception("hi")
        # manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def export_db_data(request):
    try:
        if request.method == "GET":
            admin_partner = Partner.objects.filter(is_hc=True).values("id").first()
            admin_user = UserProfile.objects.filter(partner_id=admin_partner["id"]).values("user_id").first()
            if request.user.id != admin_user["user_id"]:
                return HttpResponse('<h1 style="color:red;margin-top:300px;text-align:center;">Access denied - You are not authorized to access this page.</h1>')

            master_tables = [
                "accounts_mainmenu",
                "attachment_filetype",
                "auditlog_auditaction",
                "base_currency",
                "base_docnumber",
                "base_sysparameter",
                "base_dmi_queries",
                "base_appreport",
                "django_migrations",
                "django_content_type",
                "financial_invoicestatus",
                "financial_paymentdifferencetype",
                "financial_paymentmode",
                "inventory_movetype",
                "inventory_location",
                "logistics_shipmethod",
                "partners_country",
                "partners_paymentterm",
                "production_unitofcapacity",
                "products_unitofmeasure",
                "purchasing_orderstatus",
                "sales_orderstatus",
                "task_tasktype",
                "accounts_contentpermission",
                "accounts_pagepermission",
                "post_office_emailtemplate",
                "messaging_smstemplate",
                "messaging_notificationevent",
                "campaign_stage",
            ]

            context = {}
            context["contents"] = master_tables
            return render(request, "base/export_db_data.html", context)

        else:
            tables = json.loads(request.POST["tables"])
            cursor = connection.cursor()
            queries = ""
            imp_list = ["created_by_id", "created_by", "user_by_id", "user_by", "nextint"]
            only_units = ["products_unitofmeasure", "production_unitofcapacity"]
            for table in tables:
                cursor.execute("SELECT * FROM information_schema.columns WHERE table_schema = 'ec' AND table_name ='" + table + "'")
                rows = cursor.fetchall()
                column_names = []
                for row in rows:
                    if row[3] in ["desc", "group"]:
                        column_names.append('"' + row[3] + '"')
                    else:
                        column_names.append(row[3])

                cursor.execute("SELECT * FROM ec." + table)
                rows = cursor.fetchall()
                flag = 0
                for row in rows:
                    values = "("
                    col_names = "("
                    for index in range(len(row)):

                        if table in only_units:
                            if str(row[1]) == "Unit(s)":
                                if isinstance(row[index], int) or isinstance(row[index], True):
                                    flag = 1
                                    col_names += str(column_names[index]) + ","
                                    if str(column_names[index]) in imp_list:
                                        values += str(1) + ","
                                    else:
                                        values += str(row[index]) + ","
                                elif row[index] is None:
                                    flag = 1
                                    continue
                                else:
                                    flag = 1
                                    if str(column_names[index]) == "nextnum":
                                        prefix = str(row[3]) + "1".zfill(row[4])
                                        values += "'%s'" % str(prefix) + ","
                                        col_names += str(column_names[index]) + ","

                                    else:
                                        values += "'%s'" % str(row[index]) + ","
                                        col_names += str(column_names[index]) + ","

                        if table not in only_units:
                            if isinstance(row[index], int) or isinstance(row[index], bool):
                                flag = 1
                                col_names += str(column_names[index]) + ","
                                if str(column_names[index]) in imp_list:
                                    values += str(1) + ","
                                else:
                                    values += str(row[index]) + ","
                            elif row[index] is None:
                                continue
                            else:
                                flag = 1
                                if str(column_names[index]) == "nextnum":
                                    prefix = str(row[3]) + "1".zfill(row[4])
                                    values += "'%s'" % str(prefix) + ","
                                    col_names += str(column_names[index]) + ","

                                else:
                                    my_value = str(row[index]).replace("'", "''")
                                    values += "'%s'" % my_value + ","
                                    col_names += str(column_names[index]) + ","

                    if flag == 1:
                        flag = 0
                        col_names = col_names[:-1]
                        values = values[:-1]
                        values += ");\n"
                        col_names += ")"
                        query = "insert into ec." + table + col_names + " " "values" + values
                        queries += query
                queries += """SELECT setval(pg_get_serial_sequence(' ec.""" + table + """','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM ec.""" + table + """;\n"""

                queries += "\n\n"

            return HttpResponse(json.dumps(queries), content_type="json")
    except Exception as e:
        logging.exception("hi")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @check_view_permission([{"Admin_tools": "admin_settings"}])
def settings(request):
    perm_menu_str = users_view.get_permitted_menu(request.user.id, request.user.is_superuser)
    master_menu_dict = {}
    if perm_menu_str == "":
        return render(request, "base/settings.html", {"master_menus": master_menu_dict})

    perm_menu_ids = [int(x) for x in perm_menu_str.split(",")]
    master_menus = (
        MainMenu.objects.filter(is_master=True, id__in=perm_menu_ids)
        .exclude(parent_id__name__in=["Production", "CRM", "Human resources", "Others"])
        .values("name", "url", "parent_id", "menu_code", "parent_id__name")
    )
    for master_menu in master_menus:
        if master_menu["parent_id__name"] is not None:
            if master_menu["parent_id__name"] in master_menu_dict:
                master_menu_dict[master_menu["parent_id__name"]].append({"name": master_menu["name"], "url": master_menu["url"]})
            else:
                master_menu_dict[master_menu["parent_id__name"]] = [{"name": master_menu["name"], "url": master_menu["url"]}]

    return render(request, "base/settings.html", {"master_menus": master_menu_dict})


def admin_utilities(request):
    perm_menu_str = users_view.get_permitted_menu(request.user.id, request.user.is_superuser)
    master_menu_dict = {}
    if perm_menu_str == "":
        return render(request, "base/settings.html", {"master_menus": master_menu_dict})

    perm_menu_ids = [int(x) for x in perm_menu_str.split(",")]
    master_menus = (
        MainMenu.objects.filter(is_master=True)
        .exclude(parent_id__name__in=["Production", "CRM", "Human resources", "Others"])
        .values("name", "url", "parent_id", "menu_code", "parent_id__name")
    )
    for master_menu in master_menus:
        if master_menu["parent_id__name"] is not None:
            if master_menu["parent_id__name"] in master_menu_dict:
                master_menu_dict[master_menu["parent_id__name"]].append({"name": master_menu["name"], "url": master_menu["url"]})
            else:
                master_menu_dict[master_menu["parent_id__name"]] = [{"name": master_menu["name"], "url": master_menu["url"]}]

    return render(request, "base/admin_utilities.html", {"master_menus": master_menu_dict})


@public
def session_save_for_portal_login(request, api_result, user, profile):
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    permissions = True
    Util.set_cache("public", "user_permissions_" + str(user.id), permissions)
    decimal_parameter = None
    currency_parameter = None
    decimal_place = 4
    base_currency = ""
    if decimal_parameter is not None:
        decimal_place = int(decimal_parameter.para_value) if decimal_parameter.para_value is not None else 4
    if currency_parameter is not None:
        base_currency = currency_parameter.symbol
    session = request.session
    session["user_permissions_" + str(user.id)] = permissions
    session["username"] = api_result["username"].lower()
    session["userid"] = user.id
    session["ec_user_id"] = api_result["userid"] if "userid" in api_result else 0
    session["display_name"] = user.first_name + " " + user.last_name
    session["decimal_point"] = decimal_place
    session["base_currency"] = base_currency
    session["profile_image"] = str(profile.profile_image) if profile.profile_image else ""
    session["color_scheme"] = profile.color_scheme
    session["bg_image"] = profile.image_name
    session["list_display_row"] = profile.display_row
    session["two_fact_auth"] = api_result["tfaRequired"]
    session["AuthToken"] = api_result["AuthToken"]
    if profile.user_type == 2 or profile.user_type == 3:
        session["is_external"] = True
    else:
        session["is_external"] = False
    session.save()


@public
def portal_login(request):
    try:
        if request.method == "GET":
            username = request.GET.get("username")
            token = request.GET.get("token")
            portal_username = request.GET.get("portal_username")
            email_auth = EmailAuthBackend()
            user = email_auth.authenticate(username=username, token=token, portal_username=portal_username)
            if user:
                profile = UserProfile.objects.filter(user_id=user.id).first()
                api_result = {}
                api_result["username"] = user.username
                api_result["userid"] = profile.user_id if profile.user_id else 0
                api_result["tfaRequired"] = False
                api_result['AuthToken'] = token
                session_save_for_portal_login(request, api_result, user, profile)
                session = request.session
                session.save()
                url = project_settings.EC_PORTAL_DOMAIN + "set_cookie_as_per_domain/"
                requests.request("POST", url, data={"token": token, "username": portal_username, "portal_username": portal_username, "sessionid": request.session.session_key, "domain": "EC_FINANCEAPP"})
                return redirect("/#/collection/dashboard/")
            else:
                response = HttpResponseRedirect("/accounts/signin/")
                return response
        return HttpResponse("Unauthorizad access.", content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
@csrf_exempt
def portal_signout(request):
    try:
        key = request.POST.get("session_data")
        if key:
            Session.objects.filter(session_key=key).delete()
        return JsonResponse({"code": 0, "msg": "User logged out from EC Qualityapp"})
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @xframe_options_exempt
# @public
# def app_view_redirect(request):
#     try:
#         client_number = request.GET.get("number", "")
#         module = request.GET["module"]
#         client = request.GET["cust"]
#         token = request.GET["token"]
#         # username = request.GET["username"]
#         # password = request.GET["password"]
#         power_inquiry_id = request.GET.get("inq_id", 0)
#         session = request.session

#         # key = AES.new(project_settings.SCHEDULER_KEY[:32].encode("utf-8"), AES.MODE_ECB)

#         # raw_decrypted = (key.decrypt(base64.b64decode(password))).decode("utf-8")

#         # password = raw_decrypted.rstrip("\0")
#         if len(token) == 0:
#             return HttpResponse(AppResponse.msg(0, "Authentication failed.  Missing Token."), content_type="json")

#         auth_token = AuthToken.objects.filter(token=token).first()
#         user = User.objects.filter(id=auth_token.user_id).first()
#         if auth_token:
#             expire_on = auth_token.expire_on.replace(tzinfo=None)
#             current_time = datetime.datetime.utcnow()
#             if current_time > expire_on:
#                 return HttpResponse(AppResponse.msg(0, "Your session is expired."), content_type="json")

#         if "username" not in request.session:
#             if user:
#                 if user.is_active:
#                     login(request, user)
#                     session["client_username"] = user.username
#                     session["client_user"] = True
#                 else:
#                     return HttpResponse(AppResponse.msg(0, "Failed to authenticate"), content_type="json")
#             else:
#                 return HttpResponse(AppResponse.msg(0, "Failed to authenticate"), content_type="json")

#         error_msg = "Sparrow order is not found related to " + client_number

#         if module == "manage_tax":
#             user_id = request.GET["cust_username"]
#             session["custom_user_id"] = user_id
#             return HttpResponseRedirect("/b/iframe_index/#/products/taxes/")
#         if module == "product_scrap_code":
#             user_id = request.GET["cust_username"]
#             session["custom_user_id"] = user_id
#             return HttpResponseRedirect("/b/iframe_index/#/products/package_codes/")

#         if module == "sales":
#             sales_order = None
#             if client == "power":
#                 sales_order = PowerOrderAttributes.objects.filter(power_order=client_number, power_inquiry_id=power_inquiry_id).values("sales_order_id").first()
#                 if sales_order:
#                     sale_id = str(sales_order["sales_order_id"])
#             elif client == "ec":
#                 sales_order = OrderAttributes.objects.filter(ecorder=client_number).values("salesorder_id").first()
#                 if sales_order:
#                     sale_id = str(sales_order["salesorder_id"])
#             if sales_order is None:
#                 return HttpResponse(error_msg)
#             else:
#                 return HttpResponseRedirect("/b/iframe_index/#/sales/order/" + sale_id + "/0")

#         elif module == "prod":
#             mo_order = OrderAttributes.objects.filter(ecorder=client_number, mfg_order_id__isnull=False).values("mfg_order_id").first()
#             if mo_order is None:
#                 return HttpResponse(error_msg)
#             else:
#                 return HttpResponseRedirect("/b/iframe_index/#/production/mfg_order/" + str(mo_order["mfg_order_id"]) + "/")

#     except Exception as e:
#         logging.exception("Something went wrong.")
#         return HttpResponse(json.dumps({"code": 0, "msg": e}), content_type="json")


# def visualizer_redirect(request):
#     try:
#         mo_order_id = request.POST["mo_order_id"]
#         ecorder = request.POST["ecorder"]
#         title = request.POST["title"]

#         EC_WEB_DOMAIN = project_settings.EC_WEB_DOMAIN
#         url = EC_WEB_DOMAIN + "assembly/SparrowApi/GenerateToken"
#         payload = "key=516f30f0-b587-4381-abf6-8b91f06efa59-1"
#         data = requests.request("POST", url, data=payload, headers={"content-type": "application/x-www-form-urlencoded"})
#         response = json.loads(data.text)
#         token_number = response["Token"]
#         if not ecorder.endswith("-A"):
#             ecorder = ecorder + "-A"
#         source_num = OrderAttributes.objects.filter(ecorder=ecorder, mfg_order=mo_order_id).first()

#         if not source_num:
#             return HttpResponse(AppResponse.msg(0, "Order number does not exist"), content_type="json")

#         if title == "is_assembly":
#             url = EC_WEB_DOMAIN + "shop/assembly/assemblyeditor.aspx?number=" + ecorder + "&viewType=view&eccuserid=0&from=sparrow&tokenid=" + token_number
#         elif title == "is_visulizer":
#             url = EC_WEB_DOMAIN + "shop/orders/pcb_visualizer.aspx?r=" + ecorder + "&from=sparrow&tokenid=" + token_number
#         elif title == "is_remark":
#             url = EC_WEB_DOMAIN + "shop/rb/splasm.aspx?itemnumber=" + ecorder + "&mode=v&from=sparrow&token=" + token_number

#         response = {}
#         response["url"] = url
#         return HttpResponse(AppResponse.get(response), content_type="json")
#     except Exception as e:
#         logging.exception("something went wrong")
#         # manager.create_from_exception(e)
#         return HttpResponse(AppResponse.msg(0, "Something went wrong."), content_type="json")


# # @public
# def generate_token(request):
#     token_length = 10
#     token = uuid.uuid4().hex[:token_length]
#     expire_mins = Util.get_sys_paramter("TOKEN_EXPIRE_ON").para_value
#     expire_on = datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * int(expire_mins))
#     AuthToken.objects.create(user_id=request.user.id, token=token, expire_on=expire_on)
#     data = {"token": token}
#     return HttpResponse(json.dumps(data), content_type="json")


# def valid_token(token):
#     auth_token = AuthToken.objects.filter(token=token).first()
#     if auth_token:
#         expire_on = auth_token.expire_on.replace(tzinfo=None)
#         current_time = datetime.datetime.utcnow()
#         if expire_on >= current_time:
#             return True
#     return False


# def upload_wysiwyg_media(request):
#     try:
#         if request.method == "POST":
#             file = request.FILES["image"]
#             path = "public" + "/resources/WYSIWYG_images/" + "{}/{}/{}/".format(str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day))
#             resource_path = os.path.join(project_settings.RESOURCES_ROOT, path)
#             if not os.path.exists(resource_path):
#                 os.makedirs(resource_path)

#             if file.name == "":
#                 return HttpResponse(json.dumps({"code": 0, "msg": "NO PIC UPLODED PLEASE TRY AGAIN"}), content_type="json")

#             if file and allowed_file(file.name):
#                 _dot = file.name.find(".")
#                 file.name = str(uuid.uuid4()) + file.name[_dot:]
#                 # image = Image.open(file)
#                 with Image.open(file) as image:
#                     image.save(resource_path + "/" + file.name)
#                     image.close()
#                 image_path = os.path.join("/resources/", path)

#                 image_path = os.path.join(image_path, file.name)
#             else:
#                 return HttpResponse(json.dumps({"code": 0, "msg": "File type not allowed."}), content_type="json")

#             return HttpResponse(json.dumps({"code": 1, "filepath": image_path}), content_type="json")
#     except Exception as e:
#         # manager.create_from_exception(e)
#         logging.exception("Something went wrong.")
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# def delete_wysiwyg_media(request):
#     try:
#         path = request.POST.get("image")[11:]

#         image_path = os.path.join(project_settings.RESOURCES_ROOT, path)

#         if os.path.exists(image_path):
#             os.remove(image_path)
#         return HttpResponse(json.dumps({"code": 1, "data": ""}), content_type="json")
#     except Exception as e:
#         # manager.create_from_exception(e)
#         logging.exception("Something went wrong.")
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def detail_master(request):
    return render(request, "base/detail_master.html")


def import_order_view(request):
    return render(request, "base/import_order.html")


def batch_code_view(request):
    return render(request, "base/batch_code.html")
