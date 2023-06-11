import json
import logging

import requests
from base.models import AppResponse
from base.util import Util
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from exception_log import manager

from sales.service import CustomerService, SalesEcPyService, SalesService

# Create your views here.
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")


def new_customers(request):
    perms = [
        "view",
        "can_edit_new_customers_profile",
        "can_update_new_customer_credit_limit",
        "can_customer_login_new_customers",
        "can_add_new_customers_report",
        "can_update_new_customers_report",
    ]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "sales/new_customers.html", {"permissions": json.dumps(permissions)})


def new_customers_search(request):
    try:
        ec_py_service = SalesEcPyService()
        request.POST = Util.get_post_data(request)
        post_data = {
            "company_name": "",
            "handling_com": "",
            "root_company": "",
            "email": "",
            "country": "",
            "acc_manager": "",
            "company_dup": "",
            "included_steam": "",
            "created_from_date": "",
            "created_till_date": "",
            "limit": str(request.POST["length"]),
        }
        search_request = False
        if request.POST.get("company_name") is not None:
            post_data["company_name"] = request.POST["company_name"].strip()
            search_request = True
        if request.POST.get("handling_com") is not None:
            post_data["handling_com"] = request.POST["handling_com"].strip()
            search_request = True
        if request.POST.get("root_company") is not None:
            post_data["root_company"] = request.POST["root_company"].strip()
            search_request = True
        if request.POST.get("email") is not None:
            post_data["email"] = request.POST["email"].strip()
            search_request = True
        if request.POST.get("country") is not None:
            post_data["country"] = request.POST["country"].strip()
            search_request = True
        if request.POST.get("acc_manager") is not None:
            post_data["acc_manager"] = request.POST["acc_manager"].strip()
            search_request = True
        if request.POST.get("company_dup") is not None:
            post_data["company_dup"] = True if request.POST.get("company_dup") == "Yes" else False
            search_request = True
        if request.POST.get("included_steam") is not None:
            post_data["included_steam"] = "1" if request.POST.get("included_steam") == "Yes" else "0"
            search_request = True
        if request.POST.get("company_craeted_date") is not None:
            if "company_craeted_date_from_date" in request.POST:
                post_data["created_from_date"] = request.POST["company_craeted_date_from_date"].strip()
                post_data["created_till_date"] = request.POST["company_craeted_date_to_date"].strip()
                search_request = True
        ec_py_response = []
        if search_request:
            ec_py_end_point = "/ecpy/sales/get_new_customer/"

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
                    "id": resp["CompanyId"],
                    "company_name": resp["CompanyName"],
                    "vat_number": resp["VATNo"],
                    "handling_com": resp["HandlingCompany"],
                    "root_company": resp["RootCompany"],
                    "code": resp["Code"],
                    "email": resp["Email"],
                    "country": resp["Country"],
                    "acc_manager": resp["AccountManager"],
                    "company_dup": resp["Company duplicate"],
                    "created_date": resp["CreatedDate"],
                    "user_id": resp["UserId"],
                    "included_steam": resp["Included in Steam"],
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def update_included_steam(request):
    try:
        ec_py_service = SalesEcPyService()
        post_data = {"funname": "IncludeInSteam", "param": {"customerId": request.POST["customer_id"], "Subscribed": request.POST["included_steam"]}}
        ec_py_end_point = "/ecpy/sales/include_in_steam"
        ec_py_service.process_ec_data(post_data, ec_py_end_point, request)
        return HttpResponse(AppResponse.msg(1, ""), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in getting customer data")


def first_deliveries(request):
    perms = [
        "view",
        "can_edit_first_deliveries_profile",
        "can_add_first_deliveries_report",
        "can_update_first_deliveries_report",
    ]
    permissions = Util.get_permission_role(request.user, perms)
    return render(request, "sales/first_deliveries.html", {"permissions": json.dumps(permissions)})


def first_deliveries_search(request):
    try:
        ec_py_service = SalesEcPyService()
        search_request = False
        first_deliveries = []
        post_data = {"funname": "SearchFirstDelivery", "param": {"RowLimit": str(request.POST["length"])}}
        if request.POST.get("delivery_date__date") is not None:
            if "delivery_date__date_from_date" in request.POST:
                post_data["param"]["DeliveryFromDate"] = request.POST["delivery_date__date_from_date"].strip()
                post_data["param"]["DeliveryTillDate"] = request.POST["delivery_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("order_date__date") is not None:
            if "order_date__date_from_date" in request.POST:
                post_data["param"]["OrderedFromDate"] = request.POST["order_date__date_from_date"].strip()
                post_data["param"]["OrderedTillDate"] = request.POST["order_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("planned_delivery_date__date") is not None:
            if "planned_delivery_date__date_from_date" in request.POST:
                post_data["param"]["PlannedDeliveryFromDate"] = request.POST["planned_delivery_date__date_from_date"].strip()
                post_data["param"]["PlannedDeliveryTillDate"] = request.POST["planned_delivery_date__date_to_date"].strip()
                search_request = True

        if request.POST.get("Customer_name") is not None:
            post_data["param"]["sc.CustomerName"] = request.POST["Customer_name"].strip()
            search_request = True

        if request.POST.get("delivery_num") is not None:
            post_data["param"]["DeliveryNo"] = request.POST["delivery_num"].strip()
            search_request = True

        if request.POST.get("country") is not None:
            post_data["param"]["sc.DeliveryCountry"] = request.POST["country"].strip()
            search_request = True

        if request.POST.get("is_assembly_data") is not None:
            post_data["param"]["so.is_assembly_data"] = "1" if request.POST.get("is_assembly_data") == "Yes" else "0"
            search_request = True

        if request.POST.get("included_in_steam") is not None:
            post_data["param"]["sc.Subscribed"] = "1" if request.POST.get("included_in_steam") == "Yes" else "0"
            search_request = True

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": [],
        }
        if search_request:
            ec_py_end_point = "/ecpy/sales/search_first_delivery"
            first_deliveries = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
            for first_delivery in first_deliveries:
                response["data"].append(
                    {
                        "id": first_delivery["Customer_id"],
                        "Customer_name": first_delivery["Customer_name"],
                        "Delivery_note_number": first_delivery["Delivery_note_number"],
                        "Order_date": first_delivery["Order_date"],
                        "Delivery_note_date": first_delivery["Delivery_note_date"],
                        "Planned_delivery_date": first_delivery["Planned_delivery_date"],
                        "Order_type": first_delivery["Order_type"],
                        "Included_in_steam": first_delivery["Included_in_steam"],
                        "country": first_delivery["country"],
                        "Planned_delivery_date_incl_assembly": first_delivery["Planned_delivery_date_incl_assembly"],
                    }
                )
        response["recordsTotal"] = len(first_deliveries)
        response["recordsFiltered"] = len(first_deliveries)
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_delivery_note(request, delivery_note_num):
    try:
        fltr_data = {"deliverynr": delivery_note_num, "doctype": "deliverynote"}
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/getdoc"
        d = ec_py_service.search_ec_data(fltr_data, ec_py_end_point, request)
        if d["code"] == "0":
            ec_url = ""
        else:
            ec_url = d["url"]
        return redirect(ec_url)
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in doc view")


def create_task(request):
    try:
        title = request.POST.get("task_title")
        desc = request.POST.get("desc")

        url = "https://api.clickup.com/api/v2/list/11761383/task"
        payload = json.dumps(
            {
                "name": title,
                "description": desc,
                "status": "Open",
                "priority": 3,
                "due_date": 1508369194377,
                "due_date_time": False,
                "time_estimate": 8640000,
                "start_date": 1567780450202,
                "start_date_time": False,
                "notify_all": True,
                "parent": None,
                "links_to": None,
            }
        )
        headers = {"Authorization": "pk_3358931_O5OPFMOORDPJ9TSKL4PHGHIZLHBB928P", "Content-Type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=payload)

        return HttpResponse(AppResponse.msg(1, "Task created"), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception(str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
