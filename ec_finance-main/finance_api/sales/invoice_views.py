import json
from logging import exception
import xml.etree.cElementTree as ET
from datetime import datetime, timedelta

import requests
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import views as base_views
from base.models import CodeTable, Currency
from base.sb_send import azure_service
from base.util import Util
from customer.models import Country, Customer
from customer.models import User as ECUser
from django.conf import settings
from django.db import transaction
from django.db.models import Case, F, Q, Value, When
from django.db.models.aggregates import Sum
from django.utils import timezone
from finance_api.rest_config import APIResponse, CustomPagination
from payment.models import CodaFile, CodaTransaction, Payment, PaymentRegistration
from rest_framework import generics, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from sales.filter import HuTaxInvoiceFilter, PeppolInvocieFilter, SearchInvoiceFilter
from sales.models import CustomInvoice, HutaxInvoice, Invoice, InvoiceDiscount, InvoiceOrder, PeppolInvoice
from sales.serializers import (
    CreditStatusSerializer,
    CustomsSerializer,
    HuTaxSerializer,
    InvoiceDiscountSerializer,
    InvoiceOrderSerializer,
    InvoiceSerializer,
    PeppolInvoiceSerializer,
    PKFBookingSerializer,
    SearchInvoiceSerializer,
    UpdateInvoiceSerializer,
    XeroBookingSerilizer,
)


