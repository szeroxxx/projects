import json
from turtle import update

from auditlog import views as log_views
from auditlog.models import AuditAction
from customer.models import Customer
from django.utils import timezone
from payment.models import CodaFile, CodaTransaction, Payment, PaymentRegistration
from sales.models import Invoice

from base import views as base_views
from base.models import CodeTable, Currency
from base.sb_send import azure_service

"""coda invoice close [{'invoice_nr': 'EN16/092963,EN16/092963,EN16/092963', 'total_amount': '81.34', 'id': 4, 'bank_account_number': 'BE50413314082118',
 'amaunt': '81.34', 'message': 'ACT.NR.: EN16/0929630', 'customer_name': 'ESDACO BVBA'},
 {'invoice_nr': 'EN16/092963,EN16/092963,EN16/092963', 'total_amount': '81.34', 'id': 4, 'bank_account_number': 'BE50413314082118',
 'amaunt': '81.34', 'message': 'ACT.NR.: EN16/0929630', 'customer_name': 'ESDACO BVBA'}]"""

"""close  invoice [{'invoice_number': 'EN17/093401', 'invoice_id': 3063, 'ec_invoice_id': 352692,
'new_payment': 150.65, 'outstanding': '150.650', 'deference': 0, 'currency_amount': 150.65,
'currency_total_amount': 150.65, 'payment_deference_type': 'INVCLOSED'}]"""


