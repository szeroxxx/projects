import json
import requests
import xmltodict
from accounts.models import UserProfile
from base.models import AppResponse
from base.util import Util
from django.conf import settings
from django.shortcuts import HttpResponse, render
from exception_log import manager
from sales.service import CustomerService, SalesEcPyService, SalesService


def invoices(request, customer_name=None):
    perms = ["view", "can_grant_days", "can_update_invoice_credit_limit", "can_update_secondary_status", "can_customer_login_invoices"]
    permissions = Util.get_permission_role(request.user, perms)
    if customer_name:
        return render(request, "finance/invoices.html", {"customer_name": customer_name, "permissions": json.dumps(permissions)})
    return render(request, "finance/invoices.html", {"permissions": json.dumps(permissions)})


def invoices_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "RowLimit": str(request.POST["length"]),
        }
        search_request = False
        if request.POST.get("invoice_number") is not None:
            post_data["InvoiceNr"] = request.POST["invoice_number"].strip()
            search_request = True
        if request.POST.get("invoice_value") is not None:
            post_data["InvoiceValue"] = request.POST["invoice_value"].strip()
            search_request = True

        if request.POST.get("order_number") is not None:
            post_data["OrderNumber"] = request.POST["order_number"].strip()
            search_request = True

        if request.POST.get("customer") is not None:
            post_data["c.CustomerName"] = request.POST["customer"].strip()
            search_request = True

        if request.POST.get("invoice_status") is not None:
            post_data["ac1.UsageDescription"] = request.POST["invoice_status"].strip()
            search_request = True

        if request.POST.get("invoice_secondary_status") is not None:
            post_data["sac.UsageDescription"] = request.POST["invoice_secondary_status"].strip()
            search_request = True

        if request.POST.get("country") is not None:
            post_data["c.InvoiceCountry"] = request.POST["country"].strip()
            search_request = True

        if request.POST.get("handling_company") is not None:
            post_data["c1.Name"] = request.POST["handling_company"].strip()
            search_request = True

        if request.POST.get("root_company") is not None:
            post_data["c.RootCompanyName"] = request.POST["root_company"].strip()
            search_request = True

        if request.POST.get("postal_code") is not None:
            post_data["c.InvoicePostalCode"] = request.POST["postal_code"].strip()
            search_request = True

        if request.POST.get("city") is not None:
            post_data["c.InvoiceCity"] = request.POST["city"].strip()
            search_request = True

        if request.POST.get("phone") is not None:
            post_data["c.InvoiceTelephone"] = request.POST["phone"].strip()
            search_request = True

        if request.POST.get("vat_nr") is not None:
            post_data["c.VATNr"] = request.POST["vat_nr"].strip()
            search_request = True

        if request.POST.get("payment_tracking_id") is not None:
            post_data["PaymentTrackingNumber"] = request.POST["payment_tracking_id"].strip()
            search_request = True

        # if request.POST.get("invoice_dueDate") is not None:
        #     post_data["InvoiceDueDate"] = request.POST["invoice_dueDate"].strip()
        #     search_request = True

        if request.POST.get("pcb_name") is not None:
            post_data["PCBName"] = request.POST["pcb_name"].strip()
            search_request = True

        if request.POST.get("username") is not None:
            post_data["c.UserName"] = request.POST["username"].strip()
            search_request = True

        if request.POST.get("IncludeDeletedProforma") is not None:
            post_data["IncludeDeletedProforma"] = request.POST["IncludeDeletedProforma"].strip()
            search_request = True

        if request.POST.get("invoice_date__date") is not None:
            if "invoice_date__date_from_date" in request.POST:
                post_data["InvoiceFromDate"] = request.POST["invoice_date__date_from_date"].strip()
                post_data["InvoiceTillDate"] = request.POST["invoice_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("invoice_dueDate__date") is not None:
            if "invoice_dueDate__date_from_date" in request.POST:
                post_data["InvoiceDueFromDate"] = request.POST["invoice_dueDate__date_from_date"].strip()
                post_data["InvoiceDueTillDate"] = request.POST["invoice_dueDate__date_to_date"].strip()
                search_request = True

        invoices = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_invoice"
            invoices = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": len(invoices),
            "recordsFiltered": len(invoices),
            "data": [],
        }

        for invoice in invoices:
            response["data"].append(
                {
                    "id": invoice["InvoiceId"],
                    "invoice_number": invoice["InvoiceNr"],
                    "invoice_date": invoice["InvoiceDate"],
                    "last_rem_date": invoice["LastRemDate"],
                    "exchange_rate": invoice["Exchange_Rate"],
                    "currency_symbol": invoice["Currency_Symbol"],
                    "outstanding": invoice["Outstanding"],
                    "cust_outstanding": invoice["Cust_Outstanding"],
                    "invoice_dueDate": invoice["InvoiceDueDate"],
                    "financial_blocked": invoice["FinancialBlocked"],
                    "credit_limit": invoice["CreditLimit"],
                    "cust_credit_limit": invoice["Cust_CreditLimit"],
                    "customer": invoice["Customer"],
                    "customer_type": invoice["CustomerType"],
                    "handling_company": invoice["HC"],
                    "root_company": invoice["RootCompany"],
                    "invoice_value": invoice["InvoiceValue"],
                    "cust_invoice_value": invoice["Cust_InvoiceValue"],
                    "invoice_status": invoice["Status"],
                    "recent": invoice["Recent"],
                    "recent_id": invoice["RecentId"],
                    "communication": invoice["Communication"],
                    "amount_paid": invoice["AmountPaid"],
                    "cust_amountPaid": invoice["Cust_AmountPaid"],
                    "payment_date": invoice["Payment_Date"],
                    "delivery_nr": invoice["DeliveryNr"],
                    "vat_nr": invoice["VAT"],
                    "country": invoice["Country"],
                    "address_line1": invoice["AddressLine1"],
                    "accounting_no": invoice["Accounting no"],
                    "address_line2": invoice["AddressLine2"],
                    "postal_code": invoice["Postal_Code"],
                    "city": invoice["City"],
                    "email": invoice["Email"],
                    "phone": invoice["Phone"],
                    "fax": invoice["Fax"],
                    "match": invoice["Match"],
                    "handling_company_id": invoice["HandCompanyId"],
                    "custUserId": invoice["custUserId"],
                    "order_number": invoice["OrderNumber"],
                    "payment_tracking_id": invoice["PaymentId"],
                    "payment_status": invoice["PaymentStatus"],
                    "deliver_invoice_by_post": "No" if invoice["DeliverInvoiceByPost"] is False else "Yes",
                    "isInvoice_deliver": "No" if invoice["IsInvoiceDeliver"] is False else "Yes",
                    "invoice_secondary_status": invoice["SecondaryStatus"],
                    "invoice_delivery": invoice["InvoiceDelivery"],
                    # "pcb_name": invoice["pcb_name"] if "pcb_name" in invoice else "",
                    "customer_id": invoice["CustomerID"],
                    # "username": invoice["username"] if "username" in invoice else "",
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def proforma_invoices(request, customer_name=None):
    perms = ["view", "can_grant_days", "can_update_proforma_invoice_credit_limit", "can_update_secondary_status", "can_do_customer_login"]
    permissions = Util.get_permission_role(request.user, perms)
    if customer_name:
        return render(request, "finance/proforma_invoices.html", {"customer_name": customer_name, "permissions": json.dumps(permissions)})
    return render(request, "finance/proforma_invoices.html", {"permissions": json.dumps(permissions)})


def proforma_invoices_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "InvoiceNr": "",
            "InvoiceValue": "",
            "OrderNumber": "",
            "PCBName": "",
            "so.CustomerName": "",
            "so.CustUserName": "",
            "so.CustCountry": "",
            "ac1.UsageDescription": "",
            "C.HandlingCompany": "",
            "C.RootCompanyName": "",
            "C.InvoicePostalCode": "",
            "C.InvoiceCity": "",
            "C.InvoiceTelephone": "",
            "C.VATNr": "",
            "InvoiceFromDate": "",
            "InvoiceTillDate": "",
            "limit": str(request.POST["length"]),
        }
        search_request = False
        if request.POST.get("invoice_number") is not None:
            post_data["InvoiceNr"] = request.POST["invoice_number"]
            search_request = True
        if request.POST.get("invoice_value") is not None:
            post_data["InvoiceValue"] = request.POST["invoice_value"]
            search_request = True
        if request.POST.get("order_number") is not None:
            post_data["OrderNumber"] = request.POST["order_number"]
            search_request = True
        if request.POST.get("pcb_name") is not None:
            post_data["PCBName"] = request.POST["pcb_name"]
            search_request = True
        if request.POST.get("customer") is not None:
            post_data["so.CustomerName"] = request.POST["customer"]
            search_request = True
        if request.POST.get("username") is not None:
            post_data["so.CustUserName"] = request.POST["username"]
            search_request = True
        if request.POST.get("country") is not None:
            post_data["so.CustCountry"] = request.POST["country"]
            search_request = True
        if request.POST.get("invoice_status") is not None:
            post_data["ac1.UsageDescription"] = request.POST["invoice_status"]
            search_request = True
        if request.POST.get("handling_company") is not None:
            post_data["C.HandlingCompany"] = request.POST["handling_company"]
            search_request = True
        if request.POST.get("root_company") is not None:
            post_data["C.RootCompanyName"] = request.POST["root_company"]
            search_request = True
        if request.POST.get("Postal_code") is not None:
            post_data["C.InvoicePostalCode"] = request.POST["Postal_code"]
            search_request = True
        if request.POST.get("city") is not None:
            post_data["C.InvoiceCity"] = request.POST["city"]
            search_request = True
        if request.POST.get("phone") is not None:
            post_data["C.InvoiceTelephone"] = request.POST["phone"]
            search_request = True
        if request.POST.get("vat_nr") is not None:
            post_data["C.VATNr"] = request.POST["vat_nr"]
            search_request = True
        # if request.POST.get("IncludeDeletedProforma") is not None:
        #     post_data["IncludeDeletedProforma"] = request.POST["IncludeDeletedProforma"]
        #     search_request = True

        # if request.POST.get("outstanding_only") is not None:

        #     post_data["param"]["OutstandingOnly"] = request.POST["outstanding_only"]
        #     search_request = True

        if request.POST.get("invoice_date__date") is not None:
            if "invoice_date__date_from_date" in request.POST:
                post_data["InvoiceFromDate"] = request.POST["invoice_date__date_from_date"].strip()
                post_data["InvoiceTillDate"] = request.POST["invoice_date__date_to_date"].strip()
                search_request = True
        invoices = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_proforma_invoice/"
            invoices = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": len(invoices),
            "recordsFiltered": len(invoices),
            "data": [],
        }
        for invoice in invoices:
            response["data"].append(
                {
                    "id": invoice["InvoiceId"],
                    "invoice_number": invoice["InvoiceNr"],
                    "Comm_InvoiceNr": invoice["Comm_InvoiceNr"],
                    "invoice_date": invoice["InvoiceDate"],
                    "DeliveryNo": invoice["DeliveryNo"],
                    "order_number": invoice["OrderNumber"],
                    "invoice_status": invoice["Status"],
                    "statusid": invoice["statusid"],
                    "OrderStatusId": invoice["OrderStatusId"],
                    "Service": invoice["Service"],
                    "customer": invoice["Customer"],
                    "username": invoice["UserName"],
                    "invoice_value": invoice["InvoiceValue"],
                    "CustUserId": invoice["CustUserId"],
                    "customer_id": invoice["CustomerId"],
                    "Customer1": "invoice",
                    "CreditLimit": invoice["CreditLimit"],
                    "Currency_Symbol": invoice["Currency_Symbol"],
                    "root_company": invoice["RootCompany"],
                    "pcb_name": invoice["PCBname"],
                    "handling_company": invoice["HandlingCompany"],
                    "CustomerType": invoice["CustomerType"],
                    "Cust_AmountPaid": invoice["Cust_AmountPaid"],
                    "Cust_Outstanding": invoice["Cust_Outstanding"],
                    "outstanding_only": invoice["Outstanding"],
                    "Add1": invoice["Add1"],
                    "Add2": invoice["Add2"],
                    "Postal_code": invoice["PostalCode"],
                    "city": invoice["InvoiceCity"],
                    "phone": invoice["InvoiceTelephone"],
                    "InvoiceFax": invoice["InvoiceFax"],
                    "vat_nr": invoice["VAT"],
                    "Supplier": invoice["Supplier"],
                    "country": invoice["Country"],
                    "OrderStatus": invoice["OrderStatus"],
                    "LastRemDate": invoice["LastRemDate"],
                    "Exchange_Rate": invoice["Exchange_Rate"],
                    "InvoiceDueDate": invoice["InvoiceDueDate"],
                    "Payment_Date": invoice["Payment_Date"],
                    "HandCompanyId": invoice["HandCompanyId"],
                    "invoice_secondary_status": invoice["SecondaryStatus"],
                    "Currency_InvoiceValue": invoice["Currency_InvoiceValue"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def payment_browser(request):
    perms = ["view", "can_grant_days", "can_update_credit_limit", "can_update_secondary_status", "can_customer_login_payment_browser"]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "finance/payment_browser.html", {"permissions": json.dumps(permissions)})


def payment_browser_search(request):
    try:
        ec_py_service = SalesEcPyService()
        search_request = False
        request.POST = Util.get_post_data(request)
        post_data = {"funname": "SearchPaymentBrowser", "param": {"RowLimit": str(request.POST["length"])}}

        if request.POST.get("invoice_number") is not None:
            post_data["param"]["InvoiceNo"] = request.POST["invoice_number"].strip()
            search_request = True

        if request.POST.get("payment_mode") is not None:
            post_data["param"]["PaymentMode"] = request.POST["payment_mode"].strip()
            search_request = True

        if request.POST.get("payment_id") is not None:
            post_data["param"]["PaymentId"] = request.POST["payment_id"].strip()
            search_request = True

        if request.POST.get("customer") is not None:
            post_data["param"]["Customer"] = request.POST["customer"].strip()
            search_request = True

        if request.POST.get("country") is not None:
            post_data["param"]["Country"] = request.POST["country"].strip()
            search_request = True

        if request.POST.get("payment_date__date") is not None:
            if "payment_date__date_from_date" in request.POST:
                post_data["param"]["PaymentFromDate"] = request.POST["payment_date__date_from_date"].strip()
                post_data["param"]["PaymentTillDate"] = request.POST["payment_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("invoice_dueDate__date") is not None:
            if "invoice_dueDate__date_from_date" in request.POST:
                post_data["param"]["InvoiceDueFromDate"] = request.POST["invoice_dueDate__date_from_date"].strip()
                post_data["param"]["InvoiceDueTillDate"] = request.POST["invoice_dueDate__date_to_date"].strip()
                search_request = True

        invoices = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_payment_browser"
            invoices = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": len(invoices),
            "recordsFiltered": len(invoices),
            "data": [],
        }

        for invoice in invoices:
            response["data"].append(
                {
                    "id": invoice["InvoiceId"],
                    "invoice_number": invoice["Invoice_number"],
                    "customer": invoice["Customer_name"],
                    "payment_date": invoice["Payment_date"],
                    "payment_mode": invoice["Payment_mode"],
                    "Invoice_status": invoice["Invoice_status"],
                    "invoice_dueDate": invoice["InvoiceDueDate"],
                    "payment_id": invoice["Payment_ID"],
                    "Closed_by": invoice["Closed_by"],
                    "Closed_on": invoice["Closed_on"],
                    "Invoice_amount": invoice["Invoice_amount"],
                    "Payment_amount": invoice["Payment_amount"],
                    "Currency_symbol": invoice["Currency_symbol"],
                    "Bank_AccountNo": invoice["Bank_AccountNo"],
                    "Bank_name": invoice["Bank_name"],
                    "country": invoice["Country"],
                    "customer_id": invoice["CustomerID"],
                    "UserId": invoice["UserId"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def payment_browser_unmatched(request):
    perms = ["view", "can_grant_days", "can_send_invoice", "can_update_secondary_status", "can_do_customer_login"]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "finance/payment_browser_unmatched.html", {"permissions": json.dumps(permissions)})


def payment_browser_unmatched_search(request):
    try:
        search_request = False
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {"funname": "SearchPaymentBrowserUnmatched", "param": {"RowLimit": str(request.POST["length"])}}

        if request.POST.get("bank_name") is not None:
            post_data["param"]["Bank_Name"] = request.POST["bank_name"].strip()
            search_request = True

        if request.POST.get("payment_amount") is not None:
            post_data["param"]["Amount"] = request.POST["payment_amount"].strip()
            search_request = True

        if request.POST.get("bank_account_number") is not None:
            post_data["param"]["Bank_AccountNo"] = request.POST["bank_account_number"].strip()
            search_request = True

        if request.POST.get("payment_message") is not None:
            post_data["param"]["Message"] = request.POST["payment_message"].strip()
            search_request = True

        if request.POST.get("name") is not None:
            post_data["param"]["Customer_Name"] = request.POST["name"].strip()
            search_request = True

        if request.POST.get("create_date") is not None:
            if "create_date_from_date" in request.POST:
                post_data["param"]["CreatedFromDate"] = request.POST["create_date_from_date"].strip()
                post_data["param"]["CreatedTillDate"] = request.POST["create_date_to_date"].strip()
                search_request = True

        if request.POST.get("country") is not None:
            post_data["param"]["gsc.InvoiceCountry"] = request.POST["country"].strip()
            search_request = True
        banks_data = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_payment_browser_unmatch"
            banks_data = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": len(banks_data),
            "recordsFiltered": len(banks_data),
            "data": [],
        }

        for bank_data in banks_data:
            response["data"].append(
                {
                    "country": bank_data["country"],
                    "id": bank_data["PaymentBrowserId"],
                    "name": bank_data["Name"],
                    "bank_account_number": bank_data["Bank_AccountNo"],
                    "payment_amount": bank_data["Amount"],
                    "payment_message": bank_data["Message"],
                    "create_date": bank_data["Created_date"],
                    "bank_name": bank_data["Bank_name"],
                    "invoice_number": bank_data["Invoice Nr(s)"],
                    "remark": bank_data["Remark"],
                    "created_date": bank_data["Created_date"],
                    "Created_by": bank_data["Created_by"],
                    "codaFile_Id": bank_data["CodaFile_Id"],
                    "customer_id": bank_data["CustomerId"],
                    "communication": bank_data["Communication"],
                    "recent": bank_data["Recent"],
                    "recent_id": bank_data["RecentID"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def credit_limit(request, customer_id):
    cust_service = CustomerService(request=request)
    customer = cust_service.get_customer_detail(customer_id, request)
    ec_py_service = SalesEcPyService()
    post_data = {}
    post_data["companyId"] = customer["CompanyId"]
    ec_py_end_point = "/ecpy/sales/get_credit_limit"
    response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
    if response["code"] == 1:
        res = response["data"][0] if isinstance(response["data"], list) else response["data"]
        return HttpResponse(render(request, "finance/credit_limit.html", {"data": res, "customer_id": customer_id}))
    if response["code"] == "2":
        return HttpResponse(render(request, "finance/credit_limit.html", {"data": "", "customer_id": customer_id}))
    return HttpResponse(AppResponse.msg(0, str(response["message"])))


def save_credit_limit(request):
    try:
        post_data = {}
        cust_service = CustomerService(request=request)
        customer = cust_service.get_customer_detail(request.POST["customer_id"], request)
        post_data["companyId"] = customer["CompanyId"]
        post_data["daysStart"] = request.POST.get("daysStart")
        post_data["systemLimit"] = request.POST.get("systemLimit")
        post_data["insurance"] = request.POST.get("insurance")
        post_data["flag"] = request.POST.get("flag")
        profile = UserProfile.objects.filter(user_id=request.user.id).values("ec_user_id").first()
        post_data["ECCUserId"] = profile["ec_user_id"]
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/save_credit_limit"
        response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_grant_days(request):
    try:
        ec_py_service = SalesEcPyService()
        post_data = {}
        post_data["invoiceId"] = request.POST["invoice_id"]
        post_data["days"] = request.POST["days"]
        profile = UserProfile.objects.filter(user_id=request.user.id).values("ec_user_id").first()
        post_data["ECCUserId"] = profile["ec_user_id"]
        ec_py_end_point = "/ecpy/sales/save_grant_days"
        response = ec_py_service.process_ec_data(post_data, ec_py_end_point, request)
        if int(response["code"]) == 1:
            return HttpResponse(AppResponse.msg(1, response["message"]), content_type="json")
        return HttpResponse(AppResponse.msg(0, "Something went wrong"), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def customer_finance_report(request):
    try:
        is_refresh = request.POST.get("is_refresh")
        customer_id = request.POST.get("customer_id")
        data = {"funname": "CustomerFinancialReport", "param": {"customerid": customer_id, "isRefreshed": is_refresh}}
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/customer_financial_report"
        data = ec_py_service.search_ec_data(data, ec_py_end_point, request)
        context = data
        return render(request, "finance/customer_finance_report.html", context)

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_secondary_status_list(request):
    try:
        post_data = {"funname": "getSecondaryStatusList", "param": {}}
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/get_secondary_status_list/"
        response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_secondary_status(request):
    try:
        profile = UserProfile.objects.filter(user_id=request.user.id).values("ec_user_id").first()
        post_data = {}
        post_data["ECCUserId"] = profile["ec_user_id"]
        post_data["invoiceId"] = request.POST["invoiceId"]
        post_data["statusId"] = request.POST["statusId"]
        cust_service = CustomerService(request=request)
        customer = cust_service.get_customer_detail(str(request.POST["customerId"]), request)
        post_data["companyId"] = customer["CompanyId"]
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/change_invoice_secondary_status/"
        response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_credit_status(request):
    try:
        post_data = {}
        cust_service = CustomerService(request=request)
        ec_py_service = SalesEcPyService()
        customer = cust_service.get_customer_detail(str(request.POST.get("customerId")), request)
        post_data["companyId"] = customer["CompanyId"]
        post_data["custUserId"] = request.POST.get("custUserId")
        ec_py_end_point = "/ecpy/sales/search_invoices_credit_status/"
        response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        return render(request, "finance/credit_status.html", response)
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def invoice_proforma_search(request):
    try:
        customer_name = request.POST.get("Customer_Name")
        amount = request.POST.get("Amount")
        invoice_no = request.POST.get("InvoiceNr")
        funname = request.POST.get("funname")
        post_data = {"funname": funname, "param": {"Customer_Name": customer_name, "Amount": amount, "InvoiceNr": invoice_no}}
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/search_unmatched_proforma/"
        data = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        return HttpResponse(json.dumps(data), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def credit_report(request, customer_id):
    try:
        post_data = {"customer_id": customer_id}
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/customer_credit_report/"
        data = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)

        if data["code"] == "1":
            xml_data = xmltodict.parse(data["xmldata"], xml_attribs=False)
            context = json.dumps(xml_data)
            context_data = json.loads(context)
            # FinancialStatements
            fin_statements = context_data["CompanyReportSet"]["Reports"]["Report"]
            if fin_statements is not None and "FinancialStatements" in fin_statements:
                if (
                    fin_statements["FinancialStatements"] is not None
                    and "FinancialStatement" in fin_statements["FinancialStatements"]
                    and not isinstance(fin_statements["FinancialStatements"]["FinancialStatement"], list)
                ):
                    fin_list = [fin_statements["FinancialStatements"]["FinancialStatement"]]
                    context_data["CompanyReportSet"]["Reports"]["Report"]["FinancialStatements"]["FinancialStatement"] = fin_list
            # handle directors list
            directors = context_data["CompanyReportSet"]["Reports"]["Report"]["Directors"]
            if directors is not None and "CurrentDirectors" in directors:
                if directors["CurrentDirectors"] is not None and "Director" in directors["CurrentDirectors"] and not isinstance(directors["CurrentDirectors"]["Director"], list):
                    director_list = [directors["CurrentDirectors"]["Director"]]
                    context_data["CompanyReportSet"]["Reports"]["Report"]["Directors"]["CurrentDirectors"]["Director"] = director_list
            main_address = context_data["CompanyReportSet"]["Reports"]["Report"]["ContactInformation"]

            # handle main address list
            if main_address is not None and "MainAddress" in main_address:
                if main_address["MainAddress"] is not None and "Address" in main_address["MainAddress"] and not isinstance(main_address["MainAddress"]["Address"], list):
                    main_address_list = [main_address["MainAddress"]["Address"]]
                    context_data["CompanyReportSet"]["Reports"]["Report"]["ContactInformation"]["MainAddress"]["Address"] = main_address_list

            # handle other address list
            if main_address is not None and "OtherAddresses" in main_address:
                if (
                    main_address["OtherAddresses"] is not None
                    and "OtherAddress" in main_address["OtherAddresses"]
                    and not isinstance(main_address["OtherAddresses"]["OtherAddress"], list)
                ):
                    if (
                        main_address["OtherAddresses"]["OtherAddress"] is not None
                        and "Address" in main_address["OtherAddresses"]["OtherAddress"]
                        and not isinstance(main_address["OtherAddresses"]["OtherAddress"]["Address"], list)
                    ):
                        address_details = main_address["OtherAddresses"]["OtherAddress"]
                        country = "" if "Country" not in address_details else address_details["Country"]
                        telephone = "" if "Telephone" not in address_details else address_details["Telephone"]
                        other_address_list = [{"Address": [main_address["OtherAddresses"]["OtherAddress"]["Address"]], "Country": country, "Telephone": telephone}]
                        context_data["CompanyReportSet"]["Reports"]["Report"]["ContactInformation"]["OtherAddresses"]["OtherAddress"] = other_address_list
                elif (
                    main_address["OtherAddresses"] is not None
                    and "OtherAddress" in main_address["OtherAddresses"]
                    and isinstance(main_address["OtherAddresses"]["OtherAddress"], list)
                ):
                    other_address_list = []
                    for otheraddress in main_address["OtherAddresses"]["OtherAddress"]:
                        if otheraddress is not None:
                            country = "" if "Country" not in otheraddress else otheraddress["Country"]
                            telephone = "" if "Telephone" not in otheraddress else otheraddress["Telephone"]
                            if "Address" in otheraddress and not isinstance(otheraddress["Address"], list):
                                other_address_list.append({"Address": [otheraddress["Address"]], "Country": country, "Telephone": telephone})
                            elif "Address" in otheraddress and isinstance(otheraddress["Address"], list):
                                other_address_list.append({"Address": otheraddress["Address"], "Country": country, "Telephone": telephone})
                            elif "Address" not in otheraddress:
                                other_address_list.append({"Address": [], "Country": country, "Telephone": telephone})
                    context_data["CompanyReportSet"]["Reports"]["Report"]["ContactInformation"]["OtherAddresses"]["OtherAddress"] = other_address_list
            shareholders = context_data["CompanyReportSet"]["Reports"]["Report"]["ShareCapitalStructure"]
            if shareholders is not None and "ShareHolders" in shareholders:
                if shareholders["ShareHolders"] is not None and "ShareHolder" in shareholders["ShareHolders"] and not isinstance(shareholders["ShareHolders"]["ShareHolder"], list):
                    shareholder_list = [shareholders["ShareHolders"]["ShareHolder"]]
                    context_data["CompanyReportSet"]["Reports"]["Report"]["ShareCapitalStructure"]["ShareHolders"]["ShareHolder"] = shareholder_list
            return render(request, "finance/credit_report.html", {"data": context_data, "code": data["code"], "msg": ""})
        elif data["code"] == "2":
            return render(request, "finance/credit_report.html", {"data": "", "code": data["code"], "msg": data["message"]})
        return render(request, "finance/credit_report.html", {"data": "", "code": "", "msg": "Something went wrong."})
    except Exception as e:
        manager.create_from_exception(e)
        return render(request, "finance/credit_report.html", {"data": "", "code": "", "msg": str(e)})


def get_invoice_history(request, invoice_id):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {"invoiceId": invoice_id}
        ec_py_end_point = "/ecpy/sales/get_invoice_history/"
        ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        return HttpResponse(render(request, "finance/invoice_history.html", {"data": ec_py_response}))
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