class InvoiceView(viewsets.ModelViewSet):
    serializer_class = SearchInvoiceSerializer
    filterset_class = SearchInvoiceFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        query = Q()
        status = self.request.GET.get("status")
        name = self.request.GET.get("name")
        e_invoice = self.request.GET.get("e_invoice")
        page = self.request.GET.get("page")
        customer_invoice = self.request.GET.get("customer_invoice")
        if status == "pending":
            query.add(Q(status__code="INVPENDING"), query.connector)
        elif status == "overdue":
            query.add(~Q(status__code="INVCLOSED"), query.connector)
            query.add(Q(invoice_due_date__lt=datetime.now()), query.connector)
        elif status == "wrt_off":
            query.add(Q(secondry_status__code="Write Off"), query.connector)
        elif status == "overpaid" or status == "closed":
            query.add(Q(amount_paid__gt=F("invoice_value")) | query.add(Q(status__code="INVCLOSED"), query.connector), query.connector)
        if name and name != "undefined":
            query.add(Q(customer__name__iexact=name.strip()), query.connector)
        if e_invoice:
            query.add(Q(is_e_invoice=e_invoice), query.connector)
        if customer_invoice == "true":
            query.add(Q(is_invoice_deliver=False) & Q(is_e_invoice=False), query.connector)
        queryset = (
            Invoice.objects.filter(query)
            .values(
                "id",
                "invoice_number",
                "status__desc",
                "customer__name",
                "invoice_created_on",
                "invoice_value",
                "customer__credit_limit",
                "customer__customer_credit_limit",
                "last_rem_date",
                "curr_rate",
                "outstanding_amount",
                "invoice_due_date",
                "payment_date",
                "is_invoice_deliver",
                "amount_paid",
                "cust_amount_paid",
                "delivery_condition",
                "secondry_status__desc",
                "street_address1",
                "street_address2",
                "invoice_city",
                "invoice_fax",
                "invoice_email",
                "postal_code",
                "invoice_phone",
                "country__name",
                "customer__vat_no",
                "customer__is_root",
                "customer__customer_type__name",
                "currency__code",
                "currency_outstanding_amount",
                "hand_company__name",
                "customer__account_number",
                "delivery_no",
                "currency_invoice_value",
                "customer__invo_delivery",
                "payment_date",
                "customer__id",
                "customer__ec_customer_id",
                "financial_block",
                "customer__is_root__name",
                "order_nrs",
                "packing",
                "is_finished",
            )
            .annotate(
                is_deliver_invoice_by_post=Case(When(customer__is_deliver_invoice_by_post=True, then=Value("Yes")), default=Value("No")),
                outstanding=Sum(F("invoice_value") - F("amount_paid")),
                customer_outstanding=Sum(F("currency_invoice_value") - F("cust_amount_paid")),
            )
        )
        return queryset

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def create_invoice(self, request):
        codes = Util.get_codes("code_table")
        invoice = request.data.get("data")
        history = request.data.get("history")
        user_id = request.data.get("user_id")
        c_ip = base_views.get_client_ip(request)
        if invoice is None:
            return APIResponse(code=2, message="No fetch invoice details")
        currency = Currency.objects.filter(code=invoice["currency"]).values("id").first()
        customer = Customer.objects.filter(ec_customer_id=invoice["ec_customer_id"]).values("id").first()
        # root_company = Customer.objects.filter(ec_customer_id=invoice["root_companyId"]).values("id").first()
        if customer is None:
            customer = Customer.objects.create(
                name=invoice["customername"],
                customer_type_id=codes[invoice["customer_type"]],
                ec_customer_id=invoice["ec_customer_id"],
                credit_limit=invoice["creditLimit"],
                customer_credit_limit=invoice["creditLimit_Customer"],
                invo_delivery=invoice["invoices_delivery"],
                vat_no=invoice["vat_number"],
                account_number=invoice["cust_account_no"],
                is_deliver_invoice_by_post=invoice["is_invoice_by_post"],
            )

        else:
            Customer.objects.filter(id=customer["id"]).update(
                name=invoice["customername"],
                customer_type_id=codes[invoice["customer_type"]],
                ec_customer_id=invoice["ec_customer_id"],
                credit_limit=invoice["creditLimit"],
                customer_credit_limit=invoice["creditLimit_Customer"],
                invo_delivery=invoice["invoices_delivery"],
                vat_no=invoice["vat_number"],
                account_number=invoice["cust_account_no"],
                is_deliver_invoice_by_post=invoice["is_invoice_by_post"],
            )
        customer = Customer.objects.filter(ec_customer_id=invoice["ec_customer_id"]).values("id").first()
        hand_company = Customer.objects.filter(ec_customer_id=invoice["hand_company"]).values("id").first()
        created_by = ECUser.objects.filter(customer__ec_customer_id=invoice["ec_customer_id"]).values("id").first()
        country = Country.objects.filter(code=invoice["country_code"]).values("id").first()
        country_id = None
        if country is None:
            country = Country.objects.create(
                code=invoice["country_code"],
                name=invoice["Countryname"],
            )
            country_id = country.id
        else:
            country_id = country["id"]
        invoice["status"] = codes[invoice["status"]] if invoice["status"] in codes else None
        invoice["customer"] = customer["id"] if customer else None
        invoice["hand_company"] = hand_company["id"] if hand_company else None
        invoice["created_by"] = created_by["id"] if created_by else None
        invoice["currency"] = currency["id"] if currency else None
        invoice["secondry_status"] = codes[invoice["secondry_status"]] if invoice["secondry_status"] in codes else None
        invoice["credit_limit"] = invoice["creditLimit"]
        invoice["customer_credit_limit"] = invoice["creditLimit_Customer"]
        invoice["delivery_no"] = invoice["delivery_no"]
        invoice["country"] = country_id
        invoice["postal_code"] = invoice["postal_code"]
        invoice["street_address1"] = invoice["address_line_1"]
        invoice["street_address2"] = invoice["address_line_2"]
        invoice["invoice_city"] = invoice["city"]
        invoice["invoice_phone"] = invoice["InvoiceTelephone"]
        invoice["ec_invoice_id"] = invoice["InvoiceId"]
        if invoice["invoice_due_date"] == "":
            invoice.pop("invoice_due_date")
        if invoice["invoice_close_date"] == "":
            invoice.pop("invoice_close_date")
        if invoice["last_rem_date"] == "":
            invoice.pop("last_rem_date")
        if invoice["payment_date"] == "":
            invoice.pop("payment_date")
        if invoice["invoice_created_on"] == "":
            invoice.pop("invoice_created_on")
        if invoice["created_on"] == "":
            invoice.pop("created_on")
        invoice_id = None
        if Invoice.objects.filter(invoice_number=invoice["invoice_number"]).exists():
            invoice_instance = Invoice.objects.get(invoice_number=invoice["invoice_number"])
            serializer = UpdateInvoiceSerializer(instance=invoice_instance, data=invoice)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            invoice_id = invoice_instance.id
            log_views.insert("sales", "invoice", [invoice_id], AuditAction.INSERT, None, c_ip, "Invoice updated", history["userName"], history["actionCode"])
        else:
            serializer = InvoiceSerializer(data=invoice)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            invoice_id = serializer.data["id"]
            log_views.insert("sales", "invoice", [invoice_id], AuditAction.INSERT, None, c_ip, "Invoice created", history["userName"], history["actionCode"])
        orders_bulk = []
        customer_bulk = []
        customer_invoice = list(CustomInvoice.objects.filter(invoice_id=invoice_id).values_list("invoice_id", flat=True))
        if "CustomerInvoice" in invoice:
            for customer in invoice["CustomerInvoice"]:
                if invoice_id not in customer_invoice:
                    customer_bulk.append(
                        CustomInvoice(
                            invoice_id=invoice_id,
                            code=customer["code"],
                            harm_code=customer["harm_code"],
                            intrastat=customer["intrastat"],
                            country_of_origin=customer["country_of_origin"],
                            weight=customer["weight"],
                            value=customer["value"],
                            value_curr=customer["value_curr"],
                            vat_percentage=customer["vat_percentage"],
                        )
                    )
            CustomInvoice.objects.bulk_create(customer_bulk)
        orders = list(InvoiceOrder.objects.filter(invoice_id=invoice_id).values_list("order_number", flat=True))
        for order in invoice["Orders"]:
            if order["order_number"] not in orders:
                orders_bulk.append(
                    InvoiceOrder(
                        invoice_id=invoice_id,
                        ec_order_id=order["ec_order_id"],
                        order_number=order["order_number"],
                        order_unit_value=order["order_unit_value"],
                        quantity=order["quantity"],
                        invoice_amount=order["invoice_amount"],
                        ord_trp_value=order["ord_trp_value"],
                        order_vnit_value_curr=order["order_vnit_value_curr"],
                        invoice_amount_curr=order["invoice_amount_curr"],
                        is_reduce_vat=order["is_reduce_vat"],
                        invoice_ref=order["invoice_ref"],
                    )
                )
            else:
                orders.remove(order["order_number"])
        InvoiceOrder.objects.bulk_create(orders_bulk)
        InvoiceOrder.objects.filter(order_number__in=orders).delete()
        return APIResponse(code=1, message="Invoice inserted")

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def edit_invoice(self, request):
        invoice_number = request.data.get("invoice_number")
        invoice_created_on = request.data.get("invoice_date")
        invoice_due_date = request.data.get("invoice_due_date")
        invoice_total = request.data.get("invoice_total")
        delivery_date = request.data.get("delivery_date")
        customs_line = request.data.get("custom_line")
        order_line = request.data.get("order_line")
        discount_line = request.data.get("discount_line")
        invoice_id = request.data.get("invoice_id")
        total_weight = request.data.get("custom_weight")
        total_customs = request.data.get("total_customs")
        remarks = request.data.get("remarks")
        root = ET.Element("MetaData")
        ET.SubElement(root, "VATMessage").text = request.data.get("vat_message")
        ET.SubElement(root, "VATMessageHC").text = request.data.get("vat_message_handling")
        meta_data = ET.tostring(root).decode("utf-8")

        for order in order_line:
            instance = InvoiceOrder.objects.get(id=order["id"])
            order_serializer = InvoiceOrderSerializer(instance=instance, data=order)
            order_serializer.is_valid(raise_exception=True)
            self.perform_update(order_serializer)

        for custom in customs_line:
            instance = CustomInvoice.objects.get(id=custom["id"])
            custom_serializer = CustomsSerializer(instance=instance, data=custom)
            custom_serializer.is_valid(raise_exception=True)
            self.perform_update(custom_serializer)

        for discount in discount_line:
            if "id" in discount:
                instance = InvoiceDiscount.objects.get(id=discount["id"])
                discount_serializer = InvoiceDiscountSerializer(instance=instance, data=discount)
                discount_serializer.is_valid(raise_exception=True)
                self.perform_update(discount_serializer)
            else:
                discount["invoice_id"] = invoice_id
                invoice_discount = InvoiceDiscount(**discount)
                invoice_discount.save()

        Invoice.objects.filter(id=invoice_id).update(
            invoice_number=invoice_number,
            invoice_created_on=invoice_created_on,
            invoice_due_date=invoice_due_date,
            invoice_value=invoice_total,
            delivery_date=delivery_date,
            weight=total_weight,
            custom_value=total_customs,
            remarks=remarks,
            meta_data=meta_data,
        )
        # order_serializer.
        # payload = {
        #     "type":"EditInvoice",
        #     "order_line":order_line,
        #     "customs_line":customs_line,
        #     "invoice_data":{
        #         "invoice_number":,
        #         "invoice_created_on":,
        #         "invoice_due_date":,
        #         "delivery_date":,
        #         "weight":,
        #         "custom_value":,
        #         "remarks":,
        #         "meta_data":,
        #         "invoice_value":,
        #     }
        #     }
        return APIResponse(code=1, message="Invoice successfully updated.")

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def generate_credit_on_invoice(self, request):
        try:
            invoice_data = request.data.get("data")
            order_line = request.data.get("order_line")
            customs_line = request.data.get("custom_line")
            invoice_id = request.data.get("invoice_id")
            invoice = Invoice.objects.get(pk=invoice_id)

            invoice.pk = None
            invoice.invoice_number = "EN19/TEST"
            invoice.invoice_due_date = invoice_data["invoice_due_date"] if "invoice_due_date" in invoice_data else None
            invoice.delivery_date = invoice_data["delivery_date"] if "delivery_date" in invoice_data else None
            invoice.invoice_created_on = invoice_data["credit_note_date"] if "credit_note_date" in invoice_data else None
            invoice.transport_cost = invoice_data["transport_cost"] if "transport_cost" in invoice_data else 0.000
            invoice.weight = invoice_data["custom_weight"] if "custom_weight" in invoice_data else 0.000
            invoice.remarks = invoice_data["remark"] if "remark" in invoice_data else None
            invoice.custom_value = invoice_data["custom_value"] if "custom_value" in invoice_data else 0.000
            invoice.invoice_value = invoice_data["total_amount"] if "total_amount" in invoice_data else 0.000
            invoice.vat_percentage = invoice_data["vat_percentage"] if "vat_percentage" in invoice_data else 0.000
            invoice.save()

            for order in order_line:
                order["invoice_id"] = invoice.id
                invoice_order = InvoiceOrder(**order)
                invoice_order.save()

            for custom in customs_line:
                # del custom["invoice"]
                custom["invoice_id"] = invoice.id
                custom_invoice = CustomInvoice(**custom)
                custom_invoice.save()

            # payload = {
            #     "type":"EditInvoice",
            #     "order_line":order_line,
            #     "customs_line":customs_line,
            #     "invoice_data":{
            #         "invoice_number":,
            #         "invoice_created_on":,
            #         "invoice_due_date":,
            #         "delivery_date":,
            #         "weight":,
            #         "custom_value":,
            #         "remarks":,
            #         "meta_data":,
            #         "transport_cost":,
            #         "invoice_value":,
            #         "vat_percentage":,
            #     }
            #     }
            return APIResponse(code=1, message="Invoice successfully generated.")
        except:
            return APIResponse(code=0, message="Invoice number already exists.")

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def invoice_discount_apply_and_remove(self, request):
        # invoice_id = request.data.get("invoice_id")
        # invoice_number = request.data.get("invoice_number")
        # discount_line = request.data.get("discount_line")
        state = request.data.get("state")
        discount_ids = request.data.get("discount_ids")
        discount_code = request.data.get("discount_code")
        msg = ""
        if state == "apply" and discount_code:
            url = settings.EC_PY_URL + "/ecpy/finance/get_discount_details/" + discount_code + "/"
            token = Util.get_ec_py_token()
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers).json()
            if "code" not in response:
                return APIResponse(code=1, message="Discount code applied successfully.", data=response["data"])
            return APIResponse(code=0, message="Please check discount code. ")
        else:
            if discount_ids is None:
                return APIResponse(code=0, message="Please select at least one record. ")
            InvoiceDiscount.objects.filter(id__in=discount_ids).delete()
            msg = "Discount removed. "
        return APIResponse(code=1, message=msg)


