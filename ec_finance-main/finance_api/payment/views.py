import json
import re
import xml.etree.cElementTree as ET
import xml.etree.ElementTree as ET
from decimal import Decimal
from xml.etree import ElementTree
from xml.etree.ElementTree import XML, fromstring

import mt940
import numpy as np
import pandas as pd
import requests
from base.sb_send import azure_service
from base.util import Util
from base.util import Util as TOKEN
from django.conf import settings
from django.db.models import F, Q, Sum, Value
from django.db.models.functions import Concat
from finance_api.rest_config import APIResponse, CustomPagination
from rest_framework import generics, viewsets
from rest_framework.decorators import (action, api_view, parser_classes,
                                       renderer_classes)
from rest_framework.parsers import (FileUploadParser, FormParser,
                                    MultiPartParser)
from rest_framework.renderers import HTMLFormRenderer
from rest_framework.response import Response
from sales.models import Invoice, InvoiceOrder

from payment.filter import (PaymentBrowserFilter, PaymentBrowserUnmatchFilter,
                            PaymentImportViewFilter)
# from drf_renderer_xlsx.renderers import XLSXRenderer
# from drf_renderer_xlsx.mixins import XLSXFileMixin
from payment.models import (CodaCustomerMapping, CodaFile, CodaTransaction,
                            PaymentBrowserUnmatch)
from payment.serializers import (CodaFileSerializer, PaymentBrowserSerializer,
                                 PaymentBrowserUnmatchSerializer)


# Create your views here.
class PaymentImportView(viewsets.ModelViewSet):
    serializer_class = CodaFileSerializer
    pagination_class = CustomPagination
    filterset_class = PaymentImportViewFilter
    # self.file_data = []
    def get_queryset(self):
        query = Q()
        queryset = (
            CodaFile.objects.filter(query, is_deleted=False)
            .values("id", "created_by__last_name", "created_by__last_name", "file_name", "compared_xml_string", "is_deleted", "created_on", "xml_string")
            .annotate(full_name=Concat(F("created_by__first_name"), Value(" "), F("created_by__last_name")))
        )
        return queryset

    @action(detail=False, methods=["post"])
    def delete_payment(self, request):
        ids = request.data.get("ids")
        if ids is None:
            return APIResponse(code=0, message="Something went wrong")
        CodaFile.objects.filter(id=ids).update(is_deleted=True)
        return APIResponse(code=1, message="Payment deleted")

    @action(detail=False, methods=["get"])
    def xml_payment_import(self, request):
        ids = request.GET.get("ids")
        print(ids,"ids")
        ids = int(ids)
        xml_file = CodaFile.objects.filter(id=ids).values("compared_xml_string2").first()
        response = None
        sort_col = request.GET.get("ordering")
        if response is None and xml_file:
            response = Util.get_xml(xml_file["compared_xml_string2"])
            # if sort_col[:1] == "-":
            #     response["data"].sort(key=lambda obj:  obj[sort_col[1:]] if obj is not None else "", reverse=True)
            # else:
            #     response["data"].sort(key=lambda obj: obj[sort_col] if obj is not None else None)
        return Response(response)


class PaymentBrowserView(generics.ListAPIView):
    serializer_class = PaymentBrowserSerializer
    pagination_class = CustomPagination
    filterset_class = PaymentBrowserFilter

    def get_queryset(self):
        query = Q()
        queryset = CodaTransaction.objects.filter(query).values(
            "id",
            "invoice__id",
            "ec_customer_id",
            "invoice_no",
            "customer_name",
            "created_on",
            "invoice__status__desc",
            "invoice__currency__code",
            "invoice__country__name",
            "amount",
            "invoice__invoice_value",
            "bank_account_no",
            "bank_name",
            "invoice__payment_date",
        )
        return queryset


class PaymentBrowserUnmatchView(generics.ListAPIView):
    serializer_class = PaymentBrowserUnmatchSerializer
    pagination_class = CustomPagination
    filterset_class = PaymentBrowserUnmatchFilter

    def get_queryset(self):
        query = Q()
        queryset = (
            PaymentBrowserUnmatch.objects.filter(query, is_deleted=False)
            .values(
                "id",
                "customer_name",
                "bank_account_nr",
                "bank_name",
                "amount",
                "message",
                "invoice_nos",
                "remarks",
                "created_on",
                "created_by__last_name",
                "created_by__last_name",
            )
            .annotate(full_name=Concat(F("created_by__first_name"), Value(" "), F("created_by__last_name")))
        )
        return queryset


@api_view(["post"])
def delete_payment_unmatched(request):
    ids = request.data.get("ids")
    if ids is None:
        return APIResponse(code=0, message="Something went wrong")
    # for id in ids:
    ids = [x for x in ids.split(",")]
    PaymentBrowserUnmatch.objects.filter(id__in=ids).update(is_deleted=True)
    azure_payload = {
        "type": "DeletePyamentUnmatched",
        "data": {
            "id": id,
            "is_deleted": True,
        },
    }
    return APIResponse(code=1, message="Deleted")


def mt_940(file):
    transactions = mt940.parse(file)
    payment_file = json.dumps(transactions, indent=4, cls=mt940.JSONEncoder)
    json_data = json.loads(payment_file)
    data = []
    for value in json_data["transactions"]:
        i_line = str(value["transaction_details"]).split("\n")
        msg = ""
        if len(i_line) > 0:
            msg = i_line[2] if len(i_line) >= 3 else ""
            msg = msg + " " + i_line[1] if len(i_line) > 1 else ""
        data.append(
            {
                "name": i_line[1] if len(i_line) > 1 else "",
                "number": value["bank_reference"],
                "tr_date": str(value["date"]),
                "tre_date": str(value["entry_date"]),
                "amount": str(value["amount"]["amount"]),
                "message": msg,
                "st_message": msg,
            }
        )
    return data


