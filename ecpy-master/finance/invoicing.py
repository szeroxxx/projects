from typing import Union

import core
from fastapi import APIRouter, Request

from .models import schedulePaymentReminder

finance = APIRouter()


# need to create common Exception -->


@finance.get("/search_discount/{company_id}/{limit}")
def search_discount(company_id: int, limit: int):
    try:
        query = f"exec ecc_GetDiscountDetails 'CompanyId={company_id} and 1=1 ' ,{limit} ,1"
        data = core.execute_query(query, "Search discount", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.get("/get_credit_limit/{company_id}/")
def get_credit_limit(company_id: int):
    try:
        query = "exec ecc_getcreditlimit {}".format(company_id)
        data = core.execute_query(query, "Get credit limit", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.post("/save_credit_limit/")
async def save_credit_limit(request: Request):
    try:
        data = await request.json()
        flag = data["invoice_date"]
        ec_company_id = data["ec_company_id"]
        system_limit = data["credit_limit"]
        days = data["days"]
        insurance = 0
        user_id = 1
        query = f"""select * from genCreditLimits with(nolock) where EntityId = {ec_company_id} and CreditLevelId=2 and ISNULL(IsDeleted,0)=0"""
        data = core.execute_query(query, "Save credit limit", 1, "Finance-App")
        if len(data) == 0:
            query = f"""insert into genCreditLimits(CreditLevelId,EntityId,SysCreditLimit,SysCreditPayLimitDays,InsCreditLimit,
                        PrepaidStatus,InvoiceDueDateType,CreatedBy,CreatedDate,IsDeleted)values
                        (2,"{ec_company_id}",'"{system_limit}"','" {days}"','"{insurance}"',1," {flag} ","{user_id}",GETUTCDATE(),0);
                        """
            data = core.execute_nonquery(query, "Save credit limit", 1, "Finance-App")
        else:
            query = f"""update genCreditLimits set CreditLevelId = 2, SysCreditLimit = {system_limit}, InsCreditLimit={insurance} ,SysCreditPayLimitDays = {days} ,
             InvoiceDueDateType = {flag} where EntityId = {ec_company_id}"""
            data = core.execute_nonquery(query, "Save credit limit", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.get("/check_discount_code/{code}/")
def check_discount_code(code: str):
    try:
        query = f"select DiscountCodeId from admDiscountCodes where DiscountCode = '{code}'"
        data = core.execute_query(query, "Check discount code", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.get("/get_discount_details/{code}/")
def get_discount_details(code: str):
    try:
        code_id_query = f"select DiscountCodeId from admDiscountCodes where DiscountCode = '{code}'"
        codes = core.execute_query(code_id_query, "Get discount details", 1, "Finance-App")
        code_id = codes[0]["DiscountCodeId"] if len(codes) > 0 else 0
        if code_id == 0:
            return {"code": 0}
        query = f"""select D.DiscountCodeid, D.DiscountCode, DG.DiscountValue
        from admDiscountCodes as D Inner Join admDiscountGroups as DG on D.DiscountGroupId = DG.DiscountGroupId where D.DiscountCodeId = {code_id}"""
        data = core.execute_query(query, "Get discount details", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.post("/update_coda_file/")
async def update_coda_file(request: Request):
    try:
        data = await request.json()
        response = {"data": None}
        xml_string = str(data["xml_string"])
        # created_by= data["created_by"]
        compared_xml_string = str(data["compared_xml_string"])
        file_name = data["file_name"]  # 2783369 for testing
        query = f"""EXEC InsertUpdateCodeFileInfo'{xml_string}',2783369,'{compared_xml_string}','{file_name}'"""
        response["data"] = core.execute_nonquery(query, "Update coda file", 1, "Finance-App")
        return response
    except Exception as e:
        return {"error": str(e)}


@finance.get("/performance_order_intake/{company_id}")
def performance_order_intake(company_id: int):
    try:
        query = f"Exec ECC_CustomerPerformanceReportForOrderIntake {company_id}"
        data = core.execute_raw_query(query, "Performance order intake", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.get("/performance_shipment/{company_id}")
def performance_shipment(company_id: int):
    try:
        query = f"Exec ECC_CustomerPerformanceReportForShipment {company_id}"
        data = core.execute_raw_query(query, "Performance shipment", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.get("/performance_request/{company_id}")
def performance_request(company_id: int):
    try:
        query_cust = f"Exec ECC_CustomerPerformanceReportForCustLOgin {company_id}"
        user_detail = core.execute_raw_query(query_cust, "Performance request", 1, "Finance-App")
        response = []
        for user in user_detail[0]:
            user_id = user["UserId"]
            request_query = f"exec ECC_GetUserDetailCompanywise {user_id}"
            data = core.execute_query(request_query, "Performance request", 1, "Finance-App")
            user_name = {"UserName": user["UserName"]}
            data.append(user_name)
            response.append(data)
        return {"data": response}
    except Exception as e:
        return {"error": str(e)}


@finance.get("/performance_after_sales/{company_id}")
def performance_after_sales(company_id: int):
    try:
        query = f"Exec ECC_CustomerPerformanceReportForClaim {company_id}"
        data = core.execute_raw_query(query, "Performance after sales", 1, "Finance-App")
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.get("/financial_report/{company_id}")
def financial_report(company_id: int):
    try:
        query_account = f"exec ecc_GetCompanywithAccountnr  {company_id}"
        account_data = core.execute_query(query_account, "Financial report", 1, "Finance-App")
        query_report = f"Exec ECC_CustomerFinReport  {company_id}"
        report_data = core.execute_query(query_report, "Financial report", 1, "Finance-App")
        query_outstanding = f"Exec ECC_GetOutstandingInvoices  {company_id}"
        outstanding_data = core.execute_query(query_outstanding, "Financial report", 1, "Finance-App")
        data = {"account_data": account_data, "report_data": report_data, "outstanding_data": outstanding_data}
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@finance.post("/insert_schedule_reminder/")
def insert_schedule_reminder(request: schedulePaymentReminder):
    data = request.items[0]
    is_include_pdf = None
    if data["is_include_pdf"] == 1:
        is_include_pdf = 1
    else:
        is_include_pdf = 0
    try:
        if data["invoice"]:
            query = f"""exec SchedulePaymentReminder {data['user_id']},{data['total_item']},'{data['scheduler_name']}' """
            datas = core.execute_query(query, "Insert schedule reminder", 1, "Finance-App")
            reminder_id = datas[0]["ReminderID"]
            for invo in request.items[0]["invoice"]:
                query = f"EXEC finapp_SchedulePaymentReminderItems {reminder_id},'{invo['invoice_number']}',{is_include_pdf}"
                data = core.execute_nonquery(query, "Insert schedule reminder", 1, "Finance-App")
        else:
            query = f"exec SchedulePaymentReminder '{data['scheduler_name']}' ,'{data['ec_customer_id']}','{data['is_include_pdf']}','{data['ec_schedule_id']}'"
            data = core.execute_nonquery(query, "Insert schedule reminder", 1, "Finance-App")
        return {"data": data, "code": 1, "message": "Reminder send"}
    except Exception as e:
        return {"error": str(e)}


@finance.post("/get_address/{ec_customer_id}")
def get_address(ec_customer_id=int):
    try:
        query = f"spGetCustCompanyAddresses {ec_customer_id},'0'"
        data = core.execute_query(query, "Get company address", 1, "Finance-App")
        return {"data": data, "code": 1, "message": "Company address"}
    except Exception as e:
        return {"error" : str(e)}


@finance.post("/change_invoice_status/")
def change_invoice_status(invoice_number: str, secondary_status: Union[str, None] = None):
    secondary_status = "" if secondary_status is None else secondary_status
    try:
        if secondary_status != "":
            query = f"EXEC Update_Status_SecondaryStatus '{invoice_number}','{secondary_status}','secondaryStatusUpdate'"
            data = core.execute_nonquery(query, "Change invoice status", 1, "Finance-App")
        else:
            query = "EXEC Update_Status_SecondaryStatus '{invoice_number}','INVCLOSED','{data_types}'"
            data = core.execute_nonquery(query, "Change invoice status", 1, "Finance-App")
        return {"data": data, "code": 1, "message": "status changed"}
    except Exception as e:
        return {"error": str(e)}


@finance.post("/get_credit_status/{customer_id}")
def get_credit_data(customer_id=int):
    query = f"exec spGetCreditDataForCompany {customer_id}"
    data = core.execute_query(query, "Search invoice-Credit status", 0, "EC-finance")
    return {"data": data}


@finance.get("/search_discount_lookup/")
async def search_discount_lookup(request: Request):
    try:
        data = await request.json()
        company_id = data["ec_customer_id"]
        group_code = data["group_code"]
        discount_code = data["discount_code"]
        limit = data["limit"]
        query = f"ecc_GetDiscountDetails 'GroupCode like ''%{group_code}%'' and DiscountCode like ''%{discount_code}%'' and CompanyId ={company_id}' ,'{limit}',1"
        data = core.execute_query(query, "Search discount", 1, "Finance-App")
        return {"data" : data}
    except Exception as e:
        return {"error": str(e)}