class OrderLines(generics.ListAPIView):
    serializer_class = InvoiceOrderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        invoice_id = self.request.GET.get("ids")
        query = Q()
        if invoice_id:
            query.add(Q(invoice_id=int(invoice_id)), query.connector)
        queryset = InvoiceOrder.objects.filter(query)
        return queryset


class Customs(generics.ListAPIView):
    serializer_class = CustomsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        invoice_ids = self.request.GET.get("ids")
        query = Q()
        if invoice_ids:
            query.add(Q(invoice__id=invoice_ids), query.connector)
        queryset = CustomInvoice.objects.filter(query)
        return queryset


class InvoiceDiscountView(generics.ListAPIView):
    serializer_class = InvoiceDiscountSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        invoice_id = self.request.GET.get("invoice_id")
        query = Q()
        if invoice_id:
            query.add(Q(invoice__id=invoice_id), query.connector)
        queryset = InvoiceDiscount.objects.filter(query)
        return queryset


@api_view(["post"])
def update_sec_status(request):
    c_ip = base_views.get_client_ip(request)
    user_id = request.data.get("user_id")
    invoice_number = request.data.get("invoice_number")
    invoice_id = request.data.get("invoice_id")
    status_id = request.data.get("status_id")
    if invoice_number and status_id:
        Invoice.objects.filter(invoice_number=invoice_number).update(secondry_status_id=status_id)
        desc = CodeTable.objects.filter(id=status_id).values("code").first()
        log_views.insert("sales", "invoice", [invoice_id], AuditAction.UPDATE, user_id, c_ip, "Invoice secondary status updated", None, desc["code"])
    azure_payload = {"type": "secondaryStatusUpdate", "user_id": user_id, "invoice_number": invoice_number, "secondary_status": desc["code"]}
    azure_payload = json.dumps(azure_payload)
    azure_service(azure_payload)
    return APIResponse(code=1, message="Secondary Status Updated")