def sts_940(file):
    transactions = mt940.parse(file)
    payment_file = json.dumps(transactions, indent=4, cls=mt940.JSONEncoder)
    json_data = json.loads(payment_file)
    data = []
    for value in json_data["transactions"]:
        detail = str(value["transaction_details"]).split("\n")
        name = str(detail[0])[7:]
        number = str(detail[1]).split(",")[0]
        msg = "".join(i for i in str(detail[1]).split(",")[1:])
        data.append(
            {
                "name": name,
                "number": number.replace("C/", ""),
                "tr_date": str(value["date"]),
                "tre_date": str(value["entry_date"]),
                "amount": str(value["amount"]["amount"]),
                "message": msg,
                "st_message": "",
            }
        )
    return data


def coda_de_fr(file_path):
    file_data = str(file_path.read().decode("utf-8")).split("0 0\r\n")
    data = []
    for value in file_data:
        result = re.findall("TYPE/(.+?)/", value)
        if "089" in result and "F06" in result:
            continue
        result = defr_regex("INFO :(.+?)\d+", value)
        if result == "":
            result = defr_regex("NAME/(.+?)/", value)
        name = result
        pattern = "INFO/(.+?)/"
        result = re.findall(pattern, value)

        account_number = re.findall(pattern, value)
        result = re.findall("[0-9]{31}TRANS", value)
        trDate = ""
        if len(result) > 0 and len(result[0]) > 22:
            trDate = str(result[0])[16:22]
        amount = result
        if len(result) > 0 and len(result[0]) > 16:
            amount = str(amount[0])[2:16]
            if amount.isnumeric():
                amount = Decimal(str(amount[:11] + "." + amount[11:]))
            else:
                amount = Decimal("0")
        else:
            amount = Decimal("0")
        msg_line = value.replace("\r\n", "")
        message = re.findall("REMI(.+?)EREF", msg_line)
        data.append(
            {
                "name": name,
                "number": str(account_number[0]).strip().replace("0 0\r\n", "") if len(account_number) > 0 else "",
                "tr_date": str(trDate) if len(trDate) > 0 else "",
                "tre_date": str(trDate) if len(trDate) > 0 else "",
                "amount": str(amount),
                "message": str(message[0]) if len(message) > 0 else "",
                "st_message": "",
            }
        )
    return data


def defr_regex(pattern, value, is_match=False):
    collection = []
    result = ""
    m = None
    if len(re.findall(pattern, value)) > 0:
        collection = re.findall(pattern, value)
        if is_match:
            result = m
        else:
            result = collection[0]
    return result


def coda(file):
    file_data = str(file.read().decode("utf-8")).split("0 0\r\n")
    start = 2
    data = []
    for line in file_data:
        rows = line.split("\n")
        result = ""
        if len(rows) <= 3:
            continue
        if start == 2 and len(rows) == 4:
            start = 1
        value = str(rows[2 + start])
        message_value = str(rows[0 + start])
        if str(message_value[0:102]).isnumeric():
            message_value = ""
        if value != "":
            result = value[47:81]
        if result.rstrip().rstrip() == "":
            continue
        name = result.rstrip().rstrip()
        number_value = rows[2 + start]
        number = ""
        if number_value:
            number = number_value[10:40]
        amount_value = str(rows[0 + start])
        result = ""
        if amount_value != "":
            result = str(amount_value[31:46])
        str_amount = result
        if len(result) > 14:
            str_amount = str_amount[9:]
            if str_amount.isnumeric():
                str_amount = str(str_amount[:4] + "." + str_amount[4:])
            else:
                str_amount = "0"
        if message_value:
            message_value = message_value[62:115]
        data.append(
            {
                "name": str(name).strip() if len(name) > 0 else "",
                "number": str(number).strip(),
                "tr_date": "",
                "tre_date": "",
                "amount": str(Decimal(str_amount)),
                "message": str(message_value),
                "st_message": "",
            }
        )
        start = 0
    return data


def cam_941(xmlfile):
    ns = {"prefix": "urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"}
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    transactions = ET.Element("transactions")
    data = []
    for mainnode in root.findall("prefix:BkToCstmrStmt[prefix:Stmt]", ns):
        if len(mainnode.getchildren()) > 0:
            for i in range(len(mainnode.getchildren())):
                if str(mainnode.getchildren()[i].tag).endswith("Stmt"):
                    for j in range(len(mainnode[i].getchildren())):
                        if str(mainnode[i].getchildren()[j].tag).endswith("Ntry"):
                            name = mainnode.getchildren()[i].getchildren()[j].find("prefix:NtryDtls/prefix:TxDtls/prefix:RltdPties/prefix:Dbtr/prefix:Nm", ns).text
                            number = mainnode.getchildren()[i].getchildren()[j].find("prefix:AcctSvcrRef", ns)
                            date = mainnode.getchildren()[i].getchildren()[j].find("prefix:BookgDt/prefix:Dt", ns)
                            message = mainnode.getchildren()[i].getchildren()[j].find("prefix:NtryDtls/prefix:TxDtls/prefix:RmtInf/prefix:Ustrd", ns)
                            amount = mainnode.getchildren()[i].getchildren()[j].find("prefix:Amt", ns)
                            number = number.text if number is not None else " "
                            date = date.text if date is not None else " "
                            message = message.text if message is not None else " "
                            amount = amount.text if amount is not None else " "
                            transaction = ET.SubElement(transactions, "transaction")
                            data.append(
                                {
                                    "name": name,
                                    "number": str(number).strip(),
                                    "tr_date": date,
                                    "tre_date": date,
                                    "amount": amount,
                                    "message": message,
                                    "st_message": "",
                                }
                            )
    return data


