import csv
import datetime
import json
import math
import os
from decimal import Decimal
from io import BytesIO
from xml.dom.minidom import parseString

import pytz
import requests
import xlwt
from auditlog.models import ErrorBase
from customer.models import Country
from dateutil import tz
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Q, Sum

# from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils import timezone
from rest_framework_xml.renderers import XMLRenderer
from base.models import CodeTable, Currency
from accounts.models import MainMenu, UserProfile, UserGroup, PagePermission, GroupPermission, User


class Util(object):
    @staticmethod
    def set_cache(key, value, time=3600):
        cache.set(key, value, time)

    @staticmethod
    def get_cache(key):
        if cache.has_key(key):
            return cache.get(key)
        return None

    @staticmethod
    def clear_cache(key):
        if cache.has_key(key):
            cache.delete(key)

    @staticmethod
    def get_resource_path(resource, resource_name):
        resource_path = os.path.join(settings.RESOURCES_ROOT, "resources")
        if resource == "profile":
            resource_path = os.path.join(resource_path, "profile_image")
        if resource_name:
            resource_path = os.path.join(resource_path, resource_name)
        return resource_path

    @staticmethod
    def get_resource_url(resource, resource_name):
        resource_url = settings.RESOURCES_URL + "resources/"
        if resource == "profile":
            resource_url += "profile_image/"
        resource_url += resource_name
        return resource_url

    @staticmethod
    def delete_old_file(path_file):
        if os.path.exists(path_file):
            os.remove(path_file)

    @staticmethod
    def get_dict_from_queryset(key_name, val, records):
        dict = {}
        for record in records:
            dict[record[key_name]] = record[val]
        return dict

    @staticmethod
    def get_utc_datetime(local_datetime, has_time):
        naive_datetime = None
        current_time_zone = timezone.get_current_timezone_name()
        local_time = pytz.timezone(current_time_zone)

        if has_time:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y %H:%M")
        else:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y")

        local_datetime = local_time.localize(naive_datetime, is_dst=None)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime

    @staticmethod
    def get_codes(code):
        codes = None
        if Util.get_cache(code) is None:
            if code == "code_table":
                codes = CodeTable.objects.values("code", "id")
                Util.set_cache("code_table", codes, 3600)
            elif code == "currency":
                codes = Currency.objects.values("code", "id")
                Util.set_cache("currency", codes, 3600)
            elif code == "country":
                codes = Country.objects.values("code", "id")
                Util.set_cache("country", codes, 3600)
        else:
            codes = Util.get_cache(code)
        dict = Util.get_dict_from_queryset("code", "id", codes)
        return dict

    @staticmethod
    def get_xml(file):
        if file:
            # parser = ET.XMLParser(file)
            # root = ET.fromstring(file, parser=parser)
            data = json.loads(file)
            # data = json.dumps(data)
            response = {"totalRecords": len(data), "data": []}
            # response["data"] =  file
            for val in data:
                response["data"].append(
                    {
                        "id": val["id"],
                        "name": val["name"],
                        "bank_account_nr": val["number"],
                        "amount": val["amount"],
                        "message": val["message"],
                        "match": val["match"],
                        "invoice_status": val["invoice_status"] if "invoice_status" in val else "",
                        "invoice_nr": val["Invoice_Nr"],
                        "amountInvoice": val["amount_invoice"] if "amount_invoice" in val else 0.00,
                        "matchInvoice": val["matchInvoice"] if "matchInvoice" in val else "",
                        "type": val["type"] if "type" in val else "",
                        "manuallyadded": val["manuallyadded"] if "manuallyadded" in val else "",
                        "remark": val["remark"] if "remark" in val else "",
                        "tr_date": val["tr_date"] if "tr_date" in val else "",
                        "FilteredMessageOrder": val["FilteredMessageOrder"] if "FilteredMessageOrder" in val else "",
                        # "FilteredMessageDelivery" : FilteredMessageDelivery,
                    }
                )
            return response

    @staticmethod
    def str_to_decimal(decimal_place, obj):
        try:
            obj = float(obj)
            if math.isnan(obj) or math.isinf(obj):
                obj = 0.00
        except ValueError:
            obj = 0.00
        return Decimal(obj).quantize(Decimal(".0001"))

    payment_prefix = {
        "invoice": "C14B|C14D|C15B|C15D|C15F|CPS|CPSB|CPSD|CPSF|CPSS|E14B|E14D|E14F|E14H|E14S|E15B|E15D|E15F|E15H|E15S|EB00|EB10|EB11|EB99|EBCI|EC07|EC08|EC09|EC10|ED08|ED09|ED10|EF00|EF08|EF09|EF10|EF11|EF12|EF13|EF14|EF15|EF16|EF99|EG00|EG10|EG11|EG12|EG13|EG14|EG15|EG17|EG99|EGCI|EH00|EH10|EH11|EH12|EH13|EH14|EH15|EH16|EH99|EKB09|EKC09|EN00|EN10|EN11|EN12|EN13|EN14|EN15|EN16|EN99|EP08|EP09|EP10|EPSB|EPSD|EPSF|EPSH|EPSS|EPU12|EPU13|EPU14|EPU15|EPU17|EPU99|ES00|ES08|ES09|ES10|ES11|ES12|ES13|ES14|ES15|ES16|ES99|EU00|EU12|EU13|EU14|EU15|EU17|EU99|EW11|EW12|EW13|EW99M14B|M14D|M14F|M15B|MPS|MPSB|MPSD|MPSS|PE14B|PE14D|PE14F|PE14S|PE15B|PE15D|PE15F|PE15S|PEB10|PEB11|PEF10|PEF14|PEF15|PEF16|PEG10|PEG11|PEG14|PEG15|PEG17|PEH14|PEH15|PEN14|PEN15|PEN16|PEPU14|PES10|PES14|PES15|PES16|PESB14|PESB15|PESB16|PESF14|PESF15|PESF16|PESG14|PESG15|PESG16|PESS14|PESS15|PEU14|PEU15|PEU17|PN00|PN10|PN11|PN12|PNCI|PPN10|PPN11|SIEC04|Wk09|EN00|ENOO|EU17|EPU17|ECU17|EG17|ECD17|EH17|ECH17|ES17|ECS17|EF17|ECF17|EN17|ECN17|ECU99|ECD99|CPSH|C14H|ECH99|C14S|ECS99|C14F|ECF99|ECN99|PEU17|PEPU17|PECU17|PEG17|PESG17|PECD99|PEH17|PESH17|PE14H|PECH17|PES17|PESS17|PECS99|PEF17|PESF17|PECF17|PEN17|PESB17|PECN17EU18|EPU18|E14U18|ECU18|EG18|ECD18|EH18|ECH18|ES18|ECS18|EF18|ECF18|EN18|ECN18|CPSD99|C14D99|CPSH99|C14H99|CPSS99|C14S99|CPSF99|C14F99|CPSB99|C14B99|PEU18|PEPU18|PE14U18|PECU18|PEG18|PESG18|PECD18|PEH18|PESH18|PECH18|PES18|PESS18|PECS18|PEF18|PESF18|PECF18|PEN18|PESB18|PECN18|EU19|EPU19|E14U19|ECU19|EG19|EPSD|E14D|ECD19|EH19|EPSH|E14H|ECH19|ES19|EPSS|E14S|ECS19|EF19|EPSF|E14F|ECF19|EN19|EPSB|E14B|ECN19|PEU19|PEPU19|PE14U19|PECU19|PEG19|PESG19|PE14D|PECD19|PEH19|PESH19|PE14H|PECH19|PES19|PESS19|PE14S|PECS19|PEF19|PESF19|PE14F|PECF19|PEN19|PESB19|PE14B|PECN19|EU20|EPU20|E14U20|EG20|ECD20|EH20|ECH20|ES20|ECS20|EF20|ECF20|EN20|ECN20|4M20|EA20|ECA20|PEU20|PEPU20|PE14U20|PEG20|PESG20|PECD20|PEH20|PESH20|PECH20|PES20|PESS20|PECS20|PEF20|PESF20|PECF20|PEN20|PESB20|PECN20|PP4MN20|PEA20|PESA20|PECA20|EU21|EPU21|E14U21|ECU21|EG21|ECD21|EH21|ECH21|ES21|ECS21|EF21|ECF21|EN21|ECN21|4M21|EA21|ECA21|PEU21|PEPU21|PE14U21|PECU21|PEG21|PESG21|PECD21|PEH21|PESH21|PECH21|PES21|PESS21|PECS21|PEF21|PESF21|PECF21|PEN21|PESB21|PECN21|PP4MN21|PEA21|PESA21|PECA21|EPSA|EPSA",
        "delivery": "CSP|ECP|WIP|DE|DF|DP|HU",
        "order": "E|P|F|C|M",
    }

    @staticmethod
    def export_to_xls(headers, records, file_name):
        f = BytesIO()
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

    @staticmethod
    def xml_generator(data, root_tag_name=None, item_tag_name=None):
        renderer = XMLRenderer()
        if root_tag_name and item_tag_name:
            renderer.item_tag_name = item_tag_name
            renderer.root_tag_name = root_tag_name
        content = renderer.render(data)
        # return content
        return parseString(content).toxml(encoding="utf-8")

    @staticmethod
    def download_xml_file(data, root_tag_name=None, item_tag_name=None, file_name=None):
        response = HttpResponse(Util.xml_generator(data, root_tag_name=root_tag_name, item_tag_name=item_tag_name), content_type="application/xml")
        response["Content-Disposition"] = "attachment; filename=%s" % file_name
        return response

    @staticmethod
    def download_csv_file(headers, records, file_name):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(file_name)
        writer = csv.writer(response)
        titles = []
        for key, value in enumerate(headers):
            titles.append(value["title"])
        writer.writerow(titles)
        for record in records:
            values = record
            if type(record) == dict:
                values = record.values()
            row = []
            for col_index, (value) in enumerate(values):
                row.append(value)
            row = row
            writer.writerow(row)
        return response

    # @staticmethod
    # def get_timezone_info():
    #     if Util.get_cache(connection.tenant.schema_name, "timezone_info") is None:
    #         partner_obj = Partner.objects.filter(is_hc=True).values("timezone").first()
    #         timezone_info = partner_obj["timezone"]
    #         Util.set_cache(connection.tenant.schema_name, "timezone_info", timezone_info, 3600)
    #     else:
    #         timezone_info = Util.get_cache(connection.tenant.schema_name, "timezone_info")
    #     return timezone_info
    @staticmethod
    def get_local_time(utctime, showtime=False, time_format=None):
        if utctime == "" or utctime is None or utctime == 0 or utctime == "-":
            return ""
        timezone_info = timezone.get_current_timezone_name()
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
    def create_exception_log(message, class_name=None, level=40, traceback=None):
        ErrorBase.objects.create(class_name=class_name, message=message, traceback=traceback, level=level)

    @staticmethod
    def get_ec_py_token():
        token = None
        if Util.get_cache("ec_py_token") is None:
            payload = {
                "username": "apitest",
                "password": "ispl123;",
            }
            token_url = settings.EC_PY_URL + "/ecpy/token"
            token = requests.post(token_url, data=payload).json()
            token = token["access_token"]
            Util.set_cache("ec_py_token", token, 1500)
        else:
            token = Util.get_cache("ec_py_token")
        return token

    @staticmethod
    def get_user_permissions(user_id):
        groups = UserGroup.objects.filter(user_id=user_id).values_list("group_id", flat=True)
        menu_perm_ids = []

        for group_id in groups:
            # if Util.get_cache("ROLES" + str(group_id)) is None:
            menu_perms = GroupPermission.objects.filter(group_id=group_id).values("page_permission__menu_id", "page_permission__menu__menu_code", "page_permission__act_code")
            #     Util.set_cache("ROLES" + str(group_id), menu_perms, 3600)
            # else:
            #     menu_perms = Util.get_cache("ROLES" + str(group_id))
            menu_perm_ids += menu_perms
        return menu_perm_ids

    @staticmethod
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
        return menu_ids

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