def payment_registration(request, row_values=None, invoice_nr=None, invoice_type=None, currency_id=None, total_amount=None, payment_mode=None, paid_on=None, coda_values=None):
    print("enter in payment registration function")
    c_ip = base_views.get_client_ip(request)
    user_id = request.data.get("user_id")
    if invoice_type == "close_invoice":
        payment_mode = request.data.get("payment_mode")
        total_amount = request.data.get("total_amount")
        currency_rate = request.data.get("currency_rate")
        base_total_amount = round(float(total_amount) / float(currency_rate), 3)
        paid_on = request.data.get("paid_on")
        customer_id = request.data.get("customer_id")
        ec_customer_id = request.data.get("ec_customer_id")

    if invoice_type == "coda_invoice":
        file_name = request.data.get("file_name")
        coda_id = request.data.get("coda_id")
        coda_files = CodaFile.objects.get(id=coda_id)
        file_data = json.loads(coda_files.compared_xml_string2)

    print(user_id, "user_id")
    now = timezone.now()
    if invoice_type == "close_invoice":
        # payment = Payment.objects.create(customer_id=customer_id,currency_id=currency_id,currency_rate=currency_rate, total_amount=total_amount,currency_total_amount=base_total_amount,payment_mode=payment_mode)
        pass
    # payment = Payment.objects.create(customer_id=customer_id,currency_id=currency_id,currency_rate=currency_rate, total_amount=total_amount,currency_total_amount=base_total_amount,payment_mode=payment_mode)
    object_ids = []
    payment_registrations = []
    coda_transaction = []
    if invoice_type == "close_invoice":
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
    if invoice_type == "coda_invoice":
        invoice_nr = invoice_nr.split(",")
        row_values = Invoice.objects.filter(invoice_number__in=invoice_nr).values(
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
        # payment = Payment.objects.create(customer_id=row_values[0]["customer_id"],currency_id=row_values[0]["currency_id"],currency_rate=row_values[0]["curr_rate"], total_amount=total_amount)
        azure_payload = {
            "type": "CloseInvoice",
            "data": {
                "total_amount": str(total_amount),
                "currency_factor": str(row_values[0]["curr_rate"]),
                "paid_on": str(now),
                "ec_customer_id": row_values[0]["customer__ec_customer_id"],
                "payment_mode": "",
                "invoices": [],
            },
        }
        coda_transaction.append(
            CodaTransaction(
                customer_id=row_values[0]["customer_id"],
                invoice_id=row_values[0]["id"],
                customer_name=coda_values["customer_name"],
                amount=coda_values["amount"],
                message=coda_values["message"],
                invoice_no=invoice_nr,
                bank_account_no=coda_values["bank_ac_no"],
                ec_customer_id=row_values[0]["customer__ec_customer_id"],
            )
        )

    for invo in row_values:
        # print(row_values,"row values")
        # print(invo,"row values")
        if invoice_type == "coda_invoice":
            object_ids.append(invo["id"])
        else:
            object_ids.append(invo["invoice_id"])

        new_payment = invo["currency_invoice_value"] / invo["curr_rate"] if "new_payment" not in invo else invo["new_payment"]
        payment_registrations.append(
            PaymentRegistration(
                # payment = payment,
                customer_id=invo["customer_id"] if "customer_id" in invo else None,
                amount=new_payment,
                transfer_type="C",
                reference="",
                ref_document_do="",
                invoice_id=invo["id"] if "id" in invo else None,
                payment_difference_type="close",
                payment_date=None,
                balance_on_date=0.000,
                remark="",
                created_by_id=user_id,
                username=None,
                currency_amount=invo["currency_invoice_value"] if "currency_invoice_value" in invo else invo["currency_amount"],
                currency_balance_on_date=0.000,
                paid_on=now,
                currency_id=invo["currency_id"] if "currency_id" in invo else currency_id,
                currency_rate=invo["curr_rate"] if "curr_rate" in invo else currency_rate,
                currency_total_amount=0.000,
            )
        )
        azure_payload["data"]["invoices"].append(
            {
                "new_payment": str(new_payment),
                "invoice_number": invo["invoice_number"],
                "ec_invoice_id": invo["ec_invoice_id"],
                "is_down_payment": False,
                "outstanding_amount": str((invo["currency_invoice_value"] - invo["cust_amount_paid"])) if "outstanding" not in invo else invo["outstanding"],
                "Payment_difference_type": "Close",
                "balance": "",
            }
        )
        # print(new_payment,"newpayment")
        def_type = "INVCLOSED" if "payment_deference_type" not in invo else invo["payment_deference_type"]
        def_type_amount_paid = invo["new_payment"] if "new_payment" in invo else new_payment
        def_type_cust_amount_paid = invo["new_payment"] if "new_payment" in invo else invo["cust_amount_paid"]
        # status = CodeTable.objects.filter(code=def_type).values("id").first()
        # if "invoice_id" in invo:
        #     invoices = Invoice.objects.filter(id=invo["invoice_id"])
        # else:
        #     invoices= Invoice.objects.filter(invoice_number=invo["invoice_number"])

        # invoices.update(amount_paid = def_type_amount_paid,cust_amount_paid = def_type_cust_amount_paid,status_id=status["id"],paid_on=now)
        if invoice_type == "coda_invoice":
            # status = CodeTable.objects.filter(code=def_type).values("id").first()
            # if "invoice_id" in invo:
            #     invoices = Invoice.objects.filter(id=invo["invoice_id"])
            # else:
            #     invoices= Invoice.objects.filter(invoice_number=invo["invoice_number"])
            # # Invoice.objects.filter(id=invo["invoice_id"]).update(amount_paid = invo["new_payment"],cust_amount_paid = invo["new_payment"],status_id=status["id"],paid_on=paid_on)
            # # Invoice.objects.filter(invoice_number=invo["invoice_number"]).update(amount_paid = def_type_amount_paid,cust_amount_paid = def_type_cust_amount_paid,status_id=status["id"],paid_on=now)
            # invoices.update(amount_paid = def_type_amount_paid,cust_amount_paid = def_type_cust_amount_paid,status_id=status["id"],paid_on=now)
            if int(file_data[coda_values["file_id"]]["id"]) == int(coda_values["file_id"]):
                if invoice_nr:
                    file_data[coda_values["file_id"]]["invoice_status"] = "Closed"
                    azure_payload["data"]["invoices"][0]["coda_details"] = {
                        "customer_name": coda_values["customer_name"],
                        "ec_coda_id": "",
                        "amaunt": coda_values["amount"],
                        "message": coda_values["message"],
                        "invoice_number": invoice_nr[0],
                        "bank_account_number": coda_values["bank_ac_no"],
                        "ec_customer_id": row_values[0]["customer__ec_customer_id"],
                        "coda_file_name": file_name,
                    }
        # if coda_files:
        #     coda_files.compared_xml_string2 = json.dumps(file_data)
        #     coda_files.save()
    # PaymentRegistration.objects.bulk_create(payment_registrations)
    # print(azure_payload,"azure payload")
    # if invoice_type == "coda_invoice":
    # CodaTransaction.objects.bulk_create(coda_transaction)
    # log_views.insert("sales", "invoice", object_ids, AuditAction.UPDATE ,user_id , c_ip , "Invoice closed.",document_no=payment.id)
    print("payment registration object created")


from django.db.models import CharField, F, Func, Value
from sales.models import Invoice


class Service(object):
    @staticmethod
    def invoice(ids):
        response = (
            Invoice.objects.filter(id__in=ids)
            .values(
                "id",
                "customer__id",
                "invoice_number",
                "transport_cost",
                "currency__code",
                "financial_block",
                "customer__credit_limit",
                "customer__customer_credit_limit",
                "customer__name",
                "customer__customer_type__name",
                "hand_company__name",
                "customer__is_root__name",
                "invoice_value",
                "currency_invoice_value",
                "status__desc",
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
            )
            .annotate(
                outstanding=F("invoice_value") - F("amount_paid"),
                customer_outstanding=F("currency_invoice_value") - F("cust_amount_paid"),
                invoice_created_on=Func(F("invoice_created_on"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
                invoice_due_date=Func(F("invoice_due_date"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
                last_rem_date=Func(F("last_rem_date"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
                payment_date=Func(F("payment_date"), Value("dd.MM.yyyy"), function="to_char", output_field=CharField()),
            )
        )
        return response