@api_view(["post"])
@parser_classes([MultiPartParser])
def upload_payment_file(request):
    payment_file = request.FILES.get("file")
    file_type = str(request.data.get("file_type"))
    user_id = request.data.get("user_id")
    file_data = None
    file_xml = None
    if payment_file is None:
        return APIResponse(code=0, message="Please select file")
    file_name = str(payment_file.name)
    if "UK940" == file_type:
        if file_name.endswith(".940") is False:
            return APIResponse(code=0, message="Select only .940 file.")
        file_xml = mt_940(payment_file)
    elif "STA" == file_type:
        if file_name.endswith(".sta") is False:
            return APIResponse(code=0, message="Select only .STA file.")
        file_xml = sts_940(payment_file)
    elif "CODADEFR" == file_type:
        if file_name.endswith(".COD") is False:
            return APIResponse(code=0, message="Select only .COD file.")
        file_xml = coda_de_fr(payment_file)
    elif "CODA" == file_type:
        if file_name.endswith(".COD") is False:
            return APIResponse(code=0, message="Select only .COD file.")
        file_xml = coda(payment_file)
    elif "CAM" == file_type:
        if file_name.endswith(".CAM") is False:
            return APIResponse(code=0, message="Select only .CAM file.")
        file_xml = cam_941(payment_file)
    response = Util.xml_generator(file_xml, "transactions", "transaction")
    parser = ET.XMLParser(encoding="utf-8")
    root = fromstring(response, parser=parser)
    # file_data = ElementTree.tostring(file_xml).decode("utf-8")
    # parser = ET.XMLParser(encoding="utf-8")
    # root = fromstring(file_data,parser=parser)
    # file_xml = Util.xml_generator(file_xml,"transactions","transaction")
    coda_object = CodaFile.objects.create(file_name=file_name, created_by_id=user_id, xml_string1=json.dumps(file_xml))
    payment_root = filtered_payment_data(file_xml, coda_object, False)
    # file_data = ElementTree.tostring(payment_root,encoding='utf-8', method='xml')
    coda_object.compared_xml_string2 = json.dumps(payment_root)
    coda_object.save()
    importCodaFile(coda_object)
    return APIResponse(code=1, data=coda_object.id, message="File uploaded successfully.")


def filtered_payment_data(data, coda_object, is_updated, file_id=None):
    filtered_invoices = []
    filtered_orders = []
    filtered_delivery = []
    prefix = Util.payment_prefix["invoice"]
    delivery_prefix = Util.payment_prefix["delivery"]
    order_prefix = Util.payment_prefix["order"]
    invoice_regex = "(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/-\\\\ ][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/-\\\\ ][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/-\\\\ ][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[\\\\ ][/-][\\\\ ][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/][0-9][0-9][/][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/][0-9][0-9][0-9][0-9][0-9])"
    delivery_regex = "(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9])"
    order_regex = "(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][-][a-zA-z][a-zA-z][a-zA-z])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][-][a-zA-z 0-9][a-zA-z 0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][-][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9])"

    for i in range(len(data)):
        data[i]["id"] = i
        data[i]["invoice_status"] = ""

        message = data[i]["message"] if "message" in data[i] else ""
        if is_updated:
            message = data[i]["Invoice_Nr"]
        replaced = re.sub("[^a-zA-Z0-9_]+", "", message)
        match_invoice = re.findall(f"({prefix})", replaced)
        matches_invoice = match_invoice if match_invoice is not None else None
        hash_remove_invoice = {}
        for m_env in matches_invoice:
            if m_env not in hash_remove_invoice:
                hash_remove_invoice[m_env] = ""
        replace_str = ""
        for key, value in hash_remove_invoice.items():
            found_match = str(key)
            replce_y = found_match.replace(found_match, found_match + "/")
            replace_str = replaced.replace(found_match, replce_y)
        invoice_regex = "(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/-\\\\ ][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/-\\\\ ][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/-\\\\ ][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[\\\\ ][/-][\\\\ ][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/][0-9][0-9][/][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[/][0-9][0-9][0-9][0-9][0-9])".replace(
            "[Prefix]", prefix
        )
        r = re.compile(str(invoice_regex), re.MULTILINE)
        matches = [m.group() for m in r.finditer(replace_str)]
        if len(matches) == 0:
            delivery_regex = "(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9])".replace(
                "[Prefix]", delivery_prefix
            )
            replacestr_2 = re.sub("[^a-zA-Z0-9_ ]+", "", message)
            match_deliveries = re.findall(f"({prefix})", replacestr_2)
            hash_remove_delivery = {}
            for match_delivery in match_deliveries:
                replace_d = str(match_delivery)
                if replace_d not in hash_remove_delivery:
                    hash_remove_delivery[replace_d] = ""

            for key, value in hash_remove_delivery.items():
                found_match = str(key)
                replace_y = found_match
                # ReplaceFrom code pending
                replacestr_2 = replacestr_2.replace(found_match, replace_y)

            delivery_r = re.compile(str(delivery_regex), re.MULTILINE)
            delivery_matches = [m.group() for m in delivery_r.finditer(replacestr_2)]
            if len(delivery_matches) == 0:
                order_regex = "(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][-][a-zA-z][a-zA-z][a-zA-z])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][-][a-zA-z 0-9][a-zA-z 0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9][-][0-9])|(([Prefix])[0-9][0-9][0-9][0-9][0-9][0-9])".replace(
                    "[Prefix]", order_prefix
                )
                replacestr_1 = re.sub("[^a-zA-Z0-9_ ]+", "", message)
                matches_invoice1 = re.findall(f"({order_prefix})", replacestr_1)
                hash_remove_order = {}
                for m_e in matches_invoice1:
                    found_match = str(m_e)
                    replce_o = found_match
                    if replce_o not in hash_remove_order:
                        hash_remove_order[replce_o] = ""

                for o_key, o_value in hash_remove_order.items():
                    found_match = str(o_key)
                    replacestr_1.replace(found_match, o_key)

                order_r = re.compile(str(order_regex), re.MULTILINE)
                order_matches = [m.group() for m in order_r.finditer(replacestr_1)]
                x_order = ""
                x1_order = ""
                hash_order = {}
                for order_m in order_matches:
                    found_match = str(order_m)
                    replce_y = found_match.replace(" ", "/")

                    if replce_y not in hash_order:
                        hash_order[replce_y] = ""
                for order_el in hash_order:
                    x_order = str(order_el)
                    filtered_orders.append({"grid_id": i, "invoice_no": x_order})
                    x1_order = x1_order + x_order + ","
                data[i]["FilteredMessageOrder"] = x1_order.rstrip(",")
                if len(x1_order) > 0:
                    data[i]["Type"] = "O"
                else:
                    data[i]["Type"] = "N"

            hash_delivery = {}
            x_delivery = ""
            x1_delivery = ""
            for m_delivery in delivery_matches:
                found_match = str(m_delivery)
                replace_y = found_match.replace("-", "/")
                replace_y = replace_y.replace(" ", "/")
                if replace_y not in hash_delivery:
                    hash_delivery[replace_y] = ""
            for element_deli in hash_delivery:
                x_delivery = str(element_deli)
                filtered_delivery.append({"grid_id": i, "invoice_no": x_delivery})
                x1_delivery = x1_delivery + x_delivery + ","
            data[i]["FilteredMessageDelivery"] = x1_delivery.rstrip(",")
            if len(x1_delivery) > 0:
                data[i]["Type"] = "O"
            else:
                data[i]["Type"] = "N"
        hash_invoice = {}
        x = ""
        x1 = ""
        for mt in matches:
            if mt not in hash_invoice:
                hash_invoice[mt] = ""
        for key, val in hash_invoice.items():
            x = str(key)
            filtered_invoices.append({"grid_id": i, "invoice_no": x})
            x1 = x1 + x + ","
        data[i]["Invoice_Nr"] = x1.rstrip(",")
        if len(x1) > 0:
            data[i]["Type"] = "I"
        else:
            data[i]["Type"] = "N"
    if is_updated:
        data = match_payment_row_data(data, coda_object, filtered_invoices, filtered_orders, filtered_delivery, file_id)
        return data
    data = match_payment_data(data, coda_object, filtered_invoices, filtered_orders, filtered_delivery)
    return data


