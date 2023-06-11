import json
import re
from urllib import response

import core
from fastapi import APIRouter, Request

from .models import PrintingNeeds

customer = APIRouter()


@customer.post("/search_printing_needs/")
def search_printing_needs(request: PrintingNeeds):
    try:
        ec_user_id = request.log_data["ec_user_id"]
        ec_username = request.log_data["ec_username"]
        query = f"""exec salesApp_PrintingNeeds '{request.country}' ,'{request.region}','{request.orders}'
        ,{request.months},'{request.customer_name}','{request.included_steam}',{request.limit}"""
        data = core.execute_query(query, "Printing needs", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/save_user_detail/")
async def save_user_detail(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        response = {"data": None}
        UserId = data["UserId"]
        FirstName = data["FirstName"]
        LastName = data["LastName"]
        Email = data["Email"]
        Phone = data["Phone"]
        Mobile = data["Mobile"]
        Fax = data["Fax"]
        IM = data["IM"] if data["IM"] is not None else ""
        JobTitle = data["JobTitle"]
        ECCUserId = data["ECCUserId"] if data["ECCUserId"] is not None else "0"
        responsibility = data["user_responsibilities"]
        query = f"""EXEC SP_UpdateUserDetail {UserId},'{FirstName}','{LastName}','{Email}','{Phone}','{Mobile}','{Fax}','{JobTitle}',{ECCUserId},'{IM}','{responsibility}'"""
        data = core.execute_nonquery(query, "Sales-User update details ", ec_user_id, ec_username)
        response = {"code": "1", "message": "updated"} if data is True else {"code": "0", "message": "Internal Server Error."}
        return response
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/get_customer_report_que_ans/")
async def get_customer_report_que_ans(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        relation_id = data["param"]["relation_id"] if "relation_id" in data["param"] and data["param"]["relation_id"] is not None else "0"
        report_code = data["param"]["report_code"] if data["param"]["report_code"] is not None else "CUST_SURVEY"
        query = f"""EXEC sa_cr_get_questions_answer {relation_id},'{report_code}'"""
        response = core.execute_raw_query(query, "Sales-Report", ec_user_id, ec_username)
        final_ot = response[1]
        que_ans = []
        final = None
        if response and len(response) > 0 and response[0] is not None:
            if response and len(response) > 1 and response[1] is not None:
                for question in final_ot:
                    result = {"question_id": question["id"], "question": question["question"], "field": question["type"]}
                    que_ans.append(result)
                    result["options"] = []
                    for answer in response[2]:
                        if result["question_id"] == answer["question_id"]:
                            result["options"].append(answer)
                    final = {"report_id": response[0][0]["report_id"], "ec_action_needed": response[0][0]["ec_action_needed"], "questions": que_ans}
        else:
            final = ""
        return {"data": final}
    except Exception as e:
        return {"error": str(e)}


@customer.post("/save_survey_report/")
async def save_survey_report(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        data = data["param"]
        report_id = data["report_id"]
        customer_id = data["customer_id"]
        user_id = data["user_id"] if data["user_id"] is not None else "0"
        submitted_by_admin_id = data["submitted_by_admin_id"]
        submitted_by_customer_id = data["submitted_by_customer_id"] if data["submitted_by_customer_id"] is not None else "0"
        sub_rel_id = data["sub_rel_id"] if "sub_rel_id" in data and data["sub_rel_id"] is not None else "0"
        ec_action_needed = data["ec_action_needed"] if data["ec_action_needed"] is not None else False
        ecc_user_id = data["ec_user_id"] if "ec_user_id" in data and data["ec_user_id"] is not None else "0"
        response = {}
        if "answers" in data:
            jsonAnswer = data["answers"]
            question_id = ""
            submissin_rel_id = ""
            query = f"""EXEC sa_cust_survey_insert_update {report_id},{customer_id},{user_id},{submitted_by_admin_id},{submitted_by_customer_id},{sub_rel_id},{ec_action_needed} """
            sub_id = core.execute_return_query(query, "Sales-Report update", ec_user_id, ec_username)
            if sub_id and len(sub_id) > 0 and sub_id[0]:
                submissin_rel_id = sub_id[0]
                sql_insert_sub = ""
                answer = jsonAnswer
                for ans in answer:
                    question_id = ans["question_id"]
                    customer_answer = ans["answer_text"] if "answer_text" in ans and ans["answer_text"] is not None else ""
                    row = ans["answer"]
                    if isinstance(row, list):
                        for item in row:
                            sql_insert_sub += f"EXEC sa_cr_sub_rel_insert {submissin_rel_id},{question_id},'{item}','{customer_answer}' ;"
                    else:
                        sql_insert_sub += f"EXEC sa_cr_sub_rel_insert {submissin_rel_id},{question_id},'{row}','{customer_answer}' ;"
                response["relation_id"] = submissin_rel_id
                try:
                    created_by = submitted_by_admin_id if submitted_by_admin_id != "0" else submitted_by_customer_id
                    actionId = 0
                    origin = "SA"
                    if sub_rel_id == "0" or sub_rel_id == "":
                        actionId = core.execute_query("select CodeId from admCodes where code in ('CALLREPORTCREATED')", "Sales-Report admCodes", ec_user_id, ec_username)
                    else:
                        actionId = core.execute_query("select CodeId from admCodes where code in ('CALLREPORTCREATED')", "Sales-Report admCodes", ec_user_id, ec_username)
                        if ecc_user_id != "" and ecc_user_id != "0":
                            origin = "ECC"
                    actionId = actionId[0]["CodeId"]
                    sql = f"EXEC sa_cust_call_report_history_insert {submissin_rel_id},{actionId},{created_by},'{origin}'"
                    core.execute_nonquery(sql, "Sales-Report update", ec_user_id, ec_username)
                except Exception as ex:
                    return {"SaveSureyReport-History", 0, "insertData - " + data + " error - " + str(ex)}
                value = core.execute_nonquery(sql_insert_sub, "Sales-Report update", ec_user_id, ec_username)
                response["value"] = value
            return {"data": response}
        else:
            response = {"code": 2, "data": "", "message": "Data not saved."}
            return response
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/include_in_steam/")
async def include_in_steam(request: Request):
    try:
        data = await request.json()
        customer_id = data["param"]["customerId"]
        subscribed = data["param"]["Subscribed"]
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        query = "EXEC sa_include_in_steam {0},'{1}' ".format(customer_id, subscribed)
        data = core.execute_nonquery(query, "New customers-included in steam", ec_user_id, ec_username)
        data = {"data": data, "code": 1}
        return {"data": data}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/customer_login_validation/")
async def customer_login_validation(request: Request):
    try:
        data = await request.json()
        response = {"data": None}
        company_id = data["param"]["customerid"]
        valid_from = data["param"]["from"]
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        query = f"""exec sa_customerLoginValidation {company_id},'{valid_from}'"""
        response["data"] = core.execute_query(query, "Sales-Login", ec_user_id, ec_username)
        response["data"][0]["code"] = 1
        return response
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/search_customerv2/")
async def search_customerv2(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        response = {"data": None}
        rowlimit = "100"
        wherecluase = " 1=1"
        if "RowLimit" in data:
            rowlimit = data["RowLimit"]
        if "CustomerName" in data:
            wherecluase += " and CustomerName like ''%{0}%'' ".format(data["CustomerName"])
        if "FirstName" in data:
            wherecluase += " and FirstName like ''%{0}%'' ".format(data["FirstName"])
        if "sc.LastName" in data:
            wherecluase += " and sc.LastName like ''%{0}%'' ".format(data["sc.LastName"])
        if "ci.ContactValue" in data:
            wherecluase += " and ci.ContactValue like ''%{0}%'' ".format(data["ci.ContactValue"])
        if "sc.VisitCountry" in data:
            wherecluase += " and sc.VisitCountry like ''%{0}%'' ".format(data["sc.VisitCountry"])
        if "Subscribed" in data:
            wherecluase += " and Subscribed like ''%{0}%'' ".format(data["Subscribed"])
        if "RegistrationStartDate" and "RegistrationEndDate" in data:
            wherecluase += " and CONVERT(date, sc.RegistrationDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["RegistrationStartDate"], data["RegistrationEndDate"]
            )
        query = f"""exec sp_searchcustomers '{wherecluase}','{rowlimit}'"""
        response["data"] = core.execute_query(query, "Customers", ec_user_id, ec_username)
        return response
    except Exception as e:
        return {"error": str(e)}


@customer.post("/get_new_customer/")
async def get_new_customer(request: Request):
    try:

        data = await request.json()
        user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        row_limit = "10"
        wherecluase = "1=1"
        if "limit" in data:
            row_limit = data["limit"]
        if data["company_name"] != "":
            wherecluase += " and c.Name like ''%{}%''".format(data["company_name"])
        if data["handling_com"] != "":
            wherecluase += " and gs.HandlingCompany like ''%{}%''".format(data["handling_com"])
        if data["root_company"] != "":
            wherecluase += " and gs.RootCompanyName like ''%{}%''".format(data["root_company"])
        if data["email"] != "":
            wherecluase += " and gs.UserName  like ''%{}%''".format(data["email"])
        if data["country"] != "":
            wherecluase += " and gs.VisitCountry like ''%{}%''".format(data["country"])
        if data["acc_manager"] != "":
            wherecluase += " and gs.AccountManager like ''%{}%''".format(data["acc_manager"])
        if data["company_dup"] != "":
            wherecluase += " and c.Isduplicate = ''{}''".format(data["company_dup"])
        if data["included_steam"] != "":
            wherecluase += " and isnull(gs.Subscribed,0) = " + data["included_steam"]
        if data["created_from_date"] != "" and data["created_till_date"] != "":
            wherecluase += " and CONVERT(date,c.CreatedDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["created_from_date"], data["created_till_date"]
            )
        query = f"exec sp_GetNewCustomers '1','{wherecluase}','{row_limit}'"
        data = core.execute_query(query, "New customers ", user_id, ec_username)
        return {"data": data}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/get_offers/")
async def get_offers(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        row_limit = "10"
        wherecluase = "1=1"
        if "limit" in data:
            row_limit = data["limit"]
        if data["order_ref"] != "":
            wherecluase += " and sio.ProjectRef like ''{}%''".format(data["order_ref"])
        if data["customer_name"] != "":
            wherecluase += " and CustomerName like ''{}%''".format(data["customer_name"])
        if data["country"] != "":
            wherecluase += " and sio.CustCountry like ''{}%''".format(data["country"])
        if data["inquiery_no"] != "":
            wherecluase += " and INQNumber like ''{}%''".format(data["inquiery_no"])
        if data["inq_start_date"] != "" and data["inq_end_date"] != "":
            wherecluase += " and CONVERT(date,sio.inqofferdate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["inq_start_date"], data["inq_end_date"]
            )
        query = f"EXEC sp_searchoffers '{wherecluase}','{row_limit}'"
        data = core.execute_query(query, "Inquiries", ec_user_id, ec_username)
        return {"data": data}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/get_customer_profile/")
async def get_customer_profile(request: Request):
    try:
        cust_id = await request.json()
        customer_id = cust_id["customerid"]
        ec_user_id = cust_id["log_data"]["ec_user_id"]
        ec_username = cust_id["log_data"]["ec_username"]
        data = {}
        query = f"EXEC SP_getCustomerProfileDetail '{customer_id}'"
        customer_profile = core.execute_query(query, "Sales -Customer profile", ec_user_id, ec_username)
        customer_profile[0]["competence"] = customer_profile[0]["sa_company_competence"]
        customer_profile[0]["ec_customer_check"] = customer_profile[0]["sa_ec_customer"]
        del customer_profile[0]["sa_company_competence"], customer_profile[0]["sa_ec_customer"]
        data["Customer"] = customer_profile[0]
        language_id = data["Customer"]["LanguageId"]
        addresss_query = f"EXEC SP_getCustomerAddressDetail '{customer_id}','{language_id}'"
        addresses = core.execute_query(addresss_query, "Sales -Customer profile", ec_user_id, ec_username)
        data["Addresses"] = addresses
        contact_query = f"EXEC SP_getUserContactDetail '{customer_id}','{language_id}'"
        contact_details = core.execute_query(contact_query, "Sales -Customer profile", ec_user_id, ec_username)
        data["Users"] = contact_details
        if len(contact_details) > 0:
            contact_details[0]["user_responsibilities"] = contact_details[0]["sa_user_responsibilities"]
        profile_field_query = "EXEC SA_getCustomerProfileField"
        master_data = core.execute_raw_query(profile_field_query, "Sales -Customer profile", ec_user_id, ec_username)
        data["MasterData"] = {"competence": master_data[0], "ec_customer_check": master_data[1], "user_responsibilities": master_data[2]}
        log_details_query = f"EXEC SA_GetUserLogDetails {customer_id}"
        user_activities = core.execute_query(log_details_query, "Sales -Customer profile", ec_user_id, ec_username)
        data["UserActivities"] = user_activities
        comp_drop_down_query = f"EXEC SA_GetCompanyDropDownList {customer_id},{language_id}"
        accounts_data = core.execute_raw_query(comp_drop_down_query, "Sales -Customer profile", ec_user_id, ec_username)
        data["AccountManager"] = accounts_data[0] if len(accounts_data) > 0 else []
        data["TransportCompany"] = accounts_data[1] if len(accounts_data) > 1 else []
        data["InvoiceLanguage"] = accounts_data[2] if len(accounts_data) > 2 else []
        data["InvoiceDelivery"] = accounts_data[3] if len(accounts_data) > 3 else []
        data["AccountType"] = accounts_data[4] if len(accounts_data) > 4 else []
        data["OtherAccountType"] = accounts_data[5] if len(accounts_data) > 5 else []
        data["HandlingCompany"] = accounts_data[6] if len(accounts_data) > 6 else []
        data["CompanyStatus"] = accounts_data[7] if len(accounts_data) > 7 else []
        data["VatNo"] = accounts_data[8] if len(accounts_data) > 8 else []
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/customer_credit_report/")
async def customer_credit_report(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        query = f"""SELECT ReportXml FROM GloblGateWayReport where companyid={data["customer_id"]}"""
        data = core.execute_query(query, "Invoices-Credit report", ec_user_id, ec_username)
        if data:
            xml_data = data[0]["ReportXml"]
            response = {"code": "1", "xmldata": xml_data}
        else:
            response = {"code": "2", "message": "No record(s) found"}
        return {"data": response}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/get_customer_surveylist/")
async def get_customer_surveylist(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        customer_id = data["customer_id"]
        query = f"EXEC sa_get_survey_reports {customer_id}"
        data = core.execute_query(query, "Customer", ec_user_id, ec_username)
        return {"data": data, "code": 1, "surveylist": True}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/search_customer_call_reports/")
async def search_customer_call_reports(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        row_limit = "10"
        wherecluase = " 1=1"
        if "limit" in data:
            row_limit = data["limit"]
        if data["report_name"] != "":
            wherecluase += " and r.name like ''%{}%''".format(data["report_name"])
        if data["customer_name"] != "":
            wherecluase += " and sc.CustomerName like ''%{}%''".format(data["customer_name"])
        if data["gc.FirstName+ ' ' +gc.LastName"] != "":
            wherecluase += " and gc.FirstName+ '' '' +gc.LastName like ''%{}%''".format(data["gc.FirstName+ ' ' +gc.LastName"])
        if data["first_name"] != "":
            wherecluase += " and sc.FirstName like ''%{}%''".format(data["first_name"])
        if data["last_name"] != "":
            wherecluase += " and sc.LastName like ''%{}%''".format(data["last_name"])
        if data["country"] != "":
            wherecluase += " and sc.visitCountry like ''%{}%''".format(data["country"])
        if data["region"] != "":
            wherecluase += " and ar.RegionName like ''%{}%''".format(data["region"])
        if data["created_from_date"] and data["created_till_date"] != "":
            wherecluase += " and CONVERT(date,rsr.created_on, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["created_from_date"], data["created_till_date"]
            )
        if data["registerd_from_date"] and data["registerd_till_date"] != "":
            wherecluase += " and CONVERT(date,sc.RegistrationDate, 103) between CONVERT(datetime,''{0}'',103) and  CONVERT(datetime,''{1}'',103)".format(
                data["registerd_from_date"], data["registerd_till_date"]
            )
        if data["ec_action_needed"] == "true":
            wherecluase += " and rsr.ec_action_needed = 1 "
        if data["ec_action_needed"] == "false":
            wherecluase += " and isnull(rsr.ec_action_needed,0) = 0 "
        query = f"EXEC get_cust_call_reports '{wherecluase}',{row_limit}"
        data = core.execute_query(query, "Call reports", ec_user_id, ec_username)
        if data:
            response = {"data": data, "code": 1}
        else:
            response = {"code": "2", "message": "No record(s) found"}
        return response
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/update_customer_profile/")
async def update_customer_profile(request: Request):
    try:
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        company_id = data["CompanyId"]
        address_id = data["AddressId"]
        street_name = data["StreetName"]
        street_no = data["StreetNo"]
        address1 = data["Address1"]
        address2 = data["Address2"]
        city = data["City"]
        postal_code = data["PostalCode"]
        address_name = data["AddressName"]
        contact_name = data["ContactName"]
        ecc_user_id = data["ECCUserId"]
        telephone = data["Telephone"]
        email = data["Email"]
        fax = data["Fax"]
        box_no = data["BoxNo"]
        query = f"""EXEC SP_UpdateCustomerProfile '{company_id}','{address_id}','{street_name}',
            '{street_no}','{address1}','{address2}','{city}','{postal_code}','{address_name}',
            '{contact_name}','{ecc_user_id}','{telephone}','{email}','{fax}','{box_no}'"""
        data = core.execute_nonquery(query, "Sales-Address update", ec_user_id, ec_username)
        return {"data": data, "code": 1}
    except Exception as e:
        return {"code": 0, "message": str(e)}


@customer.post("/update_customer_preference/")
async def edit_customer_preference(request: Request):
    try:
        response = {}
        data = await request.json()
        ec_user_id = data["log_data"]["ec_user_id"]
        ec_username = data["log_data"]["ec_username"]
        ecc_user_id = data["ECCUserId"]
        company_id = data["CompanyId"]
        fnl_competence = data["competence"]
        fnl_ec_customer_check = data["ec_customer_check"]
        user_data = data["UserData"]
        user_data = "[" + user_data + "]"  # or "[{0}]".format(your_string)
        user_data = json.loads(user_data)
        handling_com_id = user_data[0]["HandlingCompanyId"]
        comp_status_id = user_data[0]["CompanyStatusId"]
        comp_status_remark = user_data[0]["CompanyStatusRemark"]
        vat_no = user_data[0]["VatNo"]
        vat_exists_conf = user_data[0]["VATExistsConfirmation"]
        is_exclude_vat = user_data[0]["IsExcludeVat"]
        old_is_exclude_vat = bool(user_data[0]["OldIsExcludeVat"])
        acc_manager_id = user_data[0]["AccountManagerId"]
        old_acc_manager_id = user_data[0]["OldAccountManagerId"]
        trans_comp_code = user_data[0]["TransportCompanyCode"]
        invo_delivery = user_data[0]["InvoiceDelivery"]
        old_invo_delivery = user_data[0]["OldInvoiceDelivery"]
        old_trans_comp_code = user_data[0]["OldTransportCompanyCode"]
        invoice_lang_id = user_data[0]["InvoiceLangId"]
        old_invoice_lang_id = user_data[0]["OldInvoiceLangId"]
        type_id = user_data[0]["TypeId"]
        old_type_id = str(user_data[0]["OtherTypeId"])
        tax_type_id = user_data[0]["TaxNumberTypeId"]
        rcs_code_query = "select CodeId from admCodes where code in ('TAXVATSIRETRCS')"
        rcs_code = core.execute_query(rcs_code_query, "Sales-Customer profile", ec_user_id, ec_username)
        stud_code_query = "select CodeId from admCodes where code in ('STUDENTCOMP')"
        student_code_id = core.execute_query(stud_code_query, "Sales-Customer profile", ec_user_id, ec_username)
        stud_team_code_query = "select CodeId from admCodes where code in ('STUDENTTEAMCOMP')"
        student_team_code_id = core.execute_query(stud_team_code_query, "Sales-Customer profile", ec_user_id, ec_username)
        teach_code_query = "select CodeId from admCodes where code in ('TEACHERCOMP')"
        teacher_code_id = core.execute_query(teach_code_query, "Sales-Customer profile", ec_user_id, ec_username)
        supplier_comp_query = "select CodeId from admCodes where code in ('SUPPLIERCOMP')"
        supplier_comp_id = core.execute_query(supplier_comp_query, "Sales-Customer profile", ec_user_id, ec_username)
        update_cust_query = f"EXEC SA_updateCustomerPreference {ecc_user_id},{company_id},'{fnl_competence}','{fnl_ec_customer_check}'"
        core.execute_nonquery(update_cust_query, "Sales-Customer profile", ec_user_id, ec_username)
        new_is_student = False
        new_is_student_team = False
        new_is_teacher = False
        if user_data is not None:
            validate_type_query = f"EXEC sa_validationTypeChange {company_id}"
            validate_data = core.execute_query(validate_type_query, "Sales-Customer profile", ec_user_id, ec_username)
            is_student = validate_data[0]["IsStudent"]
            is_teacher = validate_data[0]["IsTeacher"]
            is_student_team = validate_data[0]["IsStudentTeam"]
            is_assembly_partner = validate_data[0]["IsAssemblyPartner"]
            old_comp_status_id = str(validate_data[0]["CompanyStatusId"])
            old_tax_type_id = str(validate_data[0]["TaxNumberTypeId"])
            old_vat_no = validate_data[0]["VATNo"]
            user_id = validate_data[0]["UserId"]
            result_prefix = ""
            validate_msg = ""
            old_handling_com_id = str(validate_data[0]["HandlingCompId"]) if validate_data[0]["HandlingCompId"] else "0"
            if validate_data is not None:
                if handling_com_id != old_handling_com_id:
                    check_order_query = f"EXEC Ecc_CheckOrderIsExistForHand {company_id},{handling_com_id},{old_handling_com_id}"
                    is_exist_order = core.execute_query(check_order_query, "Sales-Customer profile", ec_user_id, ec_username)
                    if is_exist_order is not None:
                        if is_exist_order[0]["IsValidHC"] == "True":
                            if is_exist_order[0]["OrderCount"] > 0:
                                response = {"code": "2", "message": "HC can not be changed because orders history present", "messageType": ""}
                                return response
                check_user_name_query = f"exec spCheckUserNameExistRootCompanywise {company_id},{handling_com_id}"
                user_name_exist = core.execute_query(check_user_name_query, "Sales-Customer profile", ec_user_id, ec_username)
                UserNames = ""
                if user_name_exist is not None and len(user_name_exist) > 0:
                    message = (
                        f"{UserNames}- User(s) of this company already exists in Handling company you have selected to change.Please update user name to change handling company."
                    )
                    validate_msg = {"code": "2", "message": message, "messageType": ""}
                if is_student & is_teacher & is_assembly_partner & (old_type_id == student_code_id[0]["CodeId"] or old_type_id == teacher_code_id[0]["CodeId"]):
                    validate_msg = "Private/Business accounts can not be converted to Student/Teacher account"
                elif is_student & (old_type_id == teacher_code_id[0]["CodeId"] or old_type_id == is_assembly_partner or old_type_id == supplier_comp_id[0]["CodeId"]):
                    validate_msg = "Student accounts can not be converted other than Business/Private accounts."
                elif is_teacher & (old_type_id == student_code_id[0]["CodeId"] or old_type_id == is_assembly_partner or old_type_id == supplier_comp_id[0]["CodeId"]):
                    validate_msg = "Teacher accounts can not be converted other than Business/Private accounts."
                if validate_msg != "":
                    response = {"code": "2", "message": validate_msg, "messageType": ""}
                    return response
                if old_type_id == str(student_code_id[0]["CodeId"]):
                    new_is_student = True
                if old_type_id == str(student_team_code_id[0]["CodeId"]):
                    new_is_student_team = True
                if old_type_id == str(teacher_code_id[0]["CodeId"]):
                    new_is_teacher = True
            if old_comp_status_id != comp_status_id:
                if comp_status_remark == "":
                    response = {"code": "2", "message": "Status is not changed, remarks is mandatory.", "messageType": ""}
                    return response
            if validate_msg == "" and type_id != "377" and type_id != str(student_code_id[0]["CodeId"]):
                if validate_data[0]["VATNo"] != "" and len(validate_data[0]["VATNo"]) > 2:
                    rcs_prefix = ""
                    vat_prefix_query = f"exec ECC_GetVATPrefix {company_id}"
                    vat_prefix = core.execute_query(vat_prefix_query, "Sales-Customer profile", ec_user_id, ec_username)
                    result_prefix = vat_prefix[0]["VATPrefix"]
                    rcs_prefix = vat_prefix[0]["RCSPrefix"]
                    if rcs_prefix != "":
                        if old_tax_type_id == rcs_code[0]["CodeId"] and rcs_code[0]["CodeId"] != 0:
                            result_prefix = rcs_prefix
                    if vat_prefix is not None and vat_prefix != "":
                        r = re.compile(str(result_prefix), re.MULTILINE)
                        matches = [m.group() for m in r.finditer(vat_no)]
                        if len(matches) == 0:
                            response = {"code": "2", "message": "VAT number is not in proper format.", "messageType": ""}
                            return response

                if validate_data[0]["VATNo"] != vat_no:
                    lng_comp_id = "0"
                    check_vat_no_query = f"exec ECC_CheckVATNoExists {old_tax_type_id},{lng_comp_id},{lng_comp_id},'{vat_no}','true'"
                    check_vat_no = core.execute_query(check_vat_no_query, "Sales-Customer profile", ec_user_id, ec_username)
                    if lng_comp_id == 0:
                        vat_no_query = f"exec ECC_CheckVATNoExists {old_tax_type_id},{lng_comp_id},{lng_comp_id},'{vat_no}','false'"
                        check_vat_no = core.execute_query(vat_no_query, "Sales-Customer profile", ec_user_id, ec_username)
                        if check_vat_no != "" and len(check_vat_no) > 0:
                            if vat_exists_conf is True:
                                response = {"code": "2", "message": "VAT number already exists. do you want to proceed?", "messageType": "VAT_EXISTS_CONFIRMATION"}
                                return response
            if validate_msg != "":
                response = {"code": "2", "message": validate_msg, "messageType": ""}
                return response
            com_detail = ""
            if is_exclude_vat != old_is_exclude_vat:
                com_detail += f"Text extemtion - {old_is_exclude_vat}"
            if acc_manager_id != old_acc_manager_id:
                com_detail += f", AccountmanagerId- {old_acc_manager_id}"
            if trans_comp_code != old_trans_comp_code:
                com_detail += f", TransportCompanyCode- {old_trans_comp_code}"
            if invoice_lang_id != old_invoice_lang_id:
                com_detail += f", invoicelangId- {old_invoice_lang_id}"
            if type_id != old_type_id:
                com_detail += f", TypeId- {old_type_id}"
            if is_student != new_is_student:
                com_detail += f", IsStudent- {is_student}"
            if is_teacher != new_is_teacher:
                com_detail += f", IsTeacher-  {is_teacher}"
            if is_student_team != new_is_student_team:
                com_detail += f", IsStudentTeam-  {is_student_team}"
            if handling_com_id != old_handling_com_id:
                com_detail += f", HandlingCompId-  {handling_com_id}"
            if comp_status_id != old_comp_status_id:
                com_detail += f", CompanyStatusId- {old_comp_status_id}"
            if tax_type_id != old_tax_type_id:
                com_detail += f", TaxNumberTypeId- {old_tax_type_id}"
            if vat_no != old_vat_no:
                com_detail += f", VatNo- {old_vat_no}"
            update_query = f"""EXEC SA_updateCustomerProfile
            {ecc_user_id},{company_id},{is_exclude_vat},{acc_manager_id},{trans_comp_code},{invoice_lang_id},
            {invo_delivery},{old_invo_delivery},{type_id},{new_is_student},{new_is_teacher},{new_is_student_team},
            {handling_com_id},{user_id},{comp_status_id},{tax_type_id},'{vat_no}','{com_detail}'"""
            update_cust_profile = core.execute_nonquery(update_query, "Sales-Customer profile", ec_user_id, ec_username)
            if comp_status_id != old_comp_status_id and comp_status_remark != "":
                add_remark_query = f"exec ECC_AddRemarksWithDepartment {company_id},'{comp_status_remark}',{ecc_user_id},false,false,false,false,true,false,false"
                core.execute_nonquery(add_remark_query, "Sales-Customer profile", ec_user_id, ec_username)
            if update_cust_profile is True:
                response = {"code": 1, "message": "Customer profile updated", "messageType": ""}

        return response
    except Exception as e:
        return {"code": 0, "message": str(e)}