@api_view(["post"])
def change_status(request):
    invoice_number = request.data.get("invoice_number")
    invoice_id = request.data.get("invoice_id")
    status_id = request.data.get("status_id")
    user_id = request.data.get("user_id")
    c_ip = base_views.get_client_ip(request)
    if invoice_number and status_id:
        Invoice.objects.filter(invoice_number=invoice_number).update(status_id=status_id)
        desc = CodeTable.objects.filter(id=status_id).values("code").first()
        log_views.insert("sales", "invoice", [invoice_id], AuditAction.UPDATE, user_id, c_ip, "Invoice status changed", None, desc["code"])
    azure_payload = {"type": "statusUpdate", "user_id": user_id, "invoice_number": invoice_number, "status": desc["code"]}
    azure_payload = json.dumps(azure_payload)
    azure_service(azure_payload)
    return APIResponse(code=1, message="Status Changed")


@api_view(["post"])
def grant_days(request):
    invoice_number = request.data.get("invoice_number")
    invoice_due_date = request.data.get("invoice_due_date")
    invoice_id = request.data.get("invoice_id")
    user_id = request.data.get("user_id")
    days = request.data.get("days")
    date = datetime.strptime(invoice_due_date, "%d/%m/%Y %H:%M:%S")
    update_invoice_due_date = date + timedelta(days=days)
    c_ip = base_views.get_client_ip(request)
    if invoice_number and days:
        Invoice.objects.filter(invoice_number=invoice_number).update(invoice_due_date=update_invoice_due_date)
        log_views.insert("sales", "invoice", [invoice_id], AuditAction.UPDATE, user_id, c_ip, "Grant days update", None)
    azure_payload = {"type": "grantdays", "invoice_number": invoice_number, "days": days, "user_id": user_id}
    azure_payload = json.dumps(azure_payload)
    azure_service(azure_payload)
    return APIResponse(code=1, message="Days Granted")


class CreditStatus(generics.ListAPIView):
    serializer_class = CreditStatusSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        customer_id = self.request.GET.get("customer_id")
        ec_customer_id = self.request.GET.get("ec_customer_id")
        queryset = (
            Invoice.objects.filter(status__code="INVPENDING", customer__ec_customer_id=ec_customer_id)
            .values(
                "id",
                "invoice_number",
                "invoice_created_on",
                "invoice_due_date",
                "outstanding_amount",
                "currency_invoice_value",
                "invoice_value",
                "amount_paid",
                "cust_amount_paid",
                "customer__credit_limit",
                "customer__customer_credit_limit",
            )
            .annotate(
                outstanding=Sum(F("invoice_value") - F("amount_paid")),
                customer_outstanding=Sum(F("currency_invoice_value") - F("cust_amount_paid")),
            )
        )
        return queryset


@api_view(["get"])
def get_credit_status(request):
    ec_customer_id = request.GET.get("ec_customer_id")
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.post(settings.EC_PY_URL + "/ecpy/finance/get_credit_status/" + ec_customer_id, headers=headers).json()
    return APIResponse(data["data"])


