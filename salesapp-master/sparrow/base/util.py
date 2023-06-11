import json
import os, ast
import math
import decimal
import collections
import requests
import datetime
from datetime import date,timedelta
from decimal import *
import urllib.request
from django.conf import settings
from django.db.models.functions import Coalesce
from base.models import AppResponse
from django.utils import timezone
from django.core.cache import cache
from base.models import SysParameter, UISettings
from django.http import HttpResponse, response
from django.db.models import Q, CharField
from accounts.models import User, MainMenu, UserProfile, UserGroup, PagePermission, GroupPermission
from collections import OrderedDict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from exception_log import manager
from django.db import connection
import logging
from accounts.models import Company
from accounts.services import CompanyService
from io import BytesIO
import xlwt


class Util(object):
    @staticmethod
    def get_permission_role(user, perms):
        permissions = {}
        for perm in perms:
            permissions[perm] = Util.has_perm(perm, user)

        return permissions

    @staticmethod
    def fulltext_str_to_words(content):
        words = set()
        # words = []
        for word in content.lower().split(" "):
            word = word.strip("'")
            if len(word) >= 2:
                words.add(word)
        return words
        # return words - Util.STOP_WORDS

    user_perm_msg = "You do not have permission to perform this action"
    sys_param_key = "sys_parameters"

    import_model_fields = {}

    import_dropdown_field = {}

    @staticmethod
    def get_clean_string(string):
        return "".join(e for e in string if e.isalnum())

    @staticmethod
    def get_public_ip_address():
        my_ip_address = json.loads(urllib.request.urlopen("http://jsonip.com").read())["ip"]
        return my_ip_address

    @staticmethod
    def get_post_data(request):
        if request.POST.get("postData"):
            json_data = json.loads(request.POST["postData"])
            data = {}
            for d in json_data:
                data[d["name"]] = d["value"]
            return data
        else:
            return request.POST

    @staticmethod
    def get_sort_column(data, default_col="id"):
        if data["order"]:
            sort_col_index = int(data["order"][0]["column"]) if data["order"] else 0
            sort_dir = data["order"][0]["dir"] if data["order"] else "desc"
            sort_col = data["columns"][sort_col_index]["data"] if data["columns"] else None
            sort_dir = sort_dir if sort_col is not None else "desc"
            sort_col = default_col if sort_col is None else sort_col
            sort_col = "-" + sort_col if sort_dir == "desc" else sort_col
            return sort_col
        else:
            return "-" + default_col

    @staticmethod
    def get_permitted_url(urls, request):
        permitted_models = request.session.get("permitted_model", False)
        permitted_urls = []
        if urls and permitted_models:
            for url in urls:
                if url[1] in permitted_models:
                    permitted_urls.append(url)
            return permitted_urls
        else:
            return urls

    @staticmethod
    def is_integer(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def decimal_to_str(request, value):
        if value != None:
            decimal_place = 4
            if request != None and "decimal_point" in request.session:
                decimal_place = int(request.session.get("decimal_point"))
            format = "%." + str(decimal_place) + "f"
            new_decimal = format % value
            return new_decimal
        else:
            return ""

    @staticmethod
    def decimal_to_float(decimal_place, value):
        try:
            format = "%." + str(decimal_place) + "f"
            new_decimal = format % value
            return round(float(new_decimal), decimal_place)
        except ValueError:
            return 0.00

    @staticmethod
    def str_to_int(value):
        try:
            return int(value)
        except ValueError:
            return 0

    @staticmethod
    def str_to_float(decimal_place, value):
        try:
            return round(float(value), decimal_place)
        except ValueError:
            return 0.00

    @staticmethod
    def rreplace(s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    @staticmethod
    def convert_unicode_dict_to_str_dict(data):
        if isinstance(data, (str, bytes)):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(Util.convert_unicode_dict_to_str_dict, data.items()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(Util.convert_unicode_dict_to_str_dict, data))
        else:
            return data

    @staticmethod
    def get_choice_key_by_value(data, value):
        for item in data:
            if str(item[1]).lower() == value.strip().lower():
                return item[0]
        return None

    @staticmethod
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
            if menu["parent_id_id"] == None:
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

    @staticmethod
    def get_hierarchy_menu_obj(menu, obj):
        if menu.parent_id == None:
            return obj
        else:
            obj.insert(0, menu.parent_id)
            return Util.get_hierarchy_menu_obj(menu.parent_id, obj)

    @staticmethod
    def get_receipt_series_ordernum(receipt, transfer_num):
        if receipt.backorder_id == None:
            return transfer_num
        else:
            transfer_num = receipt.backorder.transfer_num + "/" + transfer_num
            return Util.get_receipt_series_ordernum(receipt.backorder, transfer_num)

    @staticmethod
    def get_sys_paramter(key):
        new_sys_parameter = {
            "decimalpoint": ["3", "Default decimal point of the system"],
            "decimalpoint_grid": ["2", "To show decimal point in grid-list"],
            "email_backend": ["", "Backend system for sending an email"],
            "email_host": ["", "Gateway provider for sending an email"],
            "email_host_user": ["", "Username for sending an email"],
            "email_host_password": ["", "Password for sending an email"],
            "email_port": ["", "Port of the mail gateway"],
            "email_use_ssl": ["", "SSL setting for the email"],
            "email_from": ["", "From email address for of the email"],
            "email_bcc": ["", "BCC mail address for the mail"],
            "LAUNCHER_VIEW": ["False", "Launcher view of website"],
            "COMPANY_LOGO": ["logo1-w.png", "Set company logo."],
            "Default_role_id": [2, "Default role id for sales app if"],
            "AWS_S3_HANDLER": ["https://sparrow-bg.s3.us-east-2.amazonaws.com/", "AWS S3 bucket url", False],
            "TOKEN_EXPIRE_ON": ["1", "Token expire time in minutes."],
        }

        sys_parameters = None
        if Util.get_cache("public", Util.sys_param_key) == None:
            sys_parameters = SysParameter.objects.all()
            Util.set_cache("public", Util.sys_param_key, sys_parameters, 3600)
        else:
            sys_parameters = Util.get_cache("public", Util.sys_param_key)
        sys_param = None
        for param in sys_parameters:
            if param.para_code == key:
                sys_param = param
                break

        if sys_param == None and key in new_sys_parameter.keys():
            sys_parameter = None
            sys_parameter = SysParameter.objects.create(para_code=key, para_value=new_sys_parameter[key][0], descr=new_sys_parameter[key][1])
            Util.clear_cache("public", Util.sys_param_key)
            sys_parameters = SysParameter.objects.all()
            Util.set_cache("public", Util.sys_param_key, sys_parameters, 3600)
            sys_param = sys_parameter
        return sys_param

    @staticmethod
    def set_cache(schemas, key, value, time=3600):
        schemas_key = schemas + key
        cache.set(schemas_key, value, time)

    @staticmethod
    def get_cache(schemas, key):
        schemas_key = schemas + key
        if schemas_key in cache:
            return cache.get(schemas_key)
        return None

    @staticmethod
    def clear_cache(schemas, key):
        schemas_key = schemas + key
        if schemas_key in cache:
            cache.delete(schemas_key)

    @staticmethod
    def get_main_parent_menu(perm_menu_ids):
        parent_menus = None
        if Util.get_cache("public", "main_parent_menu") is None:
            parent_menus = MainMenu.objects.filter(parent_id__isnull=True, is_active=True).order_by("sequence")
            Util.set_cache("public", "main_parent_menu", parent_menus, 3600)
        else:
            parent_menus = Util.get_cache("public", "main_parent_menu")
        permitted_menus = []
        for menu in parent_menus:
            for perm in perm_menu_ids:
                if perm.parent_id.id == menu.id:
                    permitted_menus.append(menu)
                    break
        return permitted_menus

    @staticmethod
    def get_main_child_menu(username, perm_menu_str):
        user = User.objects.filter(username=username).first()
        user_profile = UserProfile.objects.filter(user_id=user.id).first()

        child_menus = None
        if Util.get_cache("public", "get_main_child_menu") is None:
            child_menus = (
                MainMenu.objects.filter(is_active=True, is_external=False)
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
            if user.is_superuser == False:
                perms = [int(x) for x in perm_menu_str.split(",")]

            for menu in child_menus:
                if menu["id"] in perms or user.is_superuser:
                    permitted_menus.append(menu)
        return permitted_menus

    @staticmethod
    def get_resource_path(resource, resource_name):
        resource_path = os.path.join(settings.RESOURCES_ROOT, "public", "resources")
        if resource == "profile":
            resource_path = os.path.join(resource_path, "profile_image")

        if resource_name:
            resource_path = os.path.join(resource_path, resource_name)

        return resource_path

    @staticmethod
    def get_resource_url(resource, resource_name):
        resource_url = settings.RESOURCES_URL + "public" + "/resources/"

        if resource == "profile":
            resource_url += "profile_image/"
        resource_url += resource_name
        return resource_url

    @staticmethod
    def export_to_xls(headers, records, file_name):
        f = BytesIO()
        try:
            wb = xlwt.Workbook()
            ws = wb.add_sheet("Customers")

            for col_index, value in enumerate(headers):
                ws.write(0, col_index, value["title"])

            row_number = 1
            for record in records:
                for col_index, (key, value) in enumerate(record.items()):
                    if "type" in headers[col_index]:
                        if headers[col_index]["type"] == "date":
                            value = Util.get_display_date(value)

                    ws.write(row_number, col_index, value)
                row_number = row_number + 1

            wb.save(f)

            response = HttpResponse(content_type="application/ms-excel")
            response["Content-Disposition"] = "attachment; filename=%s" % file_name
            wb.save(response)
            return response
        finally:
            f.close()

    @staticmethod
    def get_local_time_obj(utctime):
        if Util.get_cache("public", "local_datetime") is None:
            company = CompanyService.get_root_compnay()
            offset = company["timezone_offset"] if company["timezone_offset"] != None else 0
            Util.set_cache("public", "local_datetime", offset, 3600)
        else:
            offset = Util.get_cache("public", "local_datetime")

        if utctime == "" or utctime == None:
            return ""
        if offset == 0:
            new_time = utctime
        else:
            new_time = utctime + datetime.timedelta(minutes=offset)

        return new_time

    @staticmethod
    def get_offset_info():
        if Util.get_cache("public", "offset_info") is None:
            company = CompanyService.get_root_compnay()
            today = date.today()
            offset_info = {
                "offset": company["timezone_offset"] if company["timezone_offset"] != None else 0,
                "daylight_offset": company["daylight_offset"] if company["daylight_offset"] != None else 0,
                "daylight_start": datetime.datetime.strptime(company["daylight_start"], "%d-%m").date().replace(year=today.year)
                if company["daylight_start"] not in [None, ""]
                else "",
                "daylight_end": datetime.datetime.strptime(company["daylight_end"], "%d-%m").date().replace(year=today.year) if company["daylight_end"] not in [None, ""] else "",
            }

            Util.set_cache("public", "offset_info", offset_info, 3600)
        else:
            offset_info = Util.get_cache("public", "offset_info")

        return offset_info

    @staticmethod
    def get_display_date(utctime, showtime=False, date_format=None):
        if utctime is None or utctime == "":
            return ""

        if type(utctime) == str:
            utctime = datetime.datetime.strptime(utctime, "%Y-%m-%dT%H:%M:%S")

        if date_format == None:
            date_format = "%d/%m/%Y"

        if showtime:
            date_format = "%d/%m/%Y %H:%M %p"

        return utctime.strftime(date_format)

    @staticmethod
    def get_local_time(utctime, showtime=False, time_format=None):
        offset_info = Util.get_offset_info()

        if utctime == "" or utctime == None:
            return ""
        # Add extra offset in daylight saving period
        if (
            offset_info["daylight_start"] != ""
            and offset_info["daylight_end"] != ""
            and offset_info["daylight_start"] < utctime.date()
            and utctime.date() < offset_info["daylight_end"]
        ):
            utctime = utctime + datetime.timedelta(minutes=offset_info["daylight_offset"])

        if offset_info["offset"] == 0:
            new_time = utctime
        else:
            new_time = utctime + datetime.timedelta(minutes=offset_info["offset"])

        if showtime:
            if time_format == None:
                time_format = "%d/%m/%Y %H:%M"
            return new_time.strftime(time_format)
        else:
            return new_time.strftime("%d/%m/%Y")

    @staticmethod
    def get_utc_datetime(local_datetime, has_time=True):
        offset_info = Util.get_offset_info()

        local_date = local_datetime
        if isinstance(local_datetime, (str, bytes)):
            local_datetime = local_datetime.replace("-", "/").replace("\\", "/")
            today = datetime.datetime.today()
            if len(local_datetime.split("/")) == 2:
                local_datetime = str(local_datetime) + "/" + str(today.year)
            if ":" in str(local_datetime):
                has_time = True
            if has_time:
                local_date = datetime.datetime.strptime(local_datetime, "%d/%m/%Y %H:%M")
            else:
                local_date = datetime.datetime.strptime(local_datetime, "%d/%m/%Y")
        # Substract extra offset in daylight saving period
        if (
            offset_info["daylight_start"] != ""
            and offset_info["daylight_end"] != ""
            and offset_info["daylight_start"] < local_date.date()
            and local_date.date() < offset_info["daylight_end"]
        ):
            local_date = local_date - datetime.timedelta(minutes=offset_info["daylight_offset"])

        utc_datetime = local_date - datetime.timedelta(minutes=offset_info["offset"])
        return utc_datetime

    @staticmethod
    def get_ui_settings(user_id):
        col_settings = []
        if Util.get_cache("public", "columns_ui_settings" + str(user_id)) is None:
            col_settings = UISettings.objects.filter(user_id=user_id).values("url", "table_index", "col_settings")
            Util.set_cache("public", "columns_ui_settings" + str(user_id), col_settings, 3600)
        else:
            col_settings = Util.get_cache("public", "columns_ui_settings" + str(user_id))

        return col_settings

    @staticmethod
    def get_user_permissions(user_id):
        groups = UserGroup.objects.filter(user_id=user_id).values_list("group_id", flat=True)
        menu_perm_ids = []

        for group_id in groups:
            if Util.get_cache("public", "ROLES" + str(group_id)) is None:
                menu_perms = GroupPermission.objects.filter(group_id=group_id).values("page_permission__menu_id", "page_permission__menu__menu_code", "page_permission__act_code")
                Util.set_cache("public", "ROLES" + str(group_id), menu_perms, 3600)
            else:
                menu_perms = Util.get_cache("public", "ROLES" + str(group_id))
            menu_perm_ids += menu_perms
        return menu_perm_ids

    @staticmethod
    def has_perm(act_code, user):
        has_permission = False
        if user.is_superuser == True:
            has_permission = True

        user_perms_objs = Util.get_user_permissions(user.id)

        for user_perms_obj in user_perms_objs:
            if user_perms_obj["page_permission__act_code"] == act_code:
                has_permission = True
                break

        return has_permission

    @staticmethod
    def listing_has_perm(menu_code, user):
        has_permission = False
        if user.is_superuser == True:
            return True

        user_perms_objs = Util.get_user_permissions(user.id)

        for user_perms_obj in user_perms_objs:
            if user_perms_obj["page_permission__act_code"] == "view" and user_perms_obj["page_permission__menu__menu_code"] == menu_code:
                has_permission = True
                break

        return has_permission

    @staticmethod
    def get_permitted_menu(user_id):
        menu_ids = []

        user_perms_objs = Util.get_user_permissions(user_id)
        for user_perms_obj in user_perms_objs:
            if user_perms_obj["page_permission__act_code"] == "view":
                menu_ids.append(user_perms_obj["page_permission__menu_id"])

        child_menus = MainMenu.objects.filter(parent_id_id__in=menu_ids).values_list("id", flat=True)
        menu_ids += child_menus
        sub_parent_menus = MainMenu.objects.filter(id__in=menu_ids, parent_id_id__isnull=False).values_list("parent_id_id", flat=True).distinct()
        menu_ids += sub_parent_menus
        return ",".join(map(str, menu_ids))

    @staticmethod
    def get_key(key):
        try:
            if key == None:
                return 0
            return float(key)
        except ValueError:
            return key

    @staticmethod
    def get_human_readable_time(minutes):
        time = ""
        cal_hrs = int(minutes / 60)
        days = int(cal_hrs / 24)
        hrs = cal_hrs - days * 24
        mins = int(minutes - (cal_hrs * 60))
        sec = minutes * 60

        if days != 0:
            days = "%02d" % (days)
            time += str(days) + " days "
        if hrs != 0:
            spent_hours = "%02d" % (hrs)
            time += str(spent_hours) + " hrs "
        if mins != 0:
            mins = "%02d" % round(mins)
            time += str(mins) + " mins "
        if sec != 0 and hrs == 0 and mins == 0:
            sec = "%02d" % round(sec)
            time += str(sec) + " sec "
        return time

    @staticmethod
    def get_ec_py_token(token=None):
        token = None
        if Util.get_cache("public", "ec_py_token") is None:
            payload = {
                'username': 'apitest',
                'password': 'ispl123;',
            }
            token_url = settings.EC_PY_URL + "/ecpy/token"
            token = requests.post(token_url, data=payload, timeout=5).json()
            Util.set_cache("public", "ec_py_token", token, 1500)
        else:
            token = Util.get_cache("public", "ec_py_token")
        return token