def match_payment_data(data, coda_object, filtered_invoices, filtered_orders, filtered_delivery):
    f_invoices = []
    for f_invoice in filtered_invoices:
        f_invoices.append(f_invoice["invoice_no"])
    f_orders = []
    for f_invoice in filtered_orders:
        f_orders.append(f_invoice["invoice_no"])

    f_delevery = []
    for f_invoice in filtered_delivery:
        f_delevery.append(f_invoice["invoice_no"])

    new_invoice_dict = {}
    for item in filtered_invoices:
        if item["grid_id"] in new_invoice_dict:
            new_invoice_dict[item["grid_id"]].append(item["invoice_no"])
        else:
            new_invoice_dict[item["grid_id"]] = [(item["invoice_no"])]

    new_order_dict = {}
    for item in filtered_orders:
        if item["grid_id"] in new_order_dict:
            new_order_dict[item["grid_id"]].append(item["invoice_no"])
        else:
            new_order_dict[item["grid_id"]] = [item["invoice_no"]]

    new_delivery_dict = {}
    for item in filtered_delivery:
        if item["grid_id"] in new_delivery_dict:
            new_delivery_dict[item["grid_id"]].append(item["invoice_no"])
        else:
            new_delivery_dict[item["grid_id"]] = [item["invoice_no"]]
    invoices = Invoice.objects.filter(invoice_number__in=f_invoices).values("invoice_number", "invoice_value", "currency_invoice_value", "status__code")
    invoice_orders = InvoiceOrder.objects.filter(order_number__in=f_orders).values(
        "invoice__invoice_number", "order_number", "invoice__currency_invoice_value", "invoice__invoice_value"
    )
    invoice_delivery = Invoice.objects.filter(delivery_no__in=f_delevery).values("invoice_number", "invoice_value", "currency_invoice_value", "status__code", "delivery_no")
    for s in range(len(data)):
        if data[s]["Type"] == "I":
            f1 = []
            for f_invoice in filtered_invoices:
                f1.append(f_invoice["invoice_no"])
            new_invoice_dict = {}
            for item in filtered_invoices:
                if item["grid_id"] in new_invoice_dict:
                    new_invoice_dict[item["grid_id"]] += "," + str(item["invoice_no"])
                else:
                    new_invoice_dict[item["grid_id"]] = str(item["invoice_no"])
            if len(data) > 0:
                if data[s]["Invoice_Nr"] is None or data[s]["Invoice_Nr"] == "":
                    data[s]["matchInvoice"] = "No data"
                    data[s]["match"] = "No data"
                    data[s]["AmountInvoice"] = "No data"
                else:
                    amount = 0
                    list = []
                    for j in new_invoice_dict.keys():
                        if s == int(j):
                            for invoice in invoices:
                                if str(invoice["invoice_number"]) in new_invoice_dict[j]:
                                    if str(coda_object.file_name).endswith(".940"):
                                        amount += invoice["currency_invoice_value"]
                                    else:
                                        amount += invoice["invoice_value"]
                                    if invoice["status__code"] == "INVCLOSED":
                                        if "308" not in list:
                                            list.append("308")
                                    else:
                                        if "307" not in list:
                                            list.append("307")
                                else:
                                    amount += 0
                            else:
                                amount += 0
                    if len(list) == 2:
                        data[s]["match"] = ""
                        data[s]["invoice_status"] = "Partial closed"
                    elif len(list) == 1:
                        if list[0] == "308":
                            data[s]["match"] = ""
                            if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                data[s]["invoice_status"] = "Already closed"
                            else:
                                data[s]["match"] = "Amount check"
                                data[s]["invoice_status"] = "Already closed"
                        else:
                            if amount == 0:
                                data[s]["matchInvoice"] = "Amount check"
                                data[s]["match"] = "Amount check"
                                data[s]["AmountInvoice"] = str(amount)
                            if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                data[s]["matchInvoice"] = "Full"
                                data[s]["match"] = "Full"
                                data[s]["AmountInvoice"] = str(amount)
                            elif Decimal(amount) > Decimal(0) or Decimal(amount) < Decimal(0):
                                data[s]["matchInvoice"] = "Amount check"
                                data[s]["match"] = "Amount check"
                                data[s]["AmountInvoice"] = str(amount)
                            else:
                                data[s]["matchInvoice"] = "No data"
                                data[s]["match"] = "No data"
                                data[s]["AmountInvoice"] = str(amount)
                    else:
                        data[s]["matchInvoice"] = "No data"
                        data[s]["match"] = "No data"
                        data[s]["AmountInvoice"] = str(amount)

        elif data[s]["Type"] == "O":
            for order in invoice_orders:
                if str(order["order_number"]).upper() in str(data[s]["FilteredMessageOrder"]).upper():
                    data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"] + str(order["order_number"]) + ","
            data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"]
            if len(data) > 0:
                if str(data[s]["FilteredMessageOrder"]) == "" or data[s]["FilteredMessageOrder"] is None:
                    data[s]["matchOrder"] = "No data"
                    data[s]["match"] = "No data"
                    data[s]["AmountOrder"] = "0"
                else:
                    amount = 0
                    list = []
                    for o in new_order_dict.keys():
                        if s == int(o):
                            for invoice in invoice_orders:
                                if invoice["order_number"] in new_order_dict[o]:
                                    if str(coda_object.file_name).endswith(".940"):
                                        amount += str(invoice["invoice__currency_invoice_value"]).replace(",", ".")
                                    else:
                                        amount += str(invoice["invoice__invoice_value"]).replace(",", ".")
                                    if invoice["status__code"] == "INVCLOSED":
                                        if "308" not in list:
                                            list.append("308")
                                    else:
                                        if "307" not in list:
                                            list.append("307")
                                    amount += 0
                                else:
                                    amount += 0

                    if len(list) == 2:
                        data[s]["match"] = ""
                        data[s]["Invoice_status"] = "Partial closed"

                    elif len(list) == 1:
                        if list[0] == "308":
                            data[s]["match"] = ""
                            if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                data[s]["Invoice_status"] = "Already closed"

                            else:
                                data[s]["match"] = "Amount check"
                                data[s]["Invoice_status"] = "Already closed"
                        else:
                            if amount == 0:
                                data[s]["matchOrder"] = "Amount check"
                                data[s]["AmountOrder"] = str(amount)
                                data[s]["match"] = "Amount check"

                                if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                    data[s]["matchOrder"] = "Full"
                                    data[s]["match"] = "Full"
                                    data[s]["AmountOrder"] = str(amount)

                                elif Decimal(amount) > Decimal(0) or Decimal(amount) < Decimal(0):
                                    data[s]["matchOrder"] = "Amount check"
                                    data[s]["match"] = "Amount check"
                                    data[s]["AmountOrder"] = str(amount)

                                else:
                                    data[s]["matchOrder"] = "No data"
                                    data[s]["match"] = "No data"
                                    data[s]["AmountOrder"] = str(amount)
                    else:
                        data[s]["matchInvoice"] = "No data"
                        data[s]["match"] = "No data"
                        data[s]["AmountInvoice"] = str(amount)

        elif data[s]["Type"] == "D":
            for delivery in invoice_delivery:
                if str(delivery["delivery_no"]).upper() in str(data[s]["FilteredMessageDelivery"]).upper():
                    data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"] + str(order["invoice_number"]) + ","
            data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"]
            if len(data) > 0:
                if str(data[s]["FilteredMessageDelivery"]) == "" or data[s]["FilteredMessageDelivery"] is None:
                    data[s]["matchDelivery"] = "No data"
                    data[s]["match"] = "No data"
                    data[s]["AmountDelivery"] = str(amount)
                else:
                    amount = 0
                    list = []
                    for d in new_delivery_dict.keys():
                        if s == int(d):
                            for invoice in invoice_delivery:
                                if new_delivery_dict[d] != "" | new_delivery_dict[d] is not None:
                                    if invoice["invoice_number"] in new_delivery_dict[d]:
                                        if str(coda_object.file_name).endswith(".940"):
                                            amount += str(invoice["invoice__currency_invoice_value"]).replace(",", ".")
                                        else:
                                            amount += str(invoice["invoice__invoice_value"]).replace(",", ".")
                                        if invoice["status__code"] == "INVCLOSED":
                                            if "308" not in list:
                                                list.append("308")
                                        else:
                                            if "307" not in list:

                                                list.append("307")
                                    amount += 0

                                amount += 0

                    if len(list) == 2:
                        data[s]["match"] = ""
                        data[s]["Invoice_status"] = "Partial closed"
                    elif len(list) == 1:
                        if list[0] == "308":
                            data[s]["match"] = ""
                            if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                data[s]["Invoice_status"] = "Already closed"
                            else:
                                data[s]["match"] = "Amount check"
                                data[s]["Invoice_status"] = "Already closed"
                        else:
                            if amount == 0:
                                data[s]["matchDelivery"] = "Amount check"
                                data[s]["match"] = "Amount check"
                                data[s]["AmountDelivery"] = str(amount)

                                if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                    data[s]["matchDelivery"] = "Full"
                                    data[s]["match"] = "Full"
                                    data[s]["AmountDelivery"] = str(amount)

                                elif Decimal(amount) > Decimal(0) or Decimal(amount) < Decimal(0):
                                    data[s]["matchDelivery"] = "Amount check"
                                    data[s]["match"] = "Amount check"
                                    data[s]["AmountDelivery"] = str(amount)
                                else:
                                    data[s]["matchDelivery"] = "No data"
                                    data[s]["match"] = "No data"
                                    data[s]["AmountDelivery"] = str(amount)
                    else:
                        data[s]["matchOrder"] = "No data"
                        data[s]["match"] = "No data"
                        data[s]["AmountOrder"] = str(amount)
        else:
            data[s]["match"] = "No data"
    #         if data[s]["match"] == "No data":
    #             name = data[s]["name"] if data[s]["name"] is not None else ""
    #             customer_invoices = (CodaCustomerMapping.objects
    #                                  .select_related("customer_set").filter(bank_customer_name=name)
    #                                          .values("customer_id","customer__invoice_customer__invoice_number",
    #                                             "customer__invoice_customer__invoice_value","customer__invoice_customer__id"))
    #             invoice_values = Util.get_dict_from_queryset("customer__invoice_customer__id","customer__invoice_customer__invoice_number",customer_invoices)
    #             if customer_invoices:
    #                 invoice_amount = Decimal(data[s]["amount"])
    #                 stack = []
    #                 if invoice_amount > 0 :
    #                     for cust in customer_invoices:
    #                         if cust["customer__invoice_customer__id"]:
    #                             custome_data = [{
    #                                 "invoice_value" : Decimal(str(cust["customer__invoice_customer__invoice_value"]).replace(",",".")),
    #                                 "customer_id": cust["customer__invoice_customer__id"]
    #                                             }]
    #                     stack = match_invoice(custome_data, 0, len(custome_data),invoice_amount)
    #                     invoice_number = ""
    #                     for obj in stack:
    #                         result = []
    #                         result.append(invoice_values[int(obj)])
    #                         for row in result:
    #                             invoice_number = invoice_number + invoice_values[int(obj)]
    #                     if len(invoice_number) > 5:
    #                         data[s]["invoice_nr"] = invoice_number
    #                         data[s]["match"] = "Full"
    #                         data[s]["remark"] = ""
    return data