class PeppolInvoiceView(viewsets.ModelViewSet):
    serializer_class = PeppolInvoiceSerializer
    filterset_class = PeppolInvocieFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        query = Q()
        status = self.request.GET.get("peppol_status")
        if status == "error":
            query.add(Q(pe_status="ERROR"), query.connector)
        elif status == "ok":
            query.add(Q(pe_status="OK"), query.connector)
        elif status == "not":
            query.add(Q(pe_status=None), query.connector)
        queryset = PeppolInvoice.objects.filter(query).values(
            "id",
            "invoice__invoice_number",
            "invoice__invoice_created_on",
            "invoice__customer__name",
            "invoice__status__desc",
            "invoice__hand_company__name",
            "invoice__customer__vat_no",
            "invoice__is_peppol_verified",
            "invoice__customer__id",
            "invoice__customer__ec_customer_id",
            "result",
            "error",
            "pe_status",
        )
        return queryset

    @action(detail=False, methods=["post"])
    def create_peppolinvoice(self, request):
        invoice = PeppolInvoice.objects.filter(invoice__invoice_number=request.data["invoice_number"]).values("id").first()
        invoice_id = Invoice.objects.filter(invoice_number=request.data["invoice_number"]).values("id").first()
        if invoice_id is not None:
            if invoice is None:
                peppol_invoice = PeppolInvoice.objects.create(
                    invoice_id=invoice_id["id"],
                    pe_status=request.data["pe_status"],
                    result=request.data["result"],
                    error=request.data["error"],
                )
                peppol_invoice.save()
            else:
                PeppolInvoice.objects.filter(invoice__invoice_number=request.data["invoice_number"]).update(
                    pe_status=request.data["pe_status"],
                    result=request.data["result"],
                    error=request.data["error"],
                )
        else:
            return APIResponse(code=0, message="Invoice number is not exist")

        return APIResponse(code=1, message="Peppol invoice created")


class HuTaxService(viewsets.ModelViewSet):
    serializer_class = HuTaxSerializer
    pagination_class = CustomPagination
    filterset_class = HuTaxInvoiceFilter
    # queryset = (HutaxInvoice.objects.values("id"))

    def get_queryset(self):
        query = Q()
        status = self.request.GET.get("status")
        if status == "error":
            query.add(Q(hu_status="Error"), query.connector)
        if status == "warm":
            query.add(Q(hu_status="Warm"), query.connector)
        if status == "ok":
            query.add(Q(hu_status="Ok"), query.connector)
        if status == "not_sent":
            query.add(Q(hu_status="NotSent"), query.connector)
        queryset = HutaxInvoice.objects.filter(query).values(
            "id",
            "invoice__invoice_number",
            "invoice__customer__name",
            "invoice__invoice_created_on",
            "result",
            "status_time",
            "created_on",
            "hu_status",
            "transaction_id",
            "invoice",
        )
        return queryset

    @action(detail=False, methods=["post"])
    def create_hu_taxservice(self, request):
        invoice = HutaxInvoice.objects.filter(invoice__invoice_number=request.data["invoice_number"]).values("id").first()
        invoice_id = Invoice.objects.filter(invoice_number=request.data["invoice_number"]).values("id").first()
        if invoice_id is not None:
            if invoice is None:
                hutaxservice = HutaxInvoice.objects.create(
                    invoice_id=invoice_id["id"],
                    hu_status=request.data["hu_status"],
                    transaction_id=request.data["transaction_id"],
                    file_path=request.data["file_path"],
                    index_number=request.data["index_number"],
                    order_count=request.data["order_count"],
                    status_time=request.data["status_time"],
                    result=request.data["result"],
                    error=request.data["error"],
                    original_invoice_number=request.data["original_invoice_number"],
                    vat_no=request.data["vat_no"],
                )
                hutaxservice.save()
            else:
                HutaxInvoice.objects.filter(invoice__invoice_number=request.data["invoice_number"]).update(
                    hu_status=request.data["hu_status"],
                    transaction_id=request.data["transaction_id"],
                    file_path=request.data["file_path"],
                    index_number=request.data["index_number"],
                    order_count=request.data["order_count"],
                    status_time=request.data["status_time"],
                    result=request.data["result"],
                    error=request.data["error"],
                    original_invoice_number=request.data["original_invoice_number"],
                    vat_no=request.data["vat_no"],
                )
        else:
            return APIResponse(code=0, message="Invoice number is not exist")

        return APIResponse(code=1, message="HU tax service created")


class PKFBooking(generics.ListAPIView):
    serializer_class = PKFBookingSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        prefix = self.request.GET.get("prefix")
        from_number = self.request.GET.get("from_number")
        is_date = self.request.GET.get("is_date")
        to_number = self.request.GET.get("to_number")
        query = Q()
        if from_date != "undefined" and to_date != "undefined" and is_date == "true":
            query.add(Q(invoice_created_on__range=(from_date, to_date)), query.connector)
        else:
            from_invoice_nr = prefix + "/" + from_number
            to_invoice_nr = prefix + "/" + to_number
            query.add(Q(invoice_number__range=(from_invoice_nr, to_invoice_nr)), query.connector)
        queryset = Invoice.objects.filter(query).values(
            "id",
            "ec_invoice_id",
            "customer__name",
            "invoice_number",
            "hand_company__name",
            "invoice_created_on",
            "invoice_due_date",
            "postal_code",
            "street_address1",
            "street_address2",
            "vat_percentage",
            "invoice_address__street_name",
            "invoice_address__street_no",
            "customer__ec_customer_id",
        )
        return queryset


