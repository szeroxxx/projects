import base64
import collections
import datetime
import json
import logging
import math
import os
import random
import re
import ssl
import string
import urllib.request
from decimal import Decimal
from io import BytesIO

# import numpy as np
import pytz

# import redis
import requests
import xlwt
from accounts import models as accounts_model  # import GroupPermission, UserGroup

# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
from dateutil import tz
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse

from base.models import AppResponse, SysParameter

# from exception_log import manager


# from partners.models import Partner
# from products.models import ProductGroup_Form


# r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


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

    @staticmethod
    def get_clean_string(string):
        return "".join(e for e in string if e.isalnum())

    @staticmethod
    def get_generic_product_group():
        return ProductGroup_Form.objects.filter(name="Generic").first()

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
    def get_ec_py_token(token=None):
        token = None
        if Util.get_cache("public", "ec_py_token") is None:
            payload = {
                "username": settings.ECPY_USERNAME,
                "password": settings.ECPY_PASSWORD,
            }
            token_url = settings.EC_PY_URL + "/ecpy/token"
            token = requests.post(token_url, data=payload, timeout=5).json()
            Util.set_cache("public", "ec_py_token", token, 1500)
        else:
            token = Util.get_cache("public", "ec_py_token")
        return token

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

    # Post data on Client
    @staticmethod
    def post_client_data(end_point, post_data):
        try:
            post_url = Util.get_sys_paramter("CLIENT_POST_URL").para_value + end_point
            post_key = Util.get_sys_paramter("CLIENT_POST_KEY").para_value
            post_data["key"] = post_key
            req = urllib.request.Request(post_url)
            req.add_header("Content-Type", "application/json")
            context = ssl._create_unverified_context()
            return urllib.request.urlopen(req, bytes(json.dumps(post_data), encoding="utf-8"), context=context).read()
        except Exception as e:
            manager.create_from_exception(e)
            logging.exception("Something went wrong.")
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")

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
    def NoneToZero(s):
        if s is None:
            return 0

    @staticmethod
    def decimal_to_str(request, value, decimal_precesion=3):
        if value is None or value == "":
            return ""

        if request is not None and "decimal_point" in request.session:
            decimal_precesion = int(request.session.get("decimal_point"))
        format = "%." + str(decimal_precesion) + "f"
        new_decimal = format % value
        return new_decimal

    @staticmethod
    def decimal_to_float(decimal_place, obj):
        try:
            format = "%." + str(decimal_place) + "f"
            new_decimal = format % obj
            return round(float(new_decimal), decimal_place)
        except ValueError:
            return 0.00

    @staticmethod
    def str_to_int(obj):
        try:
            return int(obj)
        except ValueError:
            return 0

    @staticmethod
    def str_to_float(decimal_place, obj):
        try:
            return round(float(obj), decimal_place)
        except ValueError:
            return 0.00

    @staticmethod
    def format_float(num):
        return np.format_float_positional(num, trim="-")

    @staticmethod
    def format_float_list(values):
        values_list = []
        for val in values:
            values_list.append(np.format_float_positional(float(val), trim="-"))
        return values_list

    @staticmethod
    def str_to_decimal(decimal_place, obj):
        try:
            obj = float(obj)
            if math.isnan(obj) or math.isinf(obj):
                obj = 0.00
        except ValueError:
            obj = 0.00
        return Decimal(obj).quantize(Decimal(".0001"))

    @staticmethod
    def remove_none(s):
        if s is None:
            return ""
        return str(s)

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
    def get_sys_paramter(key):
        new_sys_parameter = {
            "app_eda": ["-", 'If "True" to show EDA module', False],
            "decimalpoint": ["2", "Default decimal point of the system", False],
            "EC_BETA_ENDPOINT": ["-", "Read pdf image data", False],
            "workdays": ["MO,TU,WE,TH,FR,SA", "Working days in a week. Alternate working day can be defined like MO,TU,WE,TH,FR;MO,TU,WE,TH,FR,SA", False],
            "tax_rate": ["0", "Default tax rate", False],
            "app_production": ["True", 'If "True" to show production module', False],
            "auto_generate_product_code": ["False", "If value is true then product article number will be generated by system.", False],
            "auto_stock_location": ["True", "Automatic warehouse location create when sale order create.", False],
            "MO_BOX_LABEL_LANG": ["en", False],
            "quotation_approval": ["False", "for To be approoved menu in purchasing", False],
            "receipt_scan_value": ["product_name", "Scan product on the basis of product name.", False],
            "company_code": ["", "Company code for template prefix", True],
            "ECOM_API_KEY": ["6c0cefc7d600", "Used in product api as security key.", False],
            "EC_CUSTOMER_ID": ["-", "Eurocircuits id used in visualizer.", False],
            "EC_API_URL": ["-", "EC API URL to communicate with visualizer.", False],
            "EC_API_KEY": ["-", "EC API security key.", False],
            "EC_POST_URL": ["-", "EC_POST_URL", False],
            "EC_POST_KEY": ["-", "EC_POST_KEY", False],
            "Indirect_cost": ["0", " Add below cost value add into total cost.", False],
            "CLIENT_POST_URL": ["http://192.168.1.135:8080/assembly/sparrowapi/UpdateStatus", "API URL to post data on client server..", False],
            "CLIENT_POST_KEY": ["516f30f0-b587-4381-abf6-8b91f06efa59-1", "client POST API security key.", False],
            "TRANSPARENCY": ["0.5", False],
            "OCTOPART_KEY": ["-", "Octopart API key", False],
            "decimalpoint_grid": ["2", "To show decimal point in grid-list", False],
            "app_ecommerce": ["False", "If true show customer site view", False],
            "purchase_plan_eda": ["-", "If 'True' then supplier price data store into eda schemas otherwise current schemas", False],
            "farnell_storeinfo": ["sk.farnell.com", "Storeinfo id for farnell", False],
            "has_farnell_discount": ["True", "If true add discount price for farnell component.", False],
            "mpn_field": ["name", "Parameter value is the one of product's column name that we want to use as a MPN when market availability is done.", False],
            "ENFORCE_INVENTORY": ["True", "Ship order even when stock not available.", False],
            "ftr_remark": ["N9TT-9G0A-B7FQ-RANC", "Show remark tab if valid code value.", False],
            "ftr_attachment": ["QK6A-JI6S-7ETR-0A6C", "Show attachment tab if valid code value.", False],
            "ftr_notification": ["SXFP-CHYK-ONI6-S89U", "Show notification tab if valid code value.", False],
            "ftr_task": ["M66T-8A00-4RP6-93KA", "Show task icon if valid code value.", False],
            "email_backend": ["django.core.mail.backends.smtp.EmailBackend", "Backend system for sending an email", False],
            "email_host": ["email-smtp.ap-south-1.amazonaws.com", "Gateway provider for sending an email", False],
            "email_host_user": ["AKIARLZJKCXIKI5BDYN7", "Username for sending an email", False],
            "email_host_password": ["BC/LS8mIA4XF7Nc8Ja+18TLkSNh6IxwVh65TtrO7UrSc", "Password for sending an email", False],
            "email_port": ["465", "Port of the mail gateway", False],
            "email_use_ssl": ["True", "SSL setting for the email", False],
            "email_from": ["noreply@sparrowerp.com", "From email address for of the email", False],
            "email_bcc": ["False", "BCC mail address for the mail", False],
            "TAX_RULE": ["", "Apply tax on invoice", False],
            "BACKGROUND_THREAD": ["-", "If value is set CELERY then all the long process task like email sending will use celery as a background process.", False],
            "default_cust_credit": ["0", "Default customer credit limit", False],
            "ENFORCE_CUST_CREDIT": ["False", "To check credit limit of customer.", False],
            "REORDER_STOCK_MAILS": ["None", "Mail list to send reorder stock notification.", False],
            "REORDER_STOCK_NOTIFICATIONS": ["False", "If values is True then it will send mail/system notification if products stocks went down below reorder.", False],
            "LAUNCHER_VIEW": ["False", "Launcher view of website", False],
            "SUPPLIER_IDS": ['{"Element14": 69,"Digi-Key": 3,"Mouser": 6,"TME": 14,"Conrad": 13,"Arrow":8,"RSComponent":77}', "Set supplier id for purchase plan", False],
            "PROD_REPORT_STATUS_COLOR": [
                """{"PCB: In production" : "yellow","PCB: Shipped to Assembly" : "green","STA/SBA: Stencil Review" : "",
                "STA/SBA: Stencil Incoming" : "yellow","STA/SBA: Stencil Burning" : "yellow",
                "STA/SBA: Assembly Delivery" :"yellow","STA/SBA: Shipped to Assembly"  :"green",
                "EC Sourcing: Sourcing" : "yellow","EC Sourcing: Ordered": "green",
                "Customer Sourcing: Waiting" : "yellow","Customer Sourcing: Received" : "green","Finanical status: OK" : "",
                "Finanical status: Blocked/DOH" : "#ec7070"}""",
                "Set production report different status color.",
                False,
            ],
            "HRM_LEAVE_REQUEST_MAIL": ["", "Email address to sent a leave approval mail.", False],
            "ASSEMBLY_COMP_SALES_MARGIN": ["0", "Sales margin over component.", False],
            "TOKEN_EXPIRE_ON": ["1", "Token expire time in minutes.", False],
            "COMP_PRICE_SOURCE": ["-", "Api source.", False],
            "SCAN_PACK_DEFAULT_WEIGHT": ["0.01", "Default scan package weight", False],
            "SALES_CONTRACT_DEFAULT_SUPPLIERS": ["556, 535, 534", "Defualt supplier id for generating purchase order in sales contract", False],
            "PCB_ASSEMBLY_APP": ["-", "Show CPL if its value is true.", False],
            "TARIFF_CHARGE": ["2", "Default tariff charge", False],
            "POWER_SO_API_CHANGE_NOTIFY": ["", "Power so mail send", False],
            "SALES_TARIFF": ["FALSE", "Sales order TARIFF charge include or not.", False],
            "SALES_BCD": ["FALSE", "Sales order BCD charge include or not.", False],
            "SHIP_COST_PER_ITEM": ["FALSE", "Ship cost per item.", False],
            "COMPANY_LOGO": ["logo1-w.png", "Set company logo.", False],
            "CHECK_CURRENCY_EXPIRATION": ["False", "If value is True then it will force to enter currency exchange rate on login if any one is expired.", False],
            "INTELLIAL_INFO_MAIL": ["inthekhab.intellial@gmail.com", "Receive email when someone register for trial in this email", False],
            "PRODUCTION_FIXED_MARGIN": ["1", "Fixed margin for production", False],
            "PRODUCTION_PERCENTAGE_MARGIN": ["0.05", "Fixed percentage margin for production", False],
            "SALES_PRODUCT_DEFAULT_ROUTE": ["buy", "Default sales procurment states", False],
            "stock_selection": ["LIFO", "Stock selection will be proposed based on LIFO or FIFO configuration", False],
            "PO_QUOTE_REMINDER_RULE": ["", "Qutotation reminder to supplier based on once_a_week, alternate and each day rule.", False],
            "ASSEMBLY_PRICE_FORMULA": [
                {
                    "per_job": 100,
                    "per_SMD_side": 50,
                    "per_part": 3,
                    "per_SMD": 0.1,
                    "per_SMDFP": 0.15,
                    "per_TH": 0.5,
                    "per_BGA": 1,
                    "per_BGAFP": 5,
                    "per_QFN": 5,
                    "per_QFNFP": 0.2,
                    "per_LGA": 0.5,
                    "per_assembly_order_unit": 30,
                    "breakout_per_assembly_unit": 0,
                    "extra_price_for_single_PCB": 0,
                },
                "This formula will be used for calculating assembly price.",
                False,
            ],
            "RETURN_REMAINING_PART_TO_CUSTOMER": [
                False,
                "If value is True then remaining stock will be set to Zero once mfg order finished from the BOM except generic part.",
                False,
            ],
            "production_by_panel": [False, " If value is True then MO operation flow will be run by panel.", False],
            "ftr_sms_service": [False, "Sms notification service", False],
            "email_from_name": ["Sparrow", "This name will be used for sending mail", False],
            "google_analytic_code": ["", "Google analytic code to tracking most usead apps.", False],
            "eda_supp_price_update_rate": [5, "Supplier price will be updated if it is older then 3 days. Parameter value is in days.", False],
            "ftr_campaign": [False, "If value is False then “Send newaslatter” button will be disabled.", False],
            "EDI_ADDRESS": ["", "Address for EDI data.", False],
            "API_PURCHASE_ORDER_EMAIL_NOTIFICATION": ["", "Mail sent to authorised member on Purchase order via API as in case of Wurth.", False],
            "COMPANY_PDF_LOGO": ["", "Set company pdf logo.", False],
            "EDA_READONLY": [False, "Part will handled read-ony.", False],
            "SYSTEM": ["EC", "To check the crosponding system", False],
            "COMMENT_CHRONOLOGICAL_ORDER": [
                "ASC",
                "Comment will be shown in chronological order",
            ],
            "THEMES": [
                "THEMES",
                {
                    'theme_black': 'bg_color:#202020,button_color:#202020,link_color:#1a73e8,row_color:#20202017,db_bg_color:#ebebeb',
                    'theme_dark_blue': 'bg_color:#042853,button_color:#042853,link_color:#1f1bc1,row_color:#e4e4e4,db_bg_color:#d5e3f4',
                    'theme_persian_green': 'bg_color:#07a092,button_color:#07a092,link_color:#007a74,row_color:#07a09217,db_bg_color:#e8f7f5',
                    'theme_royal_blue': 'bg_color:#4169e1,button_color:#4169e1,link_color:#2d4bba,row_color:#4169e117,db_bg_color:#eef1fd',
                    'theme_violet': 'bg_color:#370665,button_color:#370665,link_color:#7a0de1,row_color:#37066517,db_bg_color:#ede8f1'
                },

                False,
            ],
        }
        sys_parameters = None

        if Util.get_cache("public", Util.sys_param_key) is None:
            sys_parameters = SysParameter.objects.all()
            Util.set_cache("public", Util.sys_param_key, sys_parameters, 3600)
        else:
            sys_parameters = Util.get_cache("public", Util.sys_param_key)
        sys_param = None
        if sys_parameters:
            for param in sys_parameters:
                if param.para_code == key:
                    sys_param = param
                    break

        if sys_param is None and key in new_sys_parameter.keys():
            sys_parameter = None
            sys_parameter = SysParameter.objects.create(para_code=key, para_value=new_sys_parameter[key][0], descr=new_sys_parameter[key][1], for_system=new_sys_parameter[key][2])
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
    def get_resource_path(resource, resource_name):
        resource_path = os.path.join(settings.RESOURCES_ROOT, "public", "resources")
        if resource == "product":
            resource_path = os.path.join(resource_path, "product_images")
        elif resource == "profile":
            resource_path = os.path.join(resource_path, "profile_image")
        elif resource == "pro_import":
            resource_path = os.path.join(resource_path, "ImportProducts")
        elif resource == "release_note_media":
            resource_path = os.path.join(resource_path, "release_note_media")
        elif resource == "pdf_marking_image":
            resource_path = os.path.join(resource_path, "pdf_marking_images")
        if resource_name:
            resource_path = os.path.join(resource_path, resource_name)

        return resource_path

    @staticmethod
    def get_resource_url(resource, resource_name):
        resource_url = settings.RESOURCES_URL + "public" + "/resources/"
        if resource == "product":
            resource_url += "product_images/"
        elif resource == "profile":
            resource_url += "profile_image/"
        elif resource == "pdf_marking_image":
            resource_url += "pdf_marking_images/"
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
                values = record
                if type(record) == dict:
                    values = record.values()
                for col_index, (value) in enumerate(values):
                    if "type" in headers[col_index]:
                        if headers[col_index]["type"] == "date":
                            value = Util.get_local_time(value)
                        if headers[col_index]["type"] == "boolean":
                            value = "YES" if value is True else "NO"
                    ws.write(row_number, col_index, value)
                row_number = row_number + 1
            wb.save(f)
            response = HttpResponse(content_type="application/ms-excel")
            response["Content-Disposition"] = "attachment; filename=%s" % file_name
            wb.save(response)
            return response

        except Exception as e:
            f.close()
            manager.create_from_exception(e)
            logging.exception("Something went wrong.")
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
        finally:
            f.close()

    # @staticmethod
    # def is_ec_integrated():
    #     if Util.get_sys_paramter("ec_integration").para_value == "True":
    #         return True
    #     else:
    #         return False

    @staticmethod
    def get_dict_from_quryset(key, val, records):
        dict = {}
        for record in records:
            dict[record[key]] = record[val]

        return dict

    @staticmethod
    def currency_convert(amount, currency_factor, into_base_currency=True):
        amount = 0 if amount is None else amount
        if into_base_currency:
            amount = amount / currency_factor
        else:
            amount = amount * currency_factor
        return float(amount)

    @staticmethod
    def get_local_time_obj(utctime):
        if Util.get_cache("public", "local_datetime") is None:
            partner_obj = Partner.objects.filter(is_hc=True).values("timezone_offset").first()
            offset = partner_obj["timezone_offset"] if partner_obj["timezone_offset"] is not None else 0
            Util.set_cache("public", "local_datetime", offset, 3600)
        else:
            offset = Util.get_cache("public", "local_datetime")

        if utctime == "" or utctime is None:
            return ""
        if offset == 0:
            new_time = utctime
        else:
            new_time = utctime + datetime.timedelta(minutes=offset)

        return new_time

    @staticmethod
    def get_timezone_info():
        if Util.get_cache("public", "timezone_info") is None:
            timezone_info = settings.TIME_ZONE
            Util.set_cache("public", "timezone_info", timezone_info, 3600)
        else:
            timezone_info = Util.get_cache("public", "timezone_info")
        return timezone_info

    @staticmethod
    def get_local_time(utctime, showtime=False, time_format=None):
        if utctime == "" or utctime is None or utctime == 0 or utctime == "-":
            return ""
        timezone_info = Util.get_timezone_info()
        from_zone = tz.gettz("UTC")
        to_zone = tz.gettz(timezone_info)
        utctime = utctime.replace(tzinfo=from_zone)
        new_time = utctime.astimezone(to_zone)
        if showtime:
            if time_format is None:
                time_format = "%d/%m/%Y %H:%M"
            return new_time.strftime(time_format)
        else:
            return new_time.strftime("%d/%m/%Y")

    @staticmethod
    def convert_time_to_utc(timeobj, time_format=None):
        local_timezone = Util.get_timezone_info()
        timezone = pytz.timezone(local_timezone)
        local_time = timezone.localize(timeobj)
        to_zone = tz.gettz("UTC")
        if time_format is None:
            time_format = "%d/%m/%Y %H:%M"
        utc_time = local_time.astimezone(to_zone).strftime(time_format)
        return utc_time

    @staticmethod
    def get_utc_datetime(local_datetime, has_time, timezone):
        naive_datetime = None
        local_time = pytz.timezone(timezone)

        if has_time:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y %H:%M")
        else:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y")

        local_datetime = local_time.localize(naive_datetime, is_dst=None)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime

    @staticmethod
    def get_user_permissions(user_id):
        user_groups = accounts_model.UserGroup.objects.filter(user_id=user_id).values_list("group_id", flat=True)
        # role_ids = ','.join(map(str, groups))
        menu_perm_ids = []
        for group_id in user_groups:
            if Util.get_cache("public", "ROLES" + str(group_id)) is None:
                group_permissions = accounts_model.GroupPermission.objects.filter(group_id=group_id).values(
                    "page_permission__menu_id", "page_permission__menu__menu_code", "page_permission__act_code"
                )
                Util.set_cache("public", "ROLES" + str(group_id), group_permissions, 3600)
            else:
                group_permissions = Util.get_cache("public", "ROLES" + str(group_id))
            menu_perm_ids += group_permissions
        return menu_perm_ids

    @staticmethod
    def has_perm(act_code, user):
        has_permission = False
        if user.is_superuser is True:
            has_permission = True

        user_perms_objs = Util.get_user_permissions(user.id)

        for user_perms_obj in user_perms_objs:
            if user_perms_obj["page_permission__act_code"] == act_code:
                has_permission = True
                break

        return has_permission

    @staticmethod
    def get_key(key):
        try:
            if key is None:
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
        secs = int((minutes - mins - (hrs * 60) - (days * 24 * 60)) * 60)

        if days != 0:
            days = "%02d" % (days)
            time += str(days) + "d"
            if hrs != 0 or mins != 0 or secs != 0:
                time += ":"
        if hrs != 0:
            spent_hours = "%02d" % (hrs)
            time += str(spent_hours) + "h"
            if mins != 0 or secs != 0:
                time += ":"
        if mins != 0:
            mins = "%02d" % round(mins)
            time += str(mins) + "m"
            if secs != 0:
                time += ":"
        if secs != 0:
            secs = "%02d" % round(secs)
            time += str(secs) + "s"
        return time

    @staticmethod
    def generate_random_string(stringLength):
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(stringLength))

    @staticmethod
    def strip_html(text):
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    @staticmethod
    def encrypt(value):
        BLOCK_SIZE = 32  # Bytes
        cipher = AES.new(settings.SECRET_KEY[:32].encode("utf8"), AES.MODE_ECB)
        msg = cipher.encrypt(pad(value.encode("utf-8"), BLOCK_SIZE))
        b64_encoded = base64.b64encode(msg)
        return b64_encoded.decode("utf-8")

    @staticmethod
    def decrypt(value):
        BLOCK_SIZE = 32  # Bytes
        decipher = AES.new(settings.SECRET_KEY[:32].encode("utf8"), AES.MODE_ECB)
        b64_decoded = base64.b64decode(value.encode("utf-8"))
        msg_dec = decipher.decrypt(b64_decoded)
        return unpad(msg_dec, BLOCK_SIZE)

    @staticmethod
    def get_client_service_instance():
        from eurocircuits.service import ECIntegration

        company_code = Util.get_sys_paramter("company_code").para_value
        if company_code == "1":
            return ECIntegration()
        return None