# def match_invoice(data, from_index, end_index,invoice_amount):
#     stack = []
#     stack1 = []
#     sum_stack = 0
#     if Decimal(str(sum_stack)) == invoice_amount:
#         return stack
#     for val in range(end_index):
#         if from_index < end_index and sum_stack != invoice_amount:
#             for inv in data:
#                 if sum_stack + inv["invoice_value"]  <= invoice_amount:
#                     stack.append(inv["invoice_value"])
#                     sum_stack += inv["invoice_value"]
#                     stack1.append(inv["customer_id"])
#                     match_invoice(data, from_index + 1, end_index,invoice_amount)
#                     if sum_stack != invoice_amount:
#                         sum_stack -= stack.pop()
#                         stack1.pop()
#                     else :
#                         break
#     return stack1


def importCodaFile(coda_object):
    coda_file_id = coda_object.id
    file_name = coda_object.file_name
    xml_string = coda_object.xml_string1
    created_by = coda_object.created_by.id
    created_on = str(coda_object.created_on)
    is_deleted = coda_object.is_deleted
    compared_xml_string = coda_object.compared_xml_string2
    azure_payload = {
        "type": "ImportCodaFile",
        "data": {
            "CodaFileId": coda_file_id,
            "CreatedBy": created_by,
            "CreatedDate": created_on,
            "Is_Deleted": is_deleted,
            "File_name": file_name,
            "XMLString": xml_string,
            "ComparedXMLString": compared_xml_string,
        },
    }
    compared_xml_string = Util.xml_generator(compared_xml_string, "newDataSet", "transaction")
    xml_string = Util.xml_generator(xml_string, "transactions", "transaction")
    compared_xml_string = compared_xml_string.decode("utf-8")
    xml_string = xml_string.decode("utf-8")
    data = {"created_by": created_by, "file_name": file_name, "xml_string": xml_string, "compared_xml_string": compared_xml_string}
    token = TOKEN.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token, "Content-Type": "application/json"}
    data = requests.post(settings.EC_PY_URL + "/ecpy/finance/update_coda_file/", headers=headers, data=json.dumps(data))
    azure_payload = json.dumps(azure_payload)
    azure_service(azure_payload)
    return APIResponse(azure_payload)