@api_view(["post"])
def submit_close_invoice(request):
    total_amount = request.data.get("total_amount")
    currency_rate = request.data.get("currency_rate")
    customer_id = request.data.get("customer_id")
    ec_customer_id = request.data.get("ec_customer_id")
    paid_on = request.data.get("paid_on")
    payment_mode = request.data.get("payment_mode")
    user_id = request.data.get("user_id")
    row_values = json.loads(request.data.get("row_values"))
    c_ip = base_views.get_client_ip(request)
    base_total_amount = round(float(total_amount) / float(currency_rate), 3)
    currency_id = None
    # payment_registration(request, row_values=row_values, invoice_type="close_invoice", currency_id=currency_id)
    if request.data.get("currency_id"):
        currency_id = Currency.objects.filter(code=request.data.get("currency_id")).values("id").first()["id"]
    payment = Payment.objects.create(
        customer_id=customer_id, currency_id=currency_id, currency_rate=currency_rate, total_amount=total_amount, currency_total_amount=base_total_amount, payment_mode=payment_mode
    )
    payment_registration = []
    azure_payload = {
        "type": "CloseInvoice",
        "data": {
            "total_amount": total_amount,
            "currency_factor": currency_rate,
            "paid_on": paid_on,
            "ec_customer_id": ec_customer_id,
            "payment_mode": payment_mode,
            "invoices": [],
        },
    }
    object_ids = []
    for value in row_values:
        object_ids.append(value["invoice_id"])
        payment_registration.append(
            PaymentRegistration(
                payment=payment,
                customer_id=customer_id,
                amount=value["new_payment"],
                transfer_type="C",
                reference="",
                ref_document_do="",
                invoice_id=value["invoice_id"],
                payment_difference_type=value["payment_deference_type"],
                payment_date=None,
                balance_on_date=0.000,
                remark="",
                created_by_id=user_id,
                username=None,
                currency_amount=value["currency_amount"],
                currency_balance_on_date=0.000,
                paid_on=paid_on,
                currency_id=currency_id,
                currency_rate=currency_rate,
                currency_total_amount=0.000,
            )
        )
        azure_payload["data"]["invoices"].append(
            {
                "new_payment": value["new_payment"],
                "invoice_number": value["invoice_number"],
                "ec_invoice_id": value["ec_invoice_id"],
                "is_down_payment": False,
                "outstanding_amount": value["outstanding"],
                "Payment_difference_type": value["payment_deference_type"],
                "balance": "",
            }
        )
        status = CodeTable.objects.filter(code=value["payment_deference_type"]).values("id").first()
        Invoice.objects.filter(id=value["invoice_id"]).update(amount_paid=value["new_payment"], cust_amount_paid=value["new_payment"], status_id=status["id"], paid_on=paid_on)
    azure_payload = json.dumps(azure_payload)
    azure_service(azure_payload)
    PaymentRegistration.objects.bulk_create(payment_registration)
    log_views.insert("sales", "invoice", object_ids, AuditAction.UPDATE, user_id, c_ip, "Invoice closed.", document_no=str(payment.id))
    return APIResponse(code=1, message="Invoice Closed.")


@api_view(["post"])
def close_coda_invoices(request):
    user_id = request.data.get("user_id")
    coda_id = request.data.get("coda_id")
    file_name = request.data.get("file_name")
    c_ip = base_views.get_client_ip(request)
    row_values = json.loads(request.data.get("row_values"))
    coda_files = CodaFile.objects.get(id=coda_id)
    file_data = json.loads(coda_files.compared_xml_string2)

    for row in row_values:
        # coda_values = {"customer_name":row["customer_name"],"amount":row["amaunt"],"message":row["message"] ,"bank_ac_no":row["bank_account_number"], "file_id":row["id"]}
        # payment_registration(request,invoice_nr=row["invoice_number"],invoice_type="coda_invoice",coda_values=coda_values)
        file_id = row["id"]
        invoice_nr = row["invoice_nr"].split(",")
        total_amount = row["total_amount"]
        invoices = Invoice.objects.filter(invoice_number__in=invoice_nr).values(
            "id",
            "currency_id",
            "ec_invoice_id",
            "cust_amount_paid",
            "invoice_number",
            "currency__code",
            "curr_rate",
            "customer_id",
            "currency_invoice_value",
            "customer__ec_customer_id",
        )
        payment = Payment.objects.create(
            customer_id=invoices[0]["customer_id"], currency_id=invoices[0]["currency_id"], currency_rate=invoices[0]["curr_rate"], total_amount=total_amount
        )
        payment_registration = []
        coda_transaction = []
        now = timezone.now()
        azure_payload = {
            "type": "CloseInvoice",
            "data": {
                "total_amount": str(total_amount),
                "currency_factor": str(invoices[0]["curr_rate"]),
                "paid_on": str(now),
                "ec_customer_id": invoices[0]["customer__ec_customer_id"],
                "payment_mode": "",
                "invoices": [],
            },
        }
        coda_transaction.append(
            CodaTransaction(
                customer_id=invoices[0]["customer_id"],
                invoice_id=invoices[0]["id"],
                customer_name=row["customer_name"],
                amount=row["amaunt"],
                message=row["message"],
                invoice_no=row["invoice_nr"],
                bank_account_no=row["bank_account_number"],
                ec_customer_id=invoices[0]["customer__ec_customer_id"],
            )
        )
        object_ids = []
        for value in invoices:
            object_ids.append(value["id"])
            new_payment = value["currency_invoice_value"] / value["curr_rate"]
            payment_registration.append(
                PaymentRegistration(
                    payment=payment,
                    customer_id=value["customer_id"],
                    amount=new_payment,
                    transfer_type="C",
                    reference="",
                    ref_document_do="",
                    invoice_id=value["id"],
                    payment_difference_type="close",
                    payment_date=None,
                    balance_on_date=0.000,
                    remark="",
                    created_by_id=user_id,
                    username=None,
                    currency_amount=value["currency_invoice_value"],
                    currency_balance_on_date=0.000,
                    paid_on=now,
                    currency_id=value["currency_id"],
                    currency_rate=value["curr_rate"],
                    currency_total_amount=0.000,
                )
            )
            azure_payload["data"]["invoices"].append(
                {
                    "new_payment": str(new_payment),
                    "invoice_number": value["invoice_number"],
                    "ec_invoice_id": value["ec_invoice_id"],
                    "is_down_payment": False,
                    "outstanding_amount": str((value["currency_invoice_value"] / value["cust_amount_paid"])) if value["cust_amount_paid"] else "0.00",
                    "Payment_difference_type": "Close",
                    "balance": "",
                    "coda_details": {
                        "customer_name": row["customer_name"],
                        "ec_coda_id": "",
                        "amaunt": row["amaunt"],
                        "message": row["message"],
                        "invoice_number": row["invoice_nr"],
                        "bank_account_number": row["bank_account_number"],
                        "ec_customer_id": invoices[0]["customer__ec_customer_id"],
                        "coda_file_name": file_name,
                    },
                }
            )
            status = CodeTable.objects.filter(code="INVCLOSED").values("id").first()
            Invoice.objects.filter(id=value["id"]).update(amount_paid=new_payment, cust_amount_paid=value["cust_amount_paid"], status_id=status["id"], paid_on=now)
            if int(file_data[file_id]["id"]) == int(file_id):
                if invoice_nr:
                    file_data[file_id]["invoice_status"] = "Closed"

        if coda_files:
            coda_files.compared_xml_string2 = json.dumps(file_data)
            coda_files.save()
        PaymentRegistration.objects.bulk_create(payment_registration)
        CodaTransaction.objects.bulk_create(coda_transaction)
        azure_payload = json.dumps(azure_payload)
        azure_service(azure_payload)
        log_views.insert("sales", "invoice", object_ids, AuditAction.UPDATE, user_id, c_ip, "Invoice closed.", document_no=payment.id)
    return APIResponse(code=1, message="Invoice closed.")


