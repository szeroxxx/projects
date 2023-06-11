import datetime
import xml.etree.ElementTree as ET

from django.db.models import CharField, Count, F, Func, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.utils import timezone
from payment.models import CodaFile, CodaTransaction, PaymentBrowserUnmatch
from rest_framework import renderers
from rest_framework.decorators import api_view
from sales.models import Invoice, InvoiceOrder, PeppolInvoice

from base.service import Service
from base.util import Util


@api_view(["get"])
def payment_export(request):
    coda_id = request.GET.get("coda_id")
    file_type = request.GET.get("file_type")
    coda_file = CodaFile.objects.filter(id=coda_id).values("compared_xml_string2").first()
    xml_string = coda_file["compared_xml_string2"]
    response = Util.get_xml(coda_file["compared_xml_string2"])
    if xml_string:
        if file_type != "xml":
            headers = [
                {"title": "id"},
                {"title": "Name"},
                {"title": "Bank Account Nr."},
                {"title": "Amount"},
                {"title": "Message"},
                {"title": "Match"},
                {"title": "Invoice status"},
                {"title": "Invoice Nr(s)"},
                {"title": "AmountInvoice"},
                {"title": "MatchInvoice"},
                {"title": "Type"},
                {"title": "Manuallyadded"},
                {"title": "Remark"},
                {"title": "tr_date"},
                {"title": "FilteredMessageOrder"},
            ]
            records = response["data"]
            return Util.export_to_xls(headers, records, "Payment.xls")
        else:
            records = response["data"]
            return Util.download_xml_file(records, root_tag_name=None, item_tag_name=None, file_name="Payment.xml")
    return Util.export_to_xls(headers, records, "Payment.xls")


