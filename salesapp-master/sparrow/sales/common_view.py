import json
import logging
from datetime import datetime, timedelta

import base.views as base_views
import requests
from accounts.forms import CreateUserForm
from accounts.models import Group, GroupPermission, MainMenu, Permission, User, UserGroup, UserProfile
from auditlog import views as log_views
from auditlog.models import AuditAction, Auditlog
from base.models import AppResponse
from base.util import Util
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core import serializers
from django.core.cache import cache
from django.db import transaction
from django.db.models import CharField, Q
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, response
from django.shortcuts import redirect, render
from exception_log import manager
from sparrow.decorators import check_view_permission

from sales.models import Customers
from sales.service import SalesEcPyService, SalesService


def validate_customer_login(request):
    try:
        ec_py_service = SalesEcPyService()
        cust_id = request.POST.get("customer_id")
        valid_from = request.POST.get("from")
        post_data = {
            "funname": "CustomerLoginValidation",
            "param": {
                "customerid": cust_id,
                "from": valid_from,
            },
        }
        ec_py_end_point = "/ecpy/sales/customer_login_validation"
        ec_py_response = ec_py_service.search_ec_data(post_data, ec_py_end_point, request)
        data = {"code": ec_py_response[0]["code"], "msg": ec_py_response[0]["msg"]}
        if data["msg"] != "" and "\\n" in data["msg"]:
            data["msg"] = data["msg"].replace("\\n", "")

        user_id = request.session["user_id"]
        ec_user_id = UserProfile.objects.filter(user_id=user_id).values("ec_user_id").first()["ec_user_id"]
        data["ec_user_id"] = str(ec_user_id)

        return HttpResponse(AppResponse.get(data), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in redirection")


def validate_customer_login_modal(request):
    return render(request, "sales/customer_login_validation.html", {})


def launch_customer_login(request, entity_nr, from_loc, ecuser_id, customer_id):
    try:

        url = settings.EC_API_ROOT_URL + "/get-customer-login-url"
        fltr_data = {"customerid": customer_id, "eccUserId": ecuser_id, "from": from_loc}
        if entity_nr.lower() != "none":
            fltr_data["entityNumber"] = "/".join(entity_nr.split("-"))
        headers = {"content-type": "application/json", "token": settings.EC_SALES_TOKEN}
        ec_res = requests.post(url, data=json.dumps(fltr_data), headers=headers, timeout=5)
        data = ec_res.json()
        data = json.loads(data)
        if data["code"] == '1' and data["url"] != "":
            ec_url = data["url"]
        else:
            return HttpResponse(AppResponse.msg(404, "Could not find url, sorry."), content_type='json')
        return redirect(ec_url)
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in redirection")
        return HttpResponse(AppResponse.msg(0, "Something went wrong"), content_type='json')


def get_ec_doc(request, order_number, doc_type):
    try:
        fltr_data = {"ordernr": order_number, "doctype": doc_type}
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


def get_ec_customer_inv_doc(request, invoicenum1, invoicenum2, doc_type):
    try:
        fltr_data = {"invoicenr": invoicenum1 + "/" + invoicenum2, "doctype": doc_type}
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
        return HttpResponse("url not found.")


def get_ec_doc_inq(request, inq_number, doc_type):
    try:
        fltr_data = {"basketnr": inq_number, "doctype": doc_type}
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


def pcbvis(request, order_number):
    try:
        fltr_data = {"ordernum": order_number}
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/get_pcbvis_url"
        d = ec_py_service.search_ec_data(fltr_data, ec_py_end_point, request)

        if d["code"] == "0":
            ec_url = ""
        else:
            ec_url = d["url"]

        return redirect(ec_url)
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in doc view")


def pcbavis(request, order_number):
    try:
        fltr_data = {"ordernum": order_number}
        ec_py_service = SalesEcPyService()
        ec_py_end_point = "/ecpy/sales/get_pcbavis_url"
        d = ec_py_service.search_ec_data(fltr_data, ec_py_end_point, request)

        if d["code"] == "0":
            ec_url = ""
        else:
            ec_url = d["url"]
        return redirect(ec_url)
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong in doc view")