@api_view(["post"])
def credit_limit(request):
    customer_id = str(request.data.get("customer_id"))
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.get(settings.EC_PY_URL + "/ecpy/finance/get_credit_limit/" + customer_id + "/", headers=headers).json()
    return APIResponse(data)


@api_view(["post"])
def change_credit_limit(request):
    ec_company_id = request.data.get("ec_company_id")
    credit_limit = request.data.get("credit_limit")
    base_credit_limit = request.data.get("base_credit_limit")
    starting_days = request.data.get("starting_days")
    invoice_date = request.data.get("invoice_date")
    payload = {"credit_limit": credit_limit, "base_credit_limit": base_credit_limit, "days": starting_days, "ec_company_id": ec_company_id, "invoice_date": invoice_date}
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token, "Content-Type": "application/json"}
    data = requests.post(settings.EC_PY_URL + "/ecpy/finance/save_credit_limit/", headers=headers, data=json.dumps(payload))
    return APIResponse(code=1, message="Changed credit limit.")


@api_view(["post"])
def ec_close_invoice(request):
    data = request.data
    c_ip = base_views.get_client_ip(request)
    customer = Customer.objects.filter(ec_customer_id=data["data"]["ec_customer_id"]).values("id").first()
    payment = Payment.objects.create(
        customer_id=customer["id"],
        payment_mode=data["data"]["payment_mode"],
        currency_rate=data["data"]["currency_factor"],
        total_amount=data["data"]["total_amount"],
    )
    payment_registration = []
    coda_transcation = []
    for invoice in data["data"]["invoices"]:
        payment_registration.append(
            PaymentRegistration(
                payment=payment,
                amount=invoice["new_payment"],
                payment_difference_type=invoice["payment_difference_type"],
                balance_on_date=invoice["balance"],
                paid_on=data["data"]["paid_on"] if data["data"]["paid_on"] in invoice else None,
                currency_rate=data["data"]["currency_factor"],
            )
        )
        invoi = Invoice.objects.filter(invoice_number=invoice["invoice_number"])
        invoi.update(outstanding_amount=invoice["outstanding_amount"], amount_paid=invoice["new_payment"])
        invoice_id = invoi.values("id")
        object_id = []
        for i in invoice_id:
            object_id.append(i["id"])
        if invoice["coda_details"]:
            coda_transcation.append(
                CodaTransaction(
                    invoice_id=invoice_id,
                    customer_name=invoice["coda_details"]["customer_name"],
                    ec_coda_id=invoice["coda_details"]["ec_coda_id"],
                    amount=invoice["coda_details"]["amaunt"],
                    message=invoice["coda_details"]["message"],
                    invoice_no=invoice["coda_details"]["invoice_number"],
                    bank_account_no=invoice["coda_details"]["bank_account_number"],
                    ec_customer_id=invoice["coda_details"]["ec_customer_id"],
                )
            )

        log_views.insert("sales", "invoice", object_id, AuditAction.UPDATE, "", c_ip, "Close invoice update.", document_no=payment.id, username="")
    PaymentRegistration.objects.bulk_create(payment_registration)
    if len(coda_transcation) > 0:
        CodaTransaction.objects.bulk_create(coda_transcation)
    return APIResponse(code=1, message="Updated close invoice")