@api_view(["post"])
def close_invoice(request):
    coda_id = request.data.get("coda_id")
    load_data = request.data.get("data")
    azure_payload = {"type": "CloseInvoice", "data": []}
    for data in load_data:
        name = data["name"]
        amount = data["amount"]
        invoice_nr = data["invoice_nr"]
        azure_payload["data"].append(
            {
                "coda_id": coda_id,
                "name": name,
                "amount": amount,
                "invoice_nr": invoice_nr,
            }
        )
    azure_payload = json.dumps(azure_payload)
    azure_service(azure_payload)
    return APIResponse(data=1, message="invoice closed")


@api_view(["POST"])
def update_payment_xml(request):
    coda_id = request.data.get("coda_id")
    remark = request.data.get("remarks")
    invoice_nr = request.data.get("invoice_nr")
    file_id = int(request.data.get("file_id"))
    user_id = request.data.get("user_id")
    coda = CodaFile.objects.get(id=coda_id)
    coda_file_name = CodaFile.objects.filter(id=coda_id).values("file_name").first()
    data = json.loads(coda.compared_xml_string2)
    if int(data[file_id]["id"]) == int(file_id):
        if remark != "undefined":
            data[file_id]["remark"] = remark
        if invoice_nr != "undefined":
            data[file_id]["Invoice_Nr"] = invoice_nr
    updated_row = filtered_payment_data([data[file_id]], coda, True, file_id)
    updated_row[0]["id"] = file_id
    data[file_id] = updated_row[0]
    coda.compared_xml_string2 = json.dumps(data)
    coda.save()
    if coda:
        azure_payload = {"type": "UpdatePaymentXmlRemarks", "data": {"user_id": user_id, "coda_id": coda_id, "coda_file_name": coda_file_name["file_name"]}}  # "data" : decode_data
        azure_payload = json.dumps(azure_payload)
        # azure_service(azure_payload)
    return APIResponse(code=1, message="Remarks inserted.")


