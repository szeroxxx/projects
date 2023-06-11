import json
import logging
from datetime import datetime

from accounts.models import UserGroup, UserProfile
from base.models import AppResponse, AuthToken
from base.util import Util
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from exception_log import manager
from sparrow.decorators import check_view_permission
from stronghold.decorators import public

from sales.models import Customers
from sales.service import CustomerService, SalesEcPyService


@check_view_permission([{"sales": "sales_customer"}])
def customers(request):
    perms = ["view", "can_customer_login_customers", "can_add_customers_report", "can_update_customers_report"]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "sales/customers.html", {"permissions": json.dumps(permissions)})


def customers_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "RowLimit": str(request.POST["length"]),
        }

        search_request = False
        if request.POST.get("customer_name") is not None:
            post_data["CustomerName"] = request.POST["customer_name"].strip()
            search_request = True

        if request.POST.get("first_name") is not None:
            post_data["FirstName"] = request.POST["first_name"].strip()
            search_request = True

        if request.POST.get("last_name") is not None:
            post_data["sc.LastName"] = request.POST["last_name"].strip()
            search_request = True

        if request.POST.get("contact_email") is not None:
            post_data["ci.ContactValue"] = request.POST["contact_email"].strip()
            search_request = True

        if request.POST.get("company_country") is not None:
            post_data["sc.VisitCountry"] = request.POST["company_country"].strip()
            search_request = True

        if request.POST.get("included_steam") is not None:
            post_data["Subscribed"] = "1" if request.POST.get("included_steam") == "Yes" else "0"
            search_request = True

        if request.POST.get("register_start_date") is not None:
            post_data["RegistrationStartDate"] = request.POST["register_start_date"].strip()
            post_data["RegistrationEndDate"] = request.POST["register_end_date"].strip()
            search_request = True

        ec_py_response = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_customerv2"
            ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)

        recordsTotal = len(ec_py_response)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        cnt = 0
        for customer in ec_py_response:
            cnt += 1
            response["data"].append(
                {
                    "id": cnt,
                    "customer_id": customer["customer_id"],
                    "data__customer_name": customer["customer_name"],
                    "data__contact_firstname": customer["contact_firstname"],
                    "data__contact_lastname": customer["contact_lastname"],
                    "data__contact_email": customer["contact_email"],
                    "data__contact_phone": customer["contact_phone"],
                    "data__company_phone": customer["company_phone"],
                    "data__company_city": customer["company_city"],
                    "data__company_country": customer["company_country"],
                    "data__registration_date": customer["registration_date"],
                    "included_steam": customer["Included in Steam"],
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_customer(request, edit_customer_from, customer_id, can_add_report, can_update_report):
    try:
        cust_service = CustomerService(invalidate_customer_cache=True, request=request)
        customer = cust_service.get_customer_detail(customer_id, request)
        cust_data = cust_service.get_customer(customer_id, request)
        activities = cust_service.get_customer_activities(customer_id, request)
        role_obj = UserGroup.objects.filter(user_id=request.session["user_id"]).values("group__name")
        roles = [role_name["group__name"].lower() for role_name in role_obj]

        perms = []
        if edit_customer_from == "inv":
            perms.append("can_edit_profile_invoice")
        if edit_customer_from == "proforma_inv":
            perms.append("can_edit_profile_proforma_invoice")
        if edit_customer_from == "payment_browser":
            perms.append("can_edit_profile_payment_browser")
        if edit_customer_from == "ord":
            perms.append("can_edit_profile_orders")
        if edit_customer_from == "customers":
            perms.append("can_edit_profile_customers")
        if edit_customer_from == "new_customers":
            perms.append("can_edit_new_customers_profile")
        if edit_customer_from == "first_deliveries":
            perms.append("can_edit_first_deliveries_profile")
        permissions = Util.get_permission_role(request.user, perms)
        report_permisions = {}
        report_permisions["can_add_report"] = can_add_report
        report_permisions["can_update_report"] = can_update_report
        MasterData = cust_service.get_customer_master_data(customer_id, request)
        return render(
            request,
            "sales/customer.html",
            {
                "roles": roles,
                "customer": customer,
                "permissions": json.dumps(permissions),
                "MasterData": MasterData,
                "CustomerData": cust_data,
                "report_permisions": report_permisions,
                "edit_customer_from": edit_customer_from,
                "activities": activities[0] if len(activities) > 0 else False,
            },
        )

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def get_customer_addresses(request, customer_id):
    try:
        cust_service = CustomerService(request=request)
        addresses = cust_service.get_customer_addresses(customer_id, request)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": 2,
            "recordsFiltered": 2,
            "data": [],
        }
        for address in addresses:
            response["data"].append(
                {
                    "id": address["AddressId"],
                    "ContactName": address["ContactName"],
                    "AddressName": address["AddressName"],
                    "AddressType": address["AddressType"],
                    "Address": address["StreetName"] + " " + address["StreetNo"] + ", " + address["PostalCode"] + " " + address["City"] + ", " + address["Country"],
                    "Telephone": address["Telephone"],
                    "Email": address["Email"],
                    "IsPrimaryAddress": address["IsPrimaryAddress"],
                    "BoxNo": address["BoxNo"],
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def get_customer_address(request):
    try:
        customer_id = request.POST["customer_id"]
        address_id = int(request.POST["address_id"])
        cust_service = CustomerService(request=request)
        addresses = cust_service.get_customer_addresses(customer_id, request)
        address = [addr for addr in addresses if addr["AddressId"] == address_id][0]
        return render(request, "sales/address.html", {"address": address})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def save_customer_address(request):
    try:
        post_data = {}
        for key in request.POST:
            if key == "csrfmiddlewaretoken":
                continue
            post_data[key] = request.POST[key]
        profile = UserProfile.objects.filter(user_id=request.user.id).first()
        post_data["ECCUserId"] = profile.ec_user_id
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        ec_py_end_point = "/ecpy/sales/update_customer_profile/"
        ec_py_response = ec_py_service.process_ec_data(post_data, ec_py_end_point, request)
        if ec_py_response["data"] == "false":
            return HttpResponse(AppResponse.msg(0, "Something went wrong. Address not saved."), content_type="json")

        # Just to clear customer cache
        cust_service = CustomerService(invalidate_customer_cache=True, request=request)
        cust_service.get_customer_detail(post_data["CompanyId"], request)

        return HttpResponse(AppResponse.msg(1, ""), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_customer_users(request, customer_id=None):
    try:
        cust_service = CustomerService(request=request)
        users = cust_service.get_customer_users(customer_id, request)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": 2,
            "recordsFiltered": 2,
            "data": [],
        }
        for user in users:
            response["data"].append(
                {
                    "id": user["UserId"],
                    "UserName": user["UserName"],
                    "FirstName": user["FirstName"],
                    "LastName": user["LastName"],
                    "Status": user["Status"],
                    "Responsibility": user["Responsibility"],
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def get_call_reports(request, customer_id=None):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {"customer_id": customer_id}
        ec_py_response = []

        ec_py_end_point = "/ecpy/sales/get_customer_surveylist/"
        ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        recordsTotal = len(ec_py_response)
        # sales_service = SalesService()
        # post_data = {"funname": "GetCustomerSurveyList", "param": {"customer_id": customer_id}}
        # all_reports = sales_service.request_ec_data(post_data, "api/v1")
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for report in ec_py_response:
            response["data"].append(
                {
                    "relation_id": report["relation_id"],
                    "Report_name": report["Report_name"],
                    "Created_by": report["Created_by"],
                    "Created_on": report["Created_on"],
                    "report_type": report["report_type"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_date_format(date):
    if date is not None:
        new_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:" + date.split(":")[-1]).strftime("%Y/%m/%d %H:%M %p")
        return new_date
    return None


def get_cust_user_view(request):
    try:
        customer_id = request.POST["customer_id"]
        user_id = int(request.POST["user_id"])
        cust_service = CustomerService(request=request)
        users = cust_service.get_customer_users(customer_id, request)
        user = [usr for usr in users if usr["UserId"] == user_id][0]
        MasterData = cust_service.get_customer_master_data(customer_id, request)
        return render(request, "sales/customer_user.html", {"user": user, "MasterData": MasterData})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def save_customer_user(request):
    try:
        ec_py_service = SalesEcPyService()
        post_data = {}
        for key in request.POST:
            if key == "csrfmiddlewaretoken":
                continue
            post_data[key] = request.POST[key]
        profile = UserProfile.objects.filter(user_id=request.user.id).first()
        post_data["ECCUserId"] = profile.ec_user_id
        ec_py_end_point = "/ecpy/sales/save_user_detail"
        response = ec_py_service.process_ec_data(post_data, ec_py_end_point, request)

        if response["code"] == 0:
            return HttpResponse(AppResponse.msg(0, "Something went wrong. User not saved."), content_type="json")

        # Just to clear customer cache
        cust_service = CustomerService(invalidate_customer_cache=True, request=request)
        cust_service.get_customer_detail(post_data["CompanyId"], request)

        return HttpResponse(AppResponse.msg(1, ""), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def export_customers(request):
    query = CustomerService(request=request).get_customers_list_query_object(request.POST)

    customers = (
        Customers.objects.filter(query)
        .values(
            "data__customer_name",
            "data__company_phone",
            "data__company_city",
            "data__company_country",
            "data__contact_firstname",
            "data__contact_lastname",
            "data__contact_phone",
            "data__contact_email",
            "data__registration_date",
        )
        .order_by("-data__customer_id")[0:2000]
    )

    headers = [
        {"title": "Customer Name"},
        {"title": "Company Phone"},
        {"title": "City"},
        {"title": "Country"},
        {"title": "Contact First Name"},
        {"title": "Contact Last Name"},
        {"title": "Contact Phone"},
        {"title": "Contact Email"},
        {"title": "Registration Date", "type": "date"},
    ]
    return Util.export_to_xls(headers, customers, "customers.xls")


def save_customer_data(request):
    try:
        if request.method == "POST":
            profile = UserProfile.objects.filter(user_id=request.user.id).first()
            ec_py_service = SalesEcPyService()
            request.POST = Util.get_post_data(request)
            payload = {}
            compentence = request.POST.get("competence").replace("[", "").replace("]", "").replace('"', "") if request.POST.get("competence") else ""
            payload["competence"] = compentence
            ec_customer_check = request.POST.get("ec_customer_check").replace("[", "").replace("]", "").replace('"', "") if request.POST.get("ec_customer_check") else ""
            payload["ec_customer_check"] = ec_customer_check
            payload["CompanyId"] = request.POST["CompanyId"]
            payload["ECCUserId"] = profile.ec_user_id
            payload["UserData"] = request.POST["user_details"]
            ec_py_end_point = "/ecpy/sales/update_customer_preference/"
            ec_py_response = ec_py_service.process_ec_data(payload, ec_py_end_point, request)
            cust_service = CustomerService(invalidate_customer_cache=True, request=request)
            cust_service.get_customer_detail(request.POST["CompanyId"], request)
        return HttpResponse(AppResponse.get(ec_py_response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def survey_report(request, customer_id, relation_id, can_update_report, report_type):
    try:
        form_data = get_survey_report_form_data(customer_id, relation_id, can_update_report, "false", report_type, request)
        return render(request, "sales/survey_report.html", {"data": json.dumps(form_data)})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def save_survey_report(request, opened_from_ec):
    try:
        ec_py_service = SalesEcPyService()
        data = json.loads(request.POST["data"])
        ec_userid = UserProfile.objects.filter(user_id=request.user.id).first().ec_user_id
        data["submitted_by_admin_id"] = data["ec_user_id"] if opened_from_ec == "true" else ec_userid
        post_data = {"funname": "SaveSureyReport", "param": data}
        ec_py_end_point = "/ecpy/sales/save_survey_report"
        response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        return HttpResponse(json.dumps({"code": 1, "msg": "Report saved", "relation_id": response["relation_id"]}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def all_call_reports(request):
    perms = ["can_add_customers_report", "can_update_customers_report"]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "sales/call_reports.html", {"permissions": json.dumps(permissions)})


def all_call_reports_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "report_name": "",
            "customer_name": "",
            "created_by": "",
            "first_name": "",
            "last_name": "",
            "country": "",
            "region": "",
            "created_from_date": "",
            "created_till_date": "",
            "registerd_from_date": "",
            "registerd_till_date": "",
            "ec_action_needed": "",
            "gc.FirstName+ ' ' +gc.LastName": "",
            "limit": str(request.POST["length"]),
        }
        search_request = False
        if request.POST.get("ReportName") is not None:
            post_data["report_name"] = request.POST.get("ReportName").strip()
            search_request = True
        if request.POST.get("CustomerName") is not None:
            post_data["customer_name"] = request.POST["CustomerName"].strip()
            search_request = True
        if request.POST.get("CreatedBy") is not None:
            post_data["gc.FirstName+ ' ' +gc.LastName"] = request.POST["CreatedBy"].strip()
            search_request = True
        if request.POST.get("FirstName") is not None:
            post_data["first_name"] = request.POST["FirstName"].strip()
            search_request = True
        if request.POST.get("LastName") is not None:
            post_data["last_name"] = request.POST["LastName"].strip()
            search_request = True

        if request.POST.get("Country") is not None:
            post_data["country"] = request.POST["Country"].strip()
            search_request = True

        if request.POST.get("Region") is not None:
            post_data["region"] = request.POST["Region"].strip()
            search_request = True

        if request.POST.get("created_date__date") is not None:
            if "created_date__date_from_date" in request.POST:
                post_data["created_from_date"] = request.POST["created_date__date_from_date"].strip()
                post_data["created_till_date"] = request.POST["created_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("registered_date__date") is not None:
            if "registered_date__date_from_date" in request.POST:
                post_data["registerd_from_date"] = request.POST["registered_date__date_from_date"].strip()
                post_data["registerd_till_date"] = request.POST["registered_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("ec_action_needed") is not None:
            post_data["ec_action_needed"] = "true" if request.POST.get("ec_action_needed") == "Yes" else "false"
            search_request = True
        ec_py_response = []

        if search_request:
            ec_py_end_point = "/ecpy/sales/search_customer_call_reports/"
            ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        recordsTotal = len(ec_py_response)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        if len(ec_py_response) > 0:
            for report in ec_py_response:
                response["data"].append(
                    {
                        "relation_id": report["relation_id"],
                        "CustomerName": report["CustomerName"],
                        "FirstName": report["FirstName"],
                        "LastName": report["LastName"],
                        "Email": report["Email"],
                        "ReportName": report["ReportName"],
                        "Created_by": report["Created_by"],
                        "Created_on": report["Created_on"],
                        "customer_id": report["customer_id"],
                        "ec_action_needed": report["ec_action_needed"],
                        "Country": report["Country"],
                        "Region": report["Region"],
                        "Registered_on": report["Registered_on"],
                        "report_type": report["report_type"],
                    }
                )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def authentication_request(request, token):
    try:
        result = {"code": 0, "msg": "Invalid token", "user_id": 0}
        if token == "" or token is None:
            return result
        auth_token = AuthToken.objects.filter(token=token).first()
        if auth_token:
            expire_on = auth_token.expire_on.replace(tzinfo=None)
            current_time = datetime.utcnow()
            if expire_on >= current_time:
                email = "ec_user_readonly@gmail.com"
                user = User.objects.filter(email=email).first()
                if "username" not in request.session:
                    user = User.objects.filter(email=email).first()
                    login(request, user)
                result["code"] = 1
        return result
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
@csrf_exempt
def public_survey_report(request, customer_id, relation_id, can_update_report, token, ec_userid, report_type):
    try:
        res = authentication_request(request, token)
        if res["code"] == 0:
            return HttpResponse(json.dumps(res), content_type="json")
        form_data = get_survey_report_form_data(customer_id, relation_id, can_update_report, "true", report_type, request)
        form_data["ec_userid"] = ec_userid
        return render(request, "sales/survey_report.html", {"data": json.dumps(form_data)})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def get_survey_report_form_data(customer_id, relation_id, can_update_report, open_from_ec, report_type, request):
    post_data = {"funname": "GetCustReportQuesAns", "param": {}}
    post_data["param"] = {} if int(relation_id) == 0 else {"relation_id": relation_id}
    post_data["param"]["report_code"] = report_type
    ec_py_service = SalesEcPyService()
    ec_py_end_point = "/ecpy/sales/get_customer_report_que_ans"
    form_data = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
    form_data["customer_id"] = customer_id
    form_data["can_update_report"] = can_update_report
    form_data["ec_userid"] = 0
    form_data["open_from_ec"] = open_from_ec
    form_data["report_type"] = report_type
    return form_data


@check_view_permission([{"sales": "printing_needs"}])
def printing_needs(request):
    perms = ["view", "can_do_customer_login", "can_add_report", "can_update_report"]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "sales/printing_needs.html", {"permissions": json.dumps(permissions)})


def printing_need_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "country": "",
            "region": "",
            "orders": 0,
            "months": 0,
            "customer_name": "",
            "included_steam": "",
            "limit": str(request.POST["length"]),
        }

        search_request = False
        if request.POST.get("country") is not None:
            post_data["country"] = request.POST["country"].strip()
            search_request = True

        if request.POST.get("y_orders") is not None and str(request.POST.get("y_orders")).isnumeric():
            post_data["orders"] = request.POST["y_orders"].strip()
            search_request = True

        if request.POST.get("y_months") is not None and str(request.POST.get("y_months")).isnumeric():
            post_data["months"] = request.POST["y_months"].strip()
            search_request = True

        if request.POST.get("region") is not None:
            post_data["region"] = request.POST["region"].strip()
            search_request = True

        if request.POST.get("customer_name") is not None:
            post_data["customer_name"] = request.POST["customer_name"].strip()
            search_request = True

        if request.POST.get("included_steam") is not None:
            post_data["included_steam"] = request.POST["included_steam"].strip().lower()
            search_request = True
        ec_py_response = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_printing_needs"
            ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)

        recordsTotal = len(ec_py_response)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        count = 0
        for resp in ec_py_response:
            count += 1
            response["data"].append(
                {
                    "id": count,
                    "customer_id": resp["CustomerID"],
                    "data__customer_name": resp["CustomerName"],
                    "data__contact_firstname": resp["FirstName"],
                    "data__contact_lastname": resp["LastName"],
                    "data__contact_email": resp["VisitEmail"],
                    "data__company_phone": resp["VisitTelephone"],
                    "data__company_city": resp["VisitCity"],
                    "data__company_country": resp["VisitCountry"],
                    "data__registration_date": resp["RegistrationDate"],
                    "number_of_PCB_orders": resp["#PCB orders"],
                    "number_of_Assembly_orders": resp["#ASS orders"],
                    "included_steam": resp["Included in Steam"],
                    "TotalRows": resp["TotalRows"],
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