@api_view(["get"])
def discount_lookup(request):
    ec_customer_id = request.GET.get("ec_customer_id")
    group_code = request.GET.get("group_code")
    discount_code = request.GET.get("discount_code")
    is_search = request.GET.get("is_search")
    limit = request.GET.get("page_size")
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    totalRecords = 0
    if is_search:
        payload = {"ec_customer_id": ec_customer_id, "group_code": group_code, "discount_code": discount_code, "limit": limit}
        data = requests.get(settings.EC_PY_URL + "/ecpy/finance/search_discount_lookup/", headers=headers, data=json.dumps(payload))
        response = data.json()
        totalRecords = len(response["data"])
    else:
        data = requests.get(settings.EC_PY_URL + "/ecpy/finance/search_discount/" + ec_customer_id + "/" + limit + "/", headers=headers)
        response = data.json()
        totalRecords = len(response["data"])
    response = {"code": 1, "totalRecords": totalRecords, "data": response["data"]}
    return Response(response)


@api_view(["get"])
def order_intake(request):
    ec_customer_id = request.GET.get("ec_customer_id")
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.get(settings.EC_PY_URL + "/ecpy/finance/performance_order_intake/" + ec_customer_id, headers=headers).json()
    return APIResponse(data["data"])


@api_view(["get"])
def shipment(request):
    ec_customer_id = request.GET.get("ec_customer_id")
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.get(settings.EC_PY_URL + "/ecpy/finance/performance_shipment/" + ec_customer_id, headers=headers).json()
    return APIResponse(data["data"])


@api_view(["get"])
def request_report(request):
    ec_customer_id = request.GET.get("ec_customer_id")
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.get(settings.EC_PY_URL + "/ecpy/finance/performance_request/" + ec_customer_id, headers=headers).json()
    return APIResponse(data["data"])


@api_view(["get"])
def after_sales(request):
    ec_customer_id = request.GET.get("ec_customer_id")
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.get(settings.EC_PY_URL + "/ecpy/finance/performance_after_sales/" + ec_customer_id, headers=headers).json()
    return APIResponse(data["data"])


@api_view(["get"])
def finance_report(request):
    ec_customer_id = request.GET.get("ec_customer_id")
    token = Util.get_ec_py_token()
    headers = {"accept": "application/json", "Authorization": "Bearer " + token}
    data = requests.get(settings.EC_PY_URL + "/ecpy/finance/financial_report/" + ec_customer_id, headers=headers).json()
    return APIResponse(data["data"])


class XeroBooking(generics.ListAPIView):
    serializer_class = XeroBookingSerilizer
    pagination_class = CustomPagination

    def get_queryset(self):
        query = Q()
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        is_date = self.request.GET.get("is_date")
        prefix = self.request.GET.get("prefix")
        from_number = self.request.GET.get("from_number")
        to_number = self.request.GET.get("to_number")
        if from_date != "undefined" and to_date != "undefined" and is_date == "true":
            query.add(Q(created_on__range=[from_date, to_date]), query.connector)
        else:
            from_invoice_nr = prefix + "/" + from_number
            to_invoice_nr = prefix + "/" + to_number
            query.add(Q(invoice_number__range=(from_invoice_nr, to_invoice_nr)), query.connector)
        queryset = (
            Invoice.objects.filter(query)
            .prefetch_related("custominvoice_invoice")
            .values(
                "id",
                "invoice_number",
                "hand_company__name",
                "invoice_created_on",
                "invoice_due_date",
                "customer__vat_no",
                "vat_percentage",
                "customer__ec_customer_id",
                "customer__name",
            )
        )
        return queryset


# @api_view(["get"])
# def get_company_address(request):
#     ec_customer_id = request.GET.get("ec_customer_id")
#     invoice_id = request.GET.get("ids")
#     print(invoice_id, "invoice_id ")
#     token = Util.get_ec_py_token()
#     headers = {"accept": "application/json", "Authorization": "Bearer " + token}
#     data = requests.post(settings.EC_PY_URL + "/ecpy/finance/get_company_address/" + ec_customer_id, headers=headers).json()
#     data = data["data"][0]
#     address_data = {}
#     for key, value in data.items():
#         if key in data:
#             address_data["address_data"] = data[key]

#     print(type(data), "data types")
#     invoice = (
#         Invoice.objects.filter(id=invoice_id)
#         .values(
#             "id",
#             "customer__name",
#             "street_address1",
#             "street_address2",
#             "invoice_city",
#             "postal_code",
#             "country__name",
#             "invoice_fax",
#             "customer__vat_no",
#             "customer__invoice_lang__name",
#             "invoice_number",
#             "invoice_address__state",
#             "invoice_phone",
#             "hand_company__name",
#             "hand_company__id",
#             "hand_company__vat_no",
#             "invoice_due_date",
#             "custom_value",
#             "weight",
#             "invoice_value",
#             "vat_percentage",
#             "transport_cost",
#         )
#         .first()
#     )
#     hand_id = invoice["hand_company__id"]
#     customer = (
#         Customer.objects.prefetch_related("address_customer")
#         .filter(id=hand_id)
#         .values(
#             "address_customer__street_address1",
#             "address_customer__street_address2",
#             "address_customer__city",
#             "address_customer__state",
#             "address_customer__country",
#             "address_customer__fax",
#             "address_customer__phone",
#             "address_customer__fax",
#             "address_customer__postal_code",
#         )
#         .first()
#     )
#     datas = {**address_data, **invoice}
#     print(type(invoice), "data type", type(customer), "data types")
#     return APIResponse(code=1, data=datas)


@api_view(["post"])
def generate_e_invoice(request):
    print("enter in generate e invoice")
    return APIResponse("data")