@api_view(["POST"])
def change_match_status(request):
    unmatched_data = request.data.get("unmatched_data")
    user_id = request.data.get("user_id")
    coda_id = request.data.get("coda_id")
    coda = CodaFile.objects.get(id=coda_id)
    data = json.loads(coda.compared_xml_string2)
    azure_payload = {"type": "changeMatchStatus", "data": {"user_id": user_id, "coda_id": coda_id, "payment_browser_unmatched_data": [], "compared_xml_string": None}}
    for unmatch_data in unmatched_data:
        customer_name = unmatch_data["name"]
        bank_account_nr = unmatch_data["bank_account_nr"]
        amount = unmatch_data["amount"]
        message = unmatch_data["message"]
        match = unmatch_data["match"]
        invoice_status = unmatch_data["invoice_status"]
        invoice_nr = unmatch_data["invoice_nr"]
        remarks = unmatch_data["name"]
        data_id = unmatch_data["id"]
        if data[data_id]["match"] == "No data":
            data[data_id]["match"] = "Unmatch"
            coda.compared_xml_string2 = json.dumps(data)
        else:
            return APIResponse(code=0, message="Match status already Unmatch(s).")
        payment_browser_unmatched_data = PaymentBrowserUnmatch.objects.create(
            coda_file_id=int(coda_id),
            customer_name=customer_name,
            bank_account_nr=bank_account_nr,
            amount=amount,
            message=message,
            remarks=remarks,
            created_by_id=int(user_id),
            invoice_nos=invoice_nr,
            bank_name=customer_name,
        )
        coda.compared_xml_string = json.dumps(data)
        coda.save()
        if coda:
            azure_payload["data"]["payment_browser_unmatched_data"].append(
                {
                    "coda_file_id": payment_browser_unmatched_data.id,
                    "customer_name": payment_browser_unmatched_data.customer_name,
                    "bank_account_nr": payment_browser_unmatched_data.bank_account_nr,
                    "amount": payment_browser_unmatched_data.amount,
                    "message": payment_browser_unmatched_data.message,
                    "create_by_id": payment_browser_unmatched_data.created_by_id,
                    "invoice_nr": payment_browser_unmatched_data.invoice_nos,
                    "bank_name": payment_browser_unmatched_data.bank_name,
                    "remarks": payment_browser_unmatched_data.remarks,
                }
            )
    data = azure_payload["data"]["payment_browser_unmatched_data"]
    token = TOKEN.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.post(settings.EC_PY_URL + "/ecpy/finance/update_unmatch_data/", headers=headers, data=json.dumps(data))
    azure_payload["data"]["compared_xml_string"] = coda.compared_xml_string
    azure_payload = json.dumps(azure_payload)
    # azure_service(azure_payload)
    return APIResponse(code=1, message="Match status changed.")