@api_view(["get"])
def payment_browser_export(request):
    ids = request.GET.get("coda_transaction_id")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    response = (
        CodaTransaction.objects.filter(id__in=ids)
        .values(
            "id",
            "invoice__id",
            "ec_customer_id",
            "invoice_no",
            "customer_name",
            "invoice__status__desc",
            # "invoice__currency__code",
            "invoice__invoice_address__country__name",
            "amount",
            "invoice__invoice_value",
            "bank_account_no",
            "bank_name",
        )
        .annotate(
            created_on=Func(F("created_on"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
        )
    )
    headers = [
        {"title": "CodaTransaction Id"},
        {"title": "Invoice id"},
        {"title": "Ec customer id"},
        {"title": "invoice no."},
        {"title": "customer_name"},
        {"title": "status_code"},
        {"title": "country_name"},
        {"title": "amount"},
        {"title": "invoice_value"},
        {"title": "bank_account_no"},
        {"title": "bank_name"},
        {"title": "created_on"},
    ]
    return Util.export_to_xls(headers, response, "Payment_browser.xls")


@api_view(["get"])
def payment_unmatch_export(request):
    ids = request.GET.get("payment_unmatch_id")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    response = (
        PaymentBrowserUnmatch.objects.filter(id__in=ids)
        .values(
            "id",
            "customer_name",
            "bank_account_nr",
            "bank_name",
            "amount",
            "message",
            "invoice_nos",
            "remarks",
        )
        .annotate(
            created_on=Func(F("created_on"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
            created_by=Concat(F("created_by__first_name"), Value(" "), F("created_by__last_name")),
        )
    )
    headers = [
        {"title": "PaymentBrowser Id"},
        {"title": "customer_name"},
        {"title": "bank_account_nr"},
        {"title": "bank_name"},
        {"title": "amount"},
        {"title": "message"},
        {"title": "invoice_nos"},
        {"title": "remarks"},
        {"title": "created_on"},
        {"title": "created_by"},
    ]
    return Util.export_to_xls(headers, response, "payment_unmatch.xls")


@api_view(["get"])
def e_invoice_export(request):
    ids = request.GET.get("invoice_id")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    response = Service.invoice(ids)
    headers = [
        {"title": "InvoiceiId"},
        {"title": "CustomerId"},
        {"title": "InvoiceNr"},
        {"title": "Exchange_Rate"},
        {"title": "Currency_Symbol"},
        {"title": "FinancialBlock"},
        {"title": "CreditLimit"},
        {"title": "Cust_Credit_Limit"},
        {"title": "Customer"},
        {"title": "CustomerType"},
        {"title": "HandCompany"},
        {"title": "RootCompany"},
        {"title": "InvoiceValue"},
        {"title": "Cust_InvoiceValue"},
        {"title": "Status"},
        {"title": "DeliveryNr"},
        {"title": "VAT"},
        {"title": "Country"},
        {"title": "AddressLine1"},
        {"title": "AccountingNo"},
        {"title": "AddressLine2"},
        {"title": "Postal_Code"},
        {"title": "City"},
        {"title": "Email"},
        {"title": "Phone"},
        {"title": "Fax"},
        {"title": "HandCompanyId"},
        {"title": "OrderNumber"},
        {"title": "DeliverInvoiceByPost"},
        {"title": "IsInvoiceDeliver"},
        {"title": "InvoiceDelivery"},
        {"title": "Outstanding"},
        {"title": "Cust_Outstanding"},
        {"title": "InvoiceData"},
        {"title": "InvoiceDueDate"},
        {"title": "LastRemDate"},
        {"title": "PaymentDate"},
    ]
    return Util.export_to_xls(headers, response, "E_invoice.xls")


@api_view(["get"])
def proforma_invoice_export(request):
    ids = request.GET.get("invoice_id")
    file_type = request.GET.get("file_type")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    invoice = Service.invoice(ids)
    pop_keys = [
        "id",
        "customer__id",
        "transport_cost",
        "currency__code",
        "financial_block",
        "customer__credit_limit",
        "customer__customer_credit_limit",
        "hand_company__name",
        "customer__is_root__name",
        "currency_invoice_value",
        "country__name",
        "street_address1",
        "cust_account_no",
        "street_address2",
        "postal_code",
        "invoice_city",
        "invoice_email",
        "invoice_phone",
        "invoice_fax",
        "hand_company__id",
        "order_nrs",
        "customer__is_deliver_invoice_by_post",
        "is_invoice_deliver",
        "customer__invo_delivery",
        "outstanding",
        "customer_outstanding",
        "invoice_created_on",
        "invoice_due_date",
        "last_rem_date",
        "payment_date",
    ]
    response = []
    for i in invoice:
        [i.pop(key) for key in pop_keys]
        response.append(i)
    headers = [
        {"title": "invoice_number"},
        {"title": "customer"},
        {"title": "customer_type"},
        {"title": "invoice_value"},
        {"title": "status"},
        {"title": "delivery_no"},
        {"title": "vat_no"},
    ]
    if file_type == "csv":
        return Util.download_csv_file(headers, response, "Invoice_proforma")
    if file_type == "xml":
        return Util.download_xml_file(response, root_tag_name=None, item_tag_name=None, file_name="Invoice_proforma.xml")
    if file_type == "xls":
        return Util.export_to_xls(headers, response, "Invoice_proforma.xls")
    return Util.export_to_xls(headers, response, "Invoice_proforma.xls")


@api_view(["get"])
def customer_invoice_export(request):
    ids = request.GET.get("invoice_id")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    response = Service.invoice(ids)
    headers = [
        {"title": "InvoiceiId"},
        {"title": "CustomerId"},
        {"title": "InvoiceNr"},
        {"title": "Exchange_Rate"},
        {"title": "Currency_Symbol"},
        {"title": "FinancialBlock"},
        {"title": "CreditLimit"},
        {"title": "Cust_Credit_Limit"},
        {"title": "Customer"},
        {"title": "CustomerType"},
        {"title": "HandCompany"},
        {"title": "RootCompany"},
        {"title": "InvoiceValue"},
        {"title": "Cust_InvoiceValue"},
        {"title": "Status"},
        {"title": "DeliveryNr"},
        {"title": "VAT"},
        {"title": "Country"},
        {"title": "AddressLine1"},
        {"title": "AccountingNo"},
        {"title": "AddressLine2"},
        {"title": "Postal_Code"},
        {"title": "City"},
        {"title": "Email"},
        {"title": "Phone"},
        {"title": "Fax"},
        {"title": "HandCompanyId"},
        {"title": "OrderNumber"},
        {"title": "DeliverInvoiceByPost"},
        {"title": "IsInvoiceDeliver"},
        {"title": "InvoiceDelivery"},
        {"title": "Outstanding"},
        {"title": "Cust_Outstanding"},
        {"title": "InvoiceData"},
        {"title": "InvoiceDueDate"},
        {"title": "LastRemDate"},
        {"title": "PaymentDate"},
    ]
    return Util.export_to_xls(headers, response, "customer_invoice.xls")


@api_view(["get"])
def custom_invoice_export(request):
    response = []
    headers = [
        {"title": "Delivery Nr."},
        {"title": "Customer"},
        {"title": "Delivered on."},
        {"title": "Delivery Country"},
        {"title": "Ship tracking nr."},
        {"title": "Order nr."},
    ]

    return Util.export_to_xls(headers, response, "custom_invoice.xls")


@api_view(["get"])
def peppol_invoice_export(request):
    ids = request.GET.get("invoice_id")
    file_type = request.GET.get("file_type")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    response = (
        PeppolInvoice.objects.filter(id__in=ids)
        .values(
            "id",
            "invoice__customer__id",
            "invoice__invoice_number",
            "invoice__customer__ec_customer_id",
            # "invoice__invoice_created_on",
            "pe_status",
            "invoice__customer__name",
            "invoice__status__desc",
            "invoice__hand_company__name",
            "invoice__customer__vat_no",
            "result",
            "error",
            "invoice__is_peppol_verified",
        )
        .annotate(
            invoice_date=Func(F("invoice__invoice_created_on"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
        )
    )
    headers = [
        {"title": "PeppolId"},
        {"title": "CustomerId"},
        {"title": "EC CustomerId"},
        {"title": "Invoice Nr.."},
        {"title": "Status"},
        {"title": "Customer"},
        {"title": "Invoice status"},
        {"title": "Handling company"},
        {"title": "Vat"},
        {"title": "Result"},
        {"title": "Error/Remarks"},
        {"title": "Peppol id verified"},
        {"title": "Invoice Date"},
    ]
    xml_record = []
    for i in response:
        xml_record.append(i)
    if file_type == "xml":
        return Util.download_xml_file(xml_record, root_tag_name="newDataSet", item_tag_name="Table", file_name="Peppol_invoice.xml")
    return Util.export_to_xls(headers, response, "peppol_invoice.xls")


@api_view(["get"])
def search_invoice_export(request):
    ids = request.GET.get("invoice_id")
    file_type = request.GET.get("file_type")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    response = Service.invoice(ids)
    xml_record = []
    for invoice in response:
        xml_record.append(
            {
                "InvoiceId": invoice["id"],
                "CustomerID": invoice["customer__id"],
                "InvoiceNr": invoice["invoice_number"],
                "InvoiceDate": invoice["invoice_created_on"],
                "Exchange_Rate": invoice["transport_cost"],
                "Currency_Symbol": invoice["currency__code"],
                "Outstanding": invoice["outstanding"],
                "Cust_Outstanding": invoice["customer_outstanding"],
                "InvoiceDueDate": invoice["invoice_due_date"],
                "FinancialBlocked": invoice["financial_block"],
                "CreditLimit": invoice["customer__credit_limit"],
                "Cust_CreditLimit": invoice["customer__customer_credit_limit"],
                "Customer": invoice["customer__name"],
                "CustomerType": invoice["customer__customer_type__name"],
                "HC": invoice["hand_company__name"],
                "RootCompany": invoice["customer__is_root__name"],
                "InvoiceValue": invoice["invoice_value"],
                "Cust_InvoiceValue": invoice["currency_invoice_value"],
                "Status": invoice["status__desc"],
                "DeliveryNr": invoice["delivery_no"],
                "VAT": invoice["customer__vat_no"],
                "Country": invoice["country__name"],
                "AddressLine1": invoice["street_address1"],
                "Accounting_x0020_no": invoice["cust_account_no"],
                "AddressLine2": invoice["street_address2"],
                "Postal_Code": invoice["postal_code"],
                "City": invoice["invoice_city"],
                "Email": invoice["invoice_email"],
                "Phone": invoice["invoice_phone"],
                "Fax": invoice["invoice_fax"],
                "HandCompanyId": invoice["hand_company__id"],
                "OrderNumber": invoice["order_nrs"],
                "DeliverInvoiceByPost": invoice["customer__is_deliver_invoice_by_post"],
                "IsInvoiceDeliver": invoice["is_invoice_deliver"],
                "InvoiceDelivery": invoice["customer__invo_delivery"],
            }
        )
    headers = [
        {"title": "InvoiceiId"},
        {"title": "CustomerId"},
        {"title": "InvoiceNr"},
        {"title": "Exchange_Rate"},
        {"title": "Currency_Symbol"},
        {"title": "FinancialBlock"},
        {"title": "CreditLimit"},
        {"title": "Cust_Credit_Limit"},
        {"title": "Customer"},
        {"title": "CustomerType"},
        {"title": "HandCompany"},
        {"title": "RootCompany"},
        {"title": "InvoiceValue"},
        {"title": "Cust_InvoiceValue"},
        {"title": "Status"},
        {"title": "DeliveryNr"},
        {"title": "VAT"},
        {"title": "Country"},
        {"title": "AddressLine1"},
        {"title": "AccountingNo"},
        {"title": "AddressLine2"},
        {"title": "Postal_Code"},
        {"title": "City"},
        {"title": "Email"},
        {"title": "Phone"},
        {"title": "Fax"},
        {"title": "HandCompanyId"},
        {"title": "OrderNumber"},
        {"title": "DeliverInvoiceByPost"},
        {"title": "IsInvoiceDeliver"},
        {"title": "InvoiceDelivery"},
        {"title": "Outstanding"},
        {"title": "Cust_Outstanding"},
        {"title": "InvoiceData"},
        {"title": "InvoiceDueDate"},
        {"title": "LastRemDate"},
        {"title": "PaymentDate"},
    ]
    headers_down = headers[0:15] + headers[-6:]
    pop_keys = [
        "delivery_no",
        "customer__vat_no",
        "country__name",
        "street_address1",
        "cust_account_no",
        "street_address2",
        "postal_code",
        "invoice_city",
        "invoice_email",
        "invoice_phone",
        "invoice_fax",
        "hand_company__id",
        "order_nrs",
        "customer__is_deliver_invoice_by_post",
        "is_invoice_deliver",
        "customer__invo_delivery",
    ]
    if file_type == "csv":
        csv_record = []
        for i in response:
            [i.pop(key) for key in pop_keys]
            csv_record.append(i)
        return Util.download_csv_file(headers_down, csv_record, "Search_invoice.csv")
    elif file_type == "xml":
        return Util.download_xml_file(xml_record, root_tag_name="newDataSet", item_tag_name="Table", file_name="Search_invoice.xml")
    else:
        xls_record = []
        for i in response:
            [i.pop(key) for key in pop_keys]
            xls_record.append(i)
        return Util.export_to_xls(headers_down, xls_record, "Search_invoice.xls")


@api_view(["get"])
def pkf_booking_generate(request):
    is_hungarian = request.GET.get("is_hungarian")
    ids = request.GET.get("invoice_id")
    ids = [x for x in ids.split(",")]
    ids.remove("")
    invoices = (
        Invoice.objects.filter(id__in=ids)
        .values(
            "id",
            "customer__name",
            "invoice_number",
            "hand_company__name",
            "postal_code",
            "street_address1",
            "street_address2",
            "vat_percentage",
            "invoice_address__street_name",
            "invoice_address__street_no",
            "customer__vat_no",
            "original_invoice_number",
            "curr_rate",
            "invoice_value",
        )
        .annotate(
            export_inv_cnt=Count("id"),
            invoice_created_on=Func(F("invoice_created_on"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
            invoice_due_date=Func(F("invoice_due_date"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
        )
    )
    orders = InvoiceOrder.objects.filter(invoice__id__in=ids).values(
        "id",
        "order_unit_value",
        "invoice_amount",
        "quantity",
        "ord_trp_value",
    )
    export_inv_cnt = invoices.count()
    starting_inv_num = invoices[0]["invoice_number"]
    ending_inv_num = invoices[export_inv_cnt - 1]["invoice_number"]
    current_date = str(datetime.date.today())

    if is_hungarian == "false":
        root = ET.Element("invoices")

        if export_inv_cnt > 0:
            ET.SubElement(root, "export_date").text = current_date
            ET.SubElement(root, "export_inv_cnt").text = str(export_inv_cnt)
            ET.SubElement(root, "start_time").text = current_date
            ET.SubElement(root, "end_time").text = current_date
            ET.SubElement(root, "starting_inv_num").text = str(starting_inv_num)
            ET.SubElement(root, "ending_inv_num").text = str(ending_inv_num)

            for inv in invoices:
                invoice = ET.SubElement(root, "invoice")

                header = ET.SubElement(invoice, "header")
                ET.SubElement(header, "invnumber").text = inv["invoice_number"]
                ET.SubElement(header, "invtype").text = ""
                ET.SubElement(header, "invdate").text = inv["invoice_created_on"]
                ET.SubElement(header, "proddate").text = ""

                invissuer = ET.SubElement(invoice, "invissuer")
                ET.SubElement(invissuer, "taxnumber").text = "11162973-2-10"
                ET.SubElement(invissuer, "eutaxnumber").text = "HU11162973"
                ET.SubElement(invissuer, "name").text = "Eurocircuits Kft."

                address = ET.SubElement(invissuer, "address")
                ET.SubElement(address, "postalcode").text = "3324"
                ET.SubElement(address, "town").text = "Felsőtárkány"
                ET.SubElement(address, "publicplacename").text = "Berva"
                ET.SubElement(address, "publicplacetype").text = "völgy"
                ET.SubElement(address, "streetnumber").text = "hrsz.: 2401/9"

                customer = ET.SubElement(invoice, "customer")
                if inv["customer__vat_no"] != "":
                    ET.SubElement(customer, "taxnumber").text = inv["customer__vat_no"]
                    ET.SubElement(customer, "name").text = "<![CDATA[{}]>".format(inv["customer__name"])

                    address = ET.SubElement(customer, "address")
                    ET.SubElement(address, "postalcode").text = inv["postal_code"]
                    ET.SubElement(address, "town").text = "<![CDATA[{}]>".format(inv[""])

                    if inv["invoice_address__street_name"] != "":
                        ET.SubElement(address, "publicplacename").text = "<![CDATA[{}]>".format(inv["invoice_address__street_name"])

                    if inv["invoice_address__street_no"] != "":
                        ET.SubElement(address, "streetnumber").text = "<![CDATA[{}]>".format(inv["invoice_address__street_no"])

                    product_service_item = ET.SubElement(invoice, "product_service_item")
                    for order in orders:
                        ET.SubElement(product_service_item, "productname").text = "<![CDATA[{}]>".format(inv[""])
                        ET.SubElement(product_service_item, "classnumber").text = ""
                        ET.SubElement(product_service_item, "quantity").text = str(order["quantity"])
                        ET.SubElement(product_service_item, "unit").text = str(order["orderer_unit_value"])
                        ET.SubElement(product_service_item, "netprice").text = str(order["invoice_amount"])
                        ET.SubElement(product_service_item, "netunitprice").text = ""

                        if order["ord_trp_value"] != "" and ord["ord_trp_value"] != "0.00":
                            ET.SubElement(product_service_item, "productname").text = "<![CDATA[Delivery cost]]>"
                            ET.SubElement(product_service_item, "classnumber").text = ""
                            ET.SubElement(product_service_item, "quantity").text = "1"
                            ET.SubElement(product_service_item, "unit").text = "1"
                            ET.SubElement(product_service_item, "netprice").text = str(order["ord_trp_value"])
                            ET.SubElement(product_service_item, "netunitprice").text = str(order["ord_trp_value"])

                correctiveinv = ET.SubElement(invoice, "correctiveinv")

                if inv["original_invoice_number"] != "":
                    ET.SubElement(correctiveinv, "originalnumber").text = inv["original_invoice_number"]

                cluases = ET.SubElement(invoice, "cluases")
                ET.SubElement(cluases, "exemption").text = "true"

                optional = ET.SubElement(invoice, "optional")
                ET.SubElement(optional, "duedate").text = inv["invoice_due_date"]
                ET.SubElement(optional, "paymentmode").text = ""
                ET.SubElement(optional, "currency").text = "EUR"
                ET.SubElement(optional, "invform").text = ""
                ET.SubElement(optional, "issuerbankacc").text = ""

                summary = ET.SubElement(invoice, "summary")
                vat = ET.SubElement(summary, "VAT")
                ET.SubElement(vat, "netprice").text = str(inv["invoice_value"])
                ET.SubElement(vat, "taxrate").text = str(inv["curr_rate"])
                ET.SubElement(vat, "tax").text = ""
                ET.SubElement(vat, "grossprice").text = ""

                totalprice = ET.SubElement(summary, "totalprice")
                ET.SubElement(totalprice, "totalnetprice").text = ""
                ET.SubElement(totalprice, "totaltaxprice").text = ""
                ET.SubElement(totalprice, "totalgrossprice").text = ""
    else:
        root = ET.Element("szamlak")
        if export_inv_cnt > 0:
            ET.SubElement(root, "export_datuma").text = current_date
            ET.SubElement(root, "export_szla_db").text = str(export_inv_cnt)
            ET.SubElement(root, "kezdo_ido").text = current_date
            ET.SubElement(root, "zaro_ido").text = current_date
            ET.SubElement(root, "kezdo_szla_szam").text = str(starting_inv_num)
            ET.SubElement(root, "zaro_szla_szam").text = str(ending_inv_num)

            for inv in invoices:
                invoice = ET.SubElement(root, "szamla")

                header = ET.SubElement(invoice, "fejlec")
                ET.SubElement(header, "szlasorszam").text = inv["invoice_number"]
                ET.SubElement(header, "szlatipus").text = ""
                ET.SubElement(header, "szladatum").text = inv["invoice_created_on"]
                ET.SubElement(header, "teljdatum").text = ""

                invissuer = ET.SubElement(invoice, "szamlakibocsato")
                ET.SubElement(invissuer, "adoszam").text = "11162973-2-10"
                ET.SubElement(invissuer, "kozadoszam").text = "HU11162973"
                ET.SubElement(invissuer, "nev").text = "Eurocircuits Kft."

                address = ET.SubElement(invissuer, "cim")
                ET.SubElement(address, "iranyitoszam").text = "3324"
                ET.SubElement(address, "telepules").text = "Felsőtárkány"
                ET.SubElement(address, "kozterulet_neve").text = "Berva"
                ET.SubElement(address, "kozterulet_jellege").text = "völgy"
                ET.SubElement(address, "hazszam").text = "hrsz.: 2401/9"

                customer = ET.SubElement(invoice, "vevo")
                if inv["customer__vat_no"] != "":
                    ET.SubElement(customer, "taxnumber").text = inv["customer__vat_no"]
                    ET.SubElement(customer, "nev").text = "<![CDATA[{}]>".format(inv["customer__name"])

                    address = ET.SubElement(customer, "cim")
                    ET.SubElement(address, "iranyitoszam").text = inv["postal_code"]
                    ET.SubElement(address, "telepules").text = "<![CDATA[{}]>".format(inv[""])

                    if inv["invoice_address__street_name"] != "":
                        ET.SubElement(address, "kozterulet_neve").text = "<![CDATA[{}]>".format(inv["invoice_address__street_name"])

                    if inv["invoice_address__street_no"] != "":
                        ET.SubElement(address, "hazszam").text = "<![CDATA[{}]>".format(inv["invoice_address__street_no"])

                    product_service_item = ET.SubElement(invoice, "termek_szolgaltatas_tetelek")
                    for order in orders:
                        ET.SubElement(product_service_item, "termeknev").text = "<![CDATA[{}]>".format(inv[""])
                        ET.SubElement(product_service_item, "besorszam").text = ""
                        ET.SubElement(product_service_item, "menny").text = str(order["quantity"])
                        ET.SubElement(product_service_item, "mertekegys").text = str(order["order_unit_value"])
                        ET.SubElement(product_service_item, "nettoar").text = str(order["invoice_amount"])
                        ET.SubElement(product_service_item, "nettoegysar").text = ""

                        if order["ord_trp_value"] != "" and order["ord_trp_value"] != "0.00":
                            ET.SubElement(product_service_item, "termeknev").text = "<![CDATA[Delivery cost]]>"
                            ET.SubElement(product_service_item, "besorszam").text = ""
                            ET.SubElement(product_service_item, "menny").text = "1"
                            ET.SubElement(product_service_item, "mertekegys").text = "1"
                            ET.SubElement(product_service_item, "nettoar").text = str(order["ord_trp_value"])
                            ET.SubElement(product_service_item, "nettoegysar").text = str(order["ord_trp_value"])

                correctiveinv = ET.SubElement(invoice, "modosito_szla")
                if inv["original_invoice_number"] != "":
                    ET.SubElement(correctiveinv, "eredeti_sorszam").text = inv["original_invoice_number"]

                cluases = ET.SubElement(invoice, "zaradekok")
                ET.SubElement(cluases, "adoment_hiv").text = "true"

                optional = ET.SubElement(invoice, "nem_kotelezo")
                ET.SubElement(optional, "fiz_hatarido").text = inv["invoice_due_date"]
                ET.SubElement(optional, "fiz_mod").text = ""
                ET.SubElement(optional, "penznem").text = "EUR"
                ET.SubElement(optional, "szla_forma").text = ""
                ET.SubElement(optional, "kibocsato_bankszla").text = ""

                summary = ET.SubElement(invoice, "osszesites")
                vat = ET.SubElement(summary, "afarovat")
                ET.SubElement(vat, "nettoar").text = str(inv["invoice_value"])
                ET.SubElement(vat, "adokulcs").text = str(inv["curr_rate"])
                ET.SubElement(vat, "adoertek").text = ""
                ET.SubElement(vat, "bruttoar").text = ""

                totalprice = ET.SubElement(summary, "vegosszeg")
                ET.SubElement(totalprice, "nettoarossz").text = ""
                ET.SubElement(totalprice, "afaertekossz").text = ""
                ET.SubElement(totalprice, "bruttoarossz").text = ""
    response = HttpResponse(ET.tostring(root).decode("utf8"), content_type="application/xml")
    response["Content-Disposition"] = "attachment; filename=%s" % "pkf_booking.xml"
    return response
