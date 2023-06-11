from datetime import datetime
from urllib import response

import core
from fastapi import APIRouter, Request,Response
from util import Util

invoicing = APIRouter()


@invoicing.post("/get_secondary_status_list/")
async def get_secondary_status_list(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        change_status = False
        query = "exec sp_Invoice_status {0}".format(change_status)
        data = core.execute_query(query, "Invoices-Change secondary status", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/change_invoice_secondary_status/")
async def change_invoice_secondary_status(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        change_status = False
        query = "EXEC sa_secondary_status_Update {0},{1},'{2}','{3}',{4}".format(data["companyId"], data["ECCUserId"], data["statusId"], data["invoiceId"], change_status)
        core.execute_nonquery(query, "Invoices-Change secondary status", ec_user_id, ec_username)
        data = {"data": "", "code": 1}
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_invoices_credit_status/")
async def search_invoices_credit_status(request: Request):
    try:
        data = await request.json()
        company_id = data["companyId"]
        ecc_user_id = data["custUserId"]
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        query = f"exec spGetCreditDataForCompany {company_id}"
        credit_data = core.execute_query(query, "Invoices-Credit Status", ec_user_id, ec_username)
        is_true = len(credit_data) > 0
        response = {
            "code": 1,
            "creditLimit": round(credit_data[0]["CreditLimit"], 2) if is_true else "",
            "outstandingInvoices": round(credit_data[0]["OpenInvoices"], 2) if is_true else "",
            "runningOrders": round(credit_data[0]["RunningOrdPrice"], 2) if is_true else "",
            "availableCredit": round(credit_data[0]["AvailableCredit"], 2) if is_true else "",
            "paymentTerms": str(credit_data[0]["PaymentTerms"]) + " " + "days" if is_true else "",
            "allAmountinSymbol_cust": credit_data[0]["CustomerSymbol"] if is_true else "",
            "creditLimit_cust": round(credit_data[0]["Customer_CreditLimit"], 2) if is_true else "",
            "outstandingInvoices_cust": round(credit_data[0]["Customer_OpenInvoices"], 2) if is_true else "",
            "runningOrders_cust": round(credit_data[0]["Customer_RunningOrdPrice"], 2) if is_true else "",
            "availableCredit_cust": round(credit_data[0]["Customer_AvailableCredit"], 2) if is_true else "",
        }
        sql_query = "exec sp_GetViewInvoiceOrder 50,1,1,'InvoiceDate','Desc', {0},493,'INVPENDING',3, 0,{1},''".format(ecc_user_id, company_id)
        invoice_orders = core.execute_query(sql_query, "Invoices-Credit Status", ec_user_id, ec_username)
        response["gridData"] = invoice_orders
        return {"data": response, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/save_grant_days/")
async def save_grant_days(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        query = "validForEditEnvoice {0}".format(data["invoiceId"])
        validate = core.execute_query(query, "Invoices-Grant days", ec_user_id, ec_username)
        is_valid = True if validate[0]["valid"] is True else False
        if is_valid:
            query = "EXEC sp_invoiceGrantDays '{0}',{1},{2}".format(data["invoiceId"], data["days"], data["ECCUserId"])
            core.execute_nonquery(query, "Invoices-Grant days", ec_user_id, ec_username)
        return {"data": "", "code": 1, "message": "Days granted successfully"}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_unmatched_proforma/")
async def search_unmatched_proforma(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        funname = data["funname"]
        Customer_Name = data["param"]["Customer_Name"]
        amount = data["param"]["Amount"]
        invoice_nr = data["param"]["InvoiceNr"]
        query = "exec Sp_selectCodaMapping '{0}'".format(Customer_Name)
        result = core.execute_query(query, "Payment browser unmatched-Search invoices", ec_user_id, ec_username)
        CustName = Customer_Name
        CustId = 0
        Ismaped = False
        fun_name = "SearchInvoice"
        if invoice_nr is not None:
            if "," in invoice_nr:
                invoice_nrs = str(invoice_nr).split(",")
                for invoice in invoice_nrs:
                    if invoice.startswith("E"):
                        fun_name = "SearchInvoice"
                    if invoice.startswith("P"):
                        fun_name = "SearchProformaInvoice"
            else:
                if invoice_nr.upper().startswith("E"):
                    fun_name = "SearchInvoice"
                if invoice_nr.upper().startswith("P"):
                    fun_name = "SearchProformaInvoice"

        if len(result) > 0:
            CustName = result[0]["companyname"] if "companyname" in result[0] else Customer_Name
            CustId = result[0]["companyId"] if "companyId" in result[0] else 0
            Ismaped = True

        if funname == "SearchUnmatchedInvoice":
            searchdata = {
                "ac1.UsageDescription": "PENDING",
                "c.CustomerName": CustName,
                "UM_CustomerId": CustId,
                "UM_IsFromCoda": "true",
                "UM_Amount": amount,
                "UM_Ismaped": Ismaped,
            }
            response = {"code": "1", "searchdata": searchdata, "funname": fun_name}
        if funname == "SearchUnmatchedProforma":
            searchdata = {"so.CustomerName": CustName, "UM_CustomerId": CustId, "UM_IsFromCoda": "true", "UM_Amount": amount, "UM_Ismaped": Ismaped}
            response = {"code": "1", "searchdata": searchdata, "funname": fun_name}
        return {"data": response, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_first_delivery/")
async def search_first_delivery(request: Request):
    try:
        data = await request.json()
        log_data = data["log_data"]
        data = data["param"]
        wherecluase = " 1=1"
        row_limit_val = "50"
        if "RowLimit" in data:
            row_limit_val = data["RowLimit"]
        if "DeliveryNo" in data:
            wherecluase += " and gd.Prefix+gd.DeliveryNo like ''%{0}%'' ".format(data["DeliveryNo"])
        if "DeliveryFromDate" and "DeliveryTillDate" in data:
            wherecluase += " and CONVERT(date, gd.CreatedOn, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["DeliveryFromDate"], data["DeliveryTillDate"]
            )
        if "sc.CustomerName" in data:
            wherecluase += "and sc.CustomerName like ''%{0}%'' ".format(data["sc.CustomerName"])
        if "sc.DeliveryCountry" in data:
            wherecluase += " and isnull( sc.DeliveryCountry,0) like ''%{0}%'' ".format(data["sc.DeliveryCountry"])
        if "so.is_assembly_data" in data:
            wherecluase += " and isnull( so.is_assembly_data,0) = ''{0}'' ".format(data["so.is_assembly_data"])
        if "sc.Subscribed" in data:
            wherecluase += " and isnull( sc.Subscribed,0) = ''{0}'' ".format(data["sc.Subscribed"])
        if "OrderedFromDate" in data and "OrderedTillDate" in data:
            wherecluase += " and CONVERT(date, so.OrderDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["OrderedFromDate"], data["OrderedTillDate"]
            )
        if "PlannedDeliveryFromDate" in data and "PlannedDeliveryTillDate" in data:
            wherecluase += " and CONVERT(date, so.DeliveryDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["PlannedDeliveryFromDate"], data["PlannedDeliveryTillDate"]
            )
        query = f"""EXEC sa_first_delivery_search '{wherecluase}',{row_limit_val}"""
        data = core.execute_query(query, "First deliveries", log_data["ec_user_id"], log_data["ec_username"])
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_orderv2/")
async def search_orderv2(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        row_limit = "10"
        wherecluase = " 1=1"
        if "RowLimit" in data:
            row_limit = data["RowLimit"]
        if "OrderNumber" in data:
            wherecluase += " and OrderNumber like ''{0}%'' ".format(data["OrderNumber"])
        if "PCBName" in data:
            wherecluase += " and PCBName like ''{0}%'' ".format(data["PCBName"])
        if "so.CustomerName" in data:
            wherecluase += " and so.CustomerName like ''{0}%'' ".format(data["so.CustomerName"])
        if "sc.VisitCountry" in data:
            wherecluase += " and sc.VisitCountry like ''{0}%'' ".format(data["sc.VisitCountry"])
        if "OrderStartDate" and "OrderEndDate" in data:
            wherecluase += " and CONVERT(date, so.OrderDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["OrderStartDate"], data["OrderEndDate"]
            )
        if "FromDeliveryDate" and "TillDeliveryDate" in data:
            wherecluase += " and CONVERT(date, so.DeliveryDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["FromDeliveryDate"], data["TillDeliveryDate"]
            )
        query = f"""exec sp_searchorders  '{wherecluase}','{row_limit}'"""
        data = core.execute_query(query, "Orders", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_invoice/")
async def search_invoice(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        rowlimit = "100"
        tracking_id = ""
        wherecluase = " 1=1"
        isSearchByOrder = False
        if "RowLimit" in data:
            rowlimit = data["RowLimit"]
        if "PaymentTrackingNumber" in data:
            tracking_id = data["PaymentTrackingNumber"]
        if "InvoiceNr" in data:
            wherecluase += " and i.Prefix+i.InvoiceNo like ''%{0}%'' ".format(data["InvoiceNr"])
        if "OrderNumber" in data:
            wherecluase += " and OrderNumber like ''%{0}%'' ".format(data["OrderNumber"])
            isSearchByOrder = True
        if "PCBName" in data:
            wherecluase += " and PCBName like ''%{0}%'' ".format(data["PCBName"])
            isSearchByOrder = True
        if "InvoiceValue" in data:
            wherecluase += " and InvoiceValue like ''%{0}%'' ".format(data["InvoiceValue"])
        if "c.CustomerName" in data:
            wherecluase += " and c.CustomerName like ''%{0}%'' ".format(data["c.CustomerName"])
        if "ac1.UsageDescription" in data:
            wherecluase += " and ac1.UsageDescription like ''%{0}%'' ".format(data["ac1.UsageDescription"])
        if "sac.UsageDescription" in data:
            wherecluase += " and sac.UsageDescription like ''%{0}%'' ".format(data["sac.UsageDescription"])
        if "c.InvoiceCountry" in data:
            wherecluase += " and c.InvoiceCountry like ''%{0}%'' ".format(data["c.InvoiceCountry"])
        if "c1.Name" in data:
            wherecluase += " and c1.Name like ''%{0}%'' ".format(data["c1.Name"])
        if "c.RootCompanyName" in data:
            wherecluase += " and c.RootCompanyName like ''%{0}%'' ".format(data["c.RootCompanyName"])
        if "c.InvoicePostalCode" in data:
            wherecluase += " and c.InvoicePostalCode like ''%{0}%'' ".format(data["c.InvoicePostalCode"])
        if "c.InvoiceCity" in data:
            wherecluase += " and c.InvoiceCity like ''%{0}%'' ".format(data["c.InvoiceCity"])
        if "c.InvoiceTelephone" in data:
            wherecluase += " and c.InvoiceTelephone like ''%{0}%'' ".format(data["c.InvoiceTelephone"])
        if "c.VATNr" in data:
            wherecluase += " and c.VATNr like ''%{0}%'' ".format(data["c.VATNr"])
        if "c.UserName" in data:
            wherecluase += " and c.UserName like ''%{0}%'' ".format(data["c.UserName"])
        if "IncludeDeletedProforma" in data:
            wherecluase += " and IncludeDeletedProforma like ''%{0}%'' ".format(data["IncludeDeletedProforma"])
        if "InvoiceFromDate" and "InvoiceTillDate" in data:
            wherecluase += " and CONVERT(date, i.InvoiceDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["InvoiceFromDate"], data["InvoiceTillDate"]
            )
        if "InvoiceDueFromDate" and "InvoiceDueTillDate" in data:
            wherecluase += " and CONVERT(date, i.InvoiceDueDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["InvoiceDueFromDate"], data["InvoiceDueTillDate"]
            )
        if isSearchByOrder:
            query = f"""exec sp_searchinvoicebyordernumber '{wherecluase}','{tracking_id}','{rowlimit}'"""
        else:
            query = f"""exec sp_Fastsearchinvoice '{wherecluase}','{tracking_id}','{rowlimit}'"""
        data = core.execute_query(query, "Invoices", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/get_pcbvis_url/")
async def get_pcbvis_url(request: Request):
    try:
        data = await request.json()
        order_nr = data["ordernum"]
        date_ticks = int(Util.ticks(datetime.utcnow()))
        ec_token = Util.encrypt_data(str(date_ticks))
        live_url = core.ECC_URL
        live_url = live_url + f"/shop/orders/pcb_visualizer.aspx?r={order_nr}"
        live_url += "&tokenid=" + ec_token.decode() + "&from=salesapp"
        data = {"url": live_url, "code": 1}
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/get_pcbavis_url/")
async def get_pcbavis_url(request: Request):
    try:
        data = await request.json()
        order_nr = data["ordernum"]
        date_ticks = int(Util.ticks(datetime.utcnow()))
        ec_token = Util.encrypt_data(str(date_ticks))
        live_url = core.ECC_URL
        live_url = live_url + f"/shop/assembly/assemblyeditor.aspx?number={order_nr}"
        live_url += "&tokenid=" + ec_token.decode() + "&from=salesapp"
        data = {"url": live_url, "code": 1}
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/getdoc/")
async def getdoc(request: Request):
    try:
        request_data = await request.json()
        date_ticks = int(Util.ticks(datetime.utcnow()))
        ec_token = Util.encrypt_data(str(date_ticks)).decode()
        live_url = core.ECC_URL
        url = ""
        doctype = request_data["doctype"]
        if "ordernr" in request_data:
            ordernr = Util.encrypt_data(str(request_data["ordernr"])).decode()
            url = "/shop/SalesappApi/getdoc.aspx?ordernr=" + ordernr + "&doctype=" + doctype + "&token=" + ec_token
        if "basketnr" in request_data:
            basketnr = Util.encrypt_data(str(request_data["basketnr"])).decode()
            url = "/shop/SalesappApi/getdoc.aspx?basketnr=" + basketnr + "&doctype=" + doctype + "&token=" + ec_token

        if "invoicenr" in request_data:
            invoicenr = Util.encrypt_data(str(request_data["invoicenr"])).decode()
            if str(request_data["invoicenr"]).startswith("P") and doctype == "performa":
                request_data["proformanr"] = request_data["invoicenr"]
            else:
                url = "/shop/SalesappApi/getdoc.aspx?invoicenr=" + invoicenr + "&doctype=" + doctype + "&token=" + ec_token
        if "proformanr" in request_data:
            proformanr = Util.encrypt_data(str(request_data["proformanr"])).decode()
            url = "/shop/SalesappApi/getdoc.aspx?proformanr=" + proformanr + "&doctype=" + doctype + "&token=" + ec_token
        if "deliverynr" in request_data:
            deliverynr = Util.encrypt_data(str(request_data["deliverynr"])).decode()
            url = "/shop/SalesappApi/getdoc.aspx?deliverynr=" + deliverynr + "&doctype=" + doctype + "&token=" + ec_token
        data = {"code": 1, "url": live_url + url}
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_proforma_invoice/")
async def proforma_invoice(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        row_limit = "10"
        wherclause = " i.StatusId in(553)  and  "
        wherclause += " 1=1"
        if "limit" in data:
            row_limit = data["limit"]
        if data["InvoiceNr"] != "":
            wherclause += " and i.Prefix+i.InvoiceNo like ''%{}%''".format(data["InvoiceNr"])
        if data["InvoiceValue"] != "":
            wherclause += " and InvoiceValue like ''%{}%''".format(data["InvoiceValue"])
        if data["OrderNumber"] != "":
            wherclause += " and OrderNumber like ''%{}%''".format(data["OrderNumber"])
        if data["PCBName"] != "":
            wherclause += " and PCBName like ''%{}%''".format(data["PCBName"])
        if data["so.CustomerName"] != "":
            wherclause += " and so.CustomerName like ''%{}%''".format(data["so.CustomerName"])
        if data["so.CustUserName"] != "":
            wherclause += " and so.CustUserName like ''%{}%''".format(data["so.CustUserName"])
        if data["so.CustCountry"] != "":
            wherclause += " and so.CustCountry like ''%{}%''".format(data["so.CustCountry"])
        if data["ac1.UsageDescription"] != "":
            wherclause += " and ac1.UsageDescription like ''%{}%''".format(data["ac1.UsageDescription"])
        if data["C.HandlingCompany"] != "":
            wherclause += " and C.HandlingCompany like ''%{}%''".format(data["C.HandlingCompany"])
        if data["C.RootCompanyName"] != "":
            wherclause += " and C.RootCompanyName like ''%{}%''".format(data["C.RootCompanyName"])
        if data["C.InvoicePostalCode"] != "":
            wherclause += " and C.InvoicePostalCode like ''%{}%''".format(data["C.InvoicePostalCode"])
        if data["C.InvoiceCity"] != "":
            wherclause += " and C.InvoiceCity like ''%{}%''".format(data["C.InvoiceCity"])
        if data["C.InvoiceTelephone"] != "":
            wherclause += " and C.InvoiceTelephone like ''%{}%''".format(data["C.InvoiceTelephone"])
        if data["C.VATNr"] != "":
            wherclause += " and C.VATNr like ''%{}%''".format(data["C.VATNr"])
        if data["InvoiceFromDate"] != "" and data["InvoiceTillDate"] != "":
            wherclause += " and CONVERT(date,i.InvoiceDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["InvoiceFromDate"], data["InvoiceTillDate"]
            )
        query = f"exec sp_offtheshelf_proforma '{wherclause}','{row_limit}',false"
        data = core.execute_query(query, "Proforma invoices", ec_user_id, ec_username)
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_payment_browser/")
async def search_payment_browser(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        data = data["param"]
        wherecluase = " 1=1"
        rowlimit = "100"
        if "RowLimit" in data:
            rowlimit = data["RowLimit"]
        if "InvoiceNo" in data:
            wherecluase += " and [InvoiceNo] like ''%{0}%'' ".format(data["InvoiceNo"])
        if "PaymentMode" in data:
            wherecluase += " and PaymentMode like ''%{0}%'' ".format(data["PaymentMode"])
        if "PaymentId" in data:
            wherecluase += " and PaymentId like ''%{0}%'' ".format(data["PaymentId"])
        if "Customer" in data:
            wherecluase += " and Customer like ''%{0}%'' ".format(data["Customer"])
        if "Country" in data:
            wherecluase += " and Country like ''%{0}%'' ".format(data["Country"])
        if "PaymentFromDate" and "PaymentTillDate" in data:
            wherecluase += " and CONVERT(date, PaymentDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["PaymentFromDate"], data["PaymentTillDate"]
            )
        if "InvoiceDueFromDate" and "InvoiceDueTillDate" in data:
            wherecluase += " and CONVERT(date, PaymentDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["InvoiceDueFromDate"], data["InvoiceDueTillDate"]
            )
        query = f"exec sp_PaymentBrowser '{wherecluase}','{rowlimit}'"
        data = core.execute_query(query, "Payment browser", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/search_payment_browser_unmatch/")
async def search_payment_browser_unmatch(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        data = data["param"]
        wherecluase = " 1=1"
        rowlimit = "100"
        if "RowLimit" in data:
            rowlimit = data["RowLimit"]
        if "Bank_Name" in data:
            wherecluase += " and Bank_Name like ''%{0}%'' ".format(data["Bank_Name"])
        if "Amount" in data:
            wherecluase += " and Amount like ''%{0}%'' ".format(data["Amount"])
        if "Bank_AccountNo" in data:
            wherecluase += " and Bank_AccountNo like ''%{0}%'' ".format(data["Bank_AccountNo"])
        if "Message" in data:
            wherecluase += " and Message like ''%{0}%'' ".format(data["Message"])
        if "Customer_Name" in data:
            wherecluase += " and Customer_Name like ''%{0}%'' ".format(data["Customer_Name"])
        if "gsc.InvoiceCountry" in data:
            wherecluase += " and gsc.InvoiceCountry like ''%{0}%'' ".format(data["gsc.InvoiceCountry"])
        if "CreatedFromDate" and "CreatedTillDate" in data:
            wherecluase += " and CONVERT(date, Created_Date, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["CreatedFromDate"], data["CreatedTillDate"]
            )
        query = f"""exec sp_PaymentBrowserUnmatch '{wherecluase}','{rowlimit}'"""
        data = core.execute_query(query, "Payment browser unmatched", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/get_invoice_history/")
async def get_invoice_history(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        invoice_id = data["invoiceId"]
        query = f"exec sp_GetInvoiceHistory {invoice_id}"
        data = core.execute_query(query, "Invoices-History", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/customer_financial_report/")
async def customer_financial_report(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        customerid = data["param"]["customerid"]
        query = f"""exec ecc_GetCompanywithAccountnr {customerid}"""
        data = core.execute_query(query, "Invoice-Customer financial report", ec_user_id, ec_username)
        finance_query = f"""Exec ECC_CustomerFinReport {customerid}"""
        finance_data = core.execute_query(finance_query, "Invoice-Customer financial report", ec_user_id, ec_username)
        is_finance_data = len(finance_data[0]) != 0
        TotalInvoice = 0
        TotalInvoiceAmount = 0
        TotalOpenAmount = 0

        invoice_query = f"""Exec ECC_GetOutstandingInvoices {customerid}"""
        invoice_data = core.execute_query(invoice_query, "Invoice-Customer financial report", ec_user_id, ec_username)
        dtfin = []
        if invoice_data and len(invoice_data) > 0:
            dtfin.extend(invoice_data)
            TotalInvoice = len(invoice_data)
            TotalInvoiceAmount = 0
            TotalOpenAmount = 0
            for i in invoice_data:
                TotalInvoiceAmount = TotalInvoiceAmount + i["Invoice_amount"]
                TotalOpenAmount = TotalOpenAmount + i["Open_amount"]
        response = {
            "code": "1",
            "CompanyCount": data[0]["CompanyCount"] if data and len(data[0]) > 0 else 0,
            "AccountNumber": data[0]["AccountNr"] if data and len(data[0]) > 0 else "",
            "CompanyName": data[0]["companyname"] if data and len(data[0]) > 0 else "",
            "CL_SystemLimit": finance_data[0]["creditLimit"] if is_finance_data and finance_data[0]["creditLimit"] is not None else "",
            "CL_InsuranceLimit": finance_data[0]["InsuranceLimit"] if is_finance_data and finance_data[0]["InsuranceLimit"] is not None else "",
            "CL_AvailableCredit": finance_data[0]["availableCredit"] if is_finance_data and finance_data[0]["availableCredit"] is not None else "",
            "CL_CreaditUsage90Days": finance_data[0]["90daycreaditusage"] if is_finance_data and finance_data[0]["90daycreaditusage"] is not None else "",
            "CL_TurnOver90": finance_data[0]["90orderintake"] if is_finance_data and finance_data[0]["90orderintake"] is not None else "",
            "CL_CreaditUsage180Days": finance_data[0]["180daycreaditusage"] if is_finance_data and finance_data[0]["180daycreaditusage"] is not None else "",
            "CL_TurnOver180": finance_data[0]["180orderintake"] if is_finance_data and finance_data[0]["180orderintake"] is not None else "",
            "CL_CreaditUsage360Days": finance_data[0]["360daycreaditusage"] if is_finance_data and finance_data[0]["360daycreaditusage"] is not None else "",
            "CL_TurnOver360": finance_data[0]["360orderintake"] if is_finance_data and finance_data[0]["360orderintake"] is not None else "",
            "RS_LastFirstReminder": finance_data[0]["Reminder1"] if is_finance_data and finance_data[0]["Reminder1"] is not None else "",
            "RS_LastSecondReminder": finance_data[0]["Reminder2"] if is_finance_data and finance_data[0]["Reminder2"] is not None else "",
            "RS_LastThirdReminder": finance_data[0]["Reminder3"] if is_finance_data and finance_data[0]["Reminder3"] is not None else "",
            "RS_AccountBlocked": finance_data[0]["AccountBlock"] if is_finance_data and finance_data[0]["AccountBlock"] is not None else "",
            "RS_LastPaymentDate": finance_data[0]["LastPayment"] if is_finance_data and finance_data[0]["LastPayment"] is not None else "",
            "RS_InvoiceNumber": finance_data[0]["InvoiceNo"] if is_finance_data and finance_data[0]["InvoiceNo"] is not None else "",
            "RS_PaidAmount": finance_data[0]["PaidAmt"] if is_finance_data and finance_data[0]["PaidAmt"] is not None else "",
            "PT_Averageterm": finance_data[0]["PaymentTerm"] if is_finance_data and finance_data[0]["PaymentTerm"] is not None else "",
            "PT_Averageterm90": finance_data[0]["90dayspaymentterm"] if is_finance_data and finance_data[0]["90dayspaymentterm"] is not None else "",
            "PT_Averageterm180": finance_data[0]["180dayspaymentterm"] if is_finance_data and finance_data[0]["180dayspaymentterm"] is not None else "",
            "PT_Averageterm360": finance_data[0]["360dayspaymentterm"] if is_finance_data and finance_data[0]["360dayspaymentterm"] is not None else "",
            "PT_Averagedelay90": finance_data[0]["90dayoustanding"] if is_finance_data and finance_data[0]["90dayoustanding"] is not None else "",
            "PT_Averagedelay180": finance_data[0]["180dayoustanding"] if is_finance_data and finance_data[0]["180dayoustanding"] is not None else "",
            "PT_Averagedelay360": finance_data[0]["360dayoustanding"] if is_finance_data and finance_data[0]["360dayoustanding"] is not None else "",
            "OutStandingInvoices": dtfin,
            "TotalInvoice": TotalInvoice,
            "TotalInvoiceAmount": TotalInvoiceAmount,
            "TotalOpenAmount": TotalOpenAmount,
        }
        return {"data": response, "code": 1}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/get_credit_limit/")
async def get_credit_limit(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        company_id = data["companyId"]
        query = f"exec ecc_getcreditlimit {company_id}"
        data = core.execute_query(query, "New customer-Credit limit", ec_user_id, ec_username)
        if data:
            data = {"code": 1, "data": data}
        else:
            data = {"code": 0, "data": "", "msg": "No records found."}
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


@invoicing.post("/save_credit_limit/")
async def save_credit_limit(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        companyId = data["companyId"]
        ECCUserid = data["ECCUserId"]
        systemLimit = data["systemLimit"]
        daysStart = data["daysStart"]
        insurance = data["insurance"]
        flag = data["flag"]
        query = f"""EXEC sp_invoiceCreditLimit {companyId},{ECCUserid},'{systemLimit}','{daysStart}','{insurance}',{flag}"""
        data = core.execute_nonquery(query, "Invoices-Credit limit update", ec_user_id, ec_username)
        data = {"code": 1, "data": "", "message": "Credit limit saved."}
        return {"data": data}
    except Exception as e:
        return {"code": 0, "msg": str(e)}


# for testing perpose

# @invoicing.post("/test_timer_log/")
# def test_timer_log():
#     data = core.execute_query("select top 20 * from DMIexchistory order by 1 desc ", "test", 191808)
#     print(data, "data")
#     return data


@invoicing.post("/order_status_by_panels/")
async def order_status_by_panels(request: Request):
    try:
        order_nr = await request.json()
        order_nr_ = order_nr["panel_numbers"]
        query = f"exec eger_orderstatus_by_panels '{order_nr_}'"
        data_ = core.execute_query(query, "Get order status", "0", "EC User")
        data = "<?xml version='1.0'?><Panels>"
        for da_ in data_:
            data +=f"""<Panel Number= "{da_["PanelNumber"]}" OrderNumber="{da_["OrderNumber"]}" OrderStatus="{da_["OrderStatus"]}"></Panel>"""
        data +="</Panels>"
        return Response(content=data, media_type="application/xml")
    except Exception as e:
        return {"code": 0, "msg": str(e)}