def match_payment_row_data(data, coda_object, filtered_invoices, filtered_orders, filtered_delivery, file_id):
    f_invoices = []
    for f_invoice in filtered_invoices:
        f_invoices.append(f_invoice["invoice_no"])
    f_orders = []
    for f_invoice in filtered_orders:
        f_orders.append(f_invoice["invoice_no"])

    f_delevery = []
    for f_invoice in filtered_delivery:
        f_delevery.append(f_invoice["invoice_no"])

    new_invoice_dict = {}
    for item in filtered_invoices:
        if item["grid_id"] in new_invoice_dict:
            new_invoice_dict[item["grid_id"]].append(item["invoice_no"])
        else:
            new_invoice_dict[item["grid_id"]] = [(item["invoice_no"])]

    new_order_dict = {}
    for item in filtered_orders:
        if item["grid_id"] in new_order_dict:
            new_order_dict[item["grid_id"]].append(item["invoice_no"])
        else:
            new_order_dict[item["grid_id"]] = [item["invoice_no"]]

    new_delivery_dict = {}
    for item in filtered_delivery:
        if item["grid_id"] in new_delivery_dict:
            new_delivery_dict[item["grid_id"]].append(item["invoice_no"])
        else:
            new_delivery_dict[item["grid_id"]] = [item["invoice_no"]]
    invoices = Invoice.objects.filter(invoice_number__in=f_invoices).values("invoice_number", "invoice_value", "currency_invoice_value", "status__code")
    invoice_orders = InvoiceOrder.objects.filter(order_number__in=f_orders).values(
        "invoice__invoice_number", "order_number", "invoice__currency_invoice_value", "invoice__invoice_value"
    )
    invoice_delivery = Invoice.objects.filter(delivery_no__in=f_delevery).values("invoice_number", "invoice_value", "currency_invoice_value", "status__code", "delivery_no")
    for s in range(len(data)):
        # transaction = root.getchildren()[s]
        id = data[s]["id"]
        if int(id) == int(file_id):
            if data[s]["Type"] == "I":
                f1 = []
                for f_invoice in filtered_invoices:
                    f1.append(f_invoice["invoice_no"])
                new_invoice_dict = {}
                for item in filtered_invoices:
                    if item["grid_id"] in new_invoice_dict:
                        new_invoice_dict[item["grid_id"]] += "," + str(item["invoice_no"])
                    else:
                        new_invoice_dict[item["grid_id"]] = str(item["invoice_no"])
                if len(data) > 0:
                    if data[s]["Invoice_Nr"] is None or data[s]["Invoice_Nr"] == "":
                        data[s]["matchInvoice"] = "No data"
                        data[s]["match"] = "No data"
                        data[s]["AmountInvoice"] = "No data"
                    else:
                        amount = 0
                        list = []
                        for j in new_invoice_dict.keys():
                            if s == int(j):
                                for invoice in invoices:
                                    if str(invoice["invoice_number"]) in new_invoice_dict[j]:
                                        if str(coda_object.file_name).endswith(".940"):
                                            amount += invoice["currency_invoice_value"]
                                        else:
                                            amount += invoice["invoice_value"]
                                        if invoice["status__code"] == "INVCLOSED":
                                            if "308" not in list:
                                                list.append("308")
                                        else:
                                            if "307" not in list:
                                                list.append("307")
                                    else:
                                        amount += 0                          
                        if len(list) == 2:
                            root[s].find("match").text = ""
                            root[s].find("Invoice_status").text = "Partial closed"
                        elif len(list) == 1:
                            if list[0] == "308":
                                root[s].find("match").text = ""
                                if Decimal(amount) == Decimal(str(root[s].find("amount").text)):
                                    root[s].find("Invoice_status").text = "Already closed"
                                else:
                                    amount += 0
                        if len(list) == 2:
                            data[s]["match"] = ""
                            data[s]["invoice_status"] = "Partial closed"

                        elif len(list) == 1:
                            if list[0] == "308":
                                data[s]["match"] = ""
                                if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                    data[s]["invoice_status"] = "Already closed"
                                else:
                                    data[s]["match"] = "Amount check"
                                    data[s]["invoice_status"] = "Already closed"
                            else:
                                if amount == 0:
                                    data[s]["matchInvoice"] = "Amount check"
                                    data[s]["match"] = "Amount check"
                                    data[s]["AmountInvoice"] = str(amount)
                                if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                    data[s]["matchInvoice"] = "Full"
                                    data[s]["match"] = "Full"
                                    data[s]["AmountInvoice"] = str(amount)
                                elif Decimal(amount) > Decimal(0) or Decimal(amount) < Decimal(0):
                                    data[s]["matchInvoice"] = "Amount check"
                                    data[s]["match"] = "Amount check"
                                    data[s]["AmountInvoice"] = str(amount)
                                else:
                                    data[s]["matchInvoice"] = "No data"
                                    data[s]["match"] = "No data"
                                    data[s]["AmountInvoice"] = str(amount)
                        else:
                            data[s]["matchInvoice"] = "No data"
                            data[s]["match"] = "No data"
                            data[s]["AmountInvoice"] = str(amount)

            elif data[s]["Type"] == "O":
                for order in invoice_orders:
                    if str(order["order_number"]).upper() in str(data[s]["FilteredMessageOrder"]).upper():
                        data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"] + str(order["order_number"]) + ","
                data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"]
                if len(data) > 0:
                    if str(data[s]["FilteredMessageOrder"]) == "" or data[s]["FilteredMessageOrder"] is None:
                        data[s]["matchOrder"] = "No data"
                        data[s]["match"] = "No data"
                        data[s]["AmountOrder"] = "0"
                    else:
                        amount = 0
                        list = []
                        for o in new_order_dict.keys():
                            if s == int(o):
                                for invoice in invoice_orders:
                                    if invoice["order_number"] in new_order_dict[o]:
                                        if str(coda_object.file_name).endswith(".940"):
                                            amount += str(invoice["invoice__currency_invoice_value"]).replace(",", ".")
                                        else:
                                            amount += str(invoice["invoice__invoice_value"]).replace(",", ".")
                                        if invoice["status__code"] == "INVCLOSED":
                                            if "308" not in list:
                                                list.append("308")
                                        else:
                                            if "307" not in list:
                                                list.append("307")
                                        amount += 0
                                    else:
                                        amount += 0

                        if len(list) == 2:
                            data[s]["match"] = ""
                            data[s]["Invoice_status"] = "Partial closed"

                        elif len(list) == 1:
                            if list[0] == "308":
                                data[s]["match"] = ""
                                if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                    data[s]["Invoice_status"] = "Already closed"

                                else:
                                    data[s]["match"] = "Amount check"
                                    data[s]["Invoice_status"] = "Already closed"
                            else:
                                if amount == 0:
                                    data[s]["matchOrder"] = "Amount check"
                                    data[s]["AmountOrder"] = str(amount)
                                    data[s]["match"] = "Amount check"

                                    if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                        data[s]["matchOrder"] = "Full"
                                        data[s]["match"] = "Full"
                                        data[s]["AmountOrder"] = str(amount)

                                    elif Decimal(amount) > Decimal(0) or Decimal(amount) < Decimal(0):
                                        data[s]["matchOrder"] = "Amount check"
                                        data[s]["match"] = "Amount check"
                                        data[s]["AmountOrder"] = str(amount)

                                    else:
                                        data[s]["matchOrder"] = "No data"
                                        data[s]["match"] = "No data"
                                        data[s]["AmountOrder"] = str(amount)
                        else:
                            data[s]["matchInvoice"] = "No data"
                            data[s]["match"] = "No data"
                            data[s]["AmountInvoice"] = str(amount)

            elif data[s]["Type"] == "D":
                for delivery in invoice_delivery:
                    if str(delivery["delivery_no"]).upper() in str(data[s]["FilteredMessageDelivery"]).upper():
                        data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"] + str(order["invoice_number"]) + ","
                data[s]["Invoice_Nr"] = data[s]["Invoice_Nr"]
                if len(data) > 0:
                    if str(data[s]["FilteredMessageDelivery"]) == "" or data[s]["FilteredMessageDelivery"] is None:
                        data[s]["matchDelivery"] = "No data"
                        data[s]["match"] = "No data"
                        data[s]["AmountDelivery"] = str(amount)
                    else:
                        amount = 0
                        list = []
                        for d in new_delivery_dict.keys():
                            if s == int(d):
                                for invoice in invoice_delivery:
                                    if new_delivery_dict[d] != "" | new_delivery_dict[d] is not None:
                                        if invoice["invoice_number"] in new_delivery_dict[d]:
                                            if str(coda_object.file_name).endswith(".940"):
                                                amount += str(invoice["invoice__currency_invoice_value"]).replace(",", ".")
                                            else:
                                                amount += str(invoice["invoice__invoice_value"]).replace(",", ".")
                                            if invoice["status__code"] == "INVCLOSED":
                                                if "308" not in list:
                                                    list.append("308")
                                            else:
                                                if "307" not in list:

                                                    list.append("307")
                                        amount += 0

                                    amount += 0

                        if len(list) == 2:
                            data[s]["match"] = ""
                            data[s]["Invoice_status"] = "Partial closed"
                        elif len(list) == 1:
                            if list[0] == "308":
                                data[s]["match"] = ""
                                if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                    data[s]["Invoice_status"] = "Already closed"
                                else:
                                    data[s]["match"] = "Amount check"
                                    data[s]["Invoice_status"] = "Already closed"
                            else:
                                if amount == 0:
                                    data[s]["matchDelivery"] = "Amount check"
                                    data[s]["match"] = "Amount check"
                                    data[s]["AmountDelivery"] = str(amount)

                                    if Decimal(amount) == Decimal(str(data[s]["amount"])):
                                        data[s]["matchDelivery"] = "Full"
                                        data[s]["match"] = "Full"
                                        data[s]["AmountDelivery"] = str(amount)

                                    elif Decimal(amount) > Decimal(0) or Decimal(amount) < Decimal(0):
                                        data[s]["matchDelivery"] = "Amount check"
                                        data[s]["match"] = "Amount check"
                                        data[s]["AmountDelivery"] = str(amount)
                                    else:
                                        data[s]["matchDelivery"] = "No data"
                                        data[s]["match"] = "No data"
                                        data[s]["AmountDelivery"] = str(amount)
                        else:
                            data[s]["matchOrder"] = "No data"
                            data[s]["match"] = "No data"
                            data[s]["AmountOrder"] = str(amount)
    return data
