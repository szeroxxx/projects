import base64
import calendar
import datetime
import itertools
import json
import logging
import os
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from uuid import uuid4

import requests
from accounts.models import UserGroup, UserProfile
from attachment.models import FileType
from attachment.views import upload_and_save_impersonate
from auditlog import views as log_views
from auditlog.models import AuditAction, Auditlog
from base import views as base_views
from base.choices import (bottom_legend, bottom_solder_mask,
                          customer_specific_parameter, delivery_term,
                          layer_code_gtn, material_tg, nc_type, operator_group,
                          operator_type, order_status, permanent_shift, shift,
                          surface_finish, technical_parameter, top_legend,
                          top_solder_mask, years_of_experience)
from base.models import AppResponse, CommentType, DocNumber, Remark
from base.util import Util
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import (Case, Count, F, FloatField, IntegerField, Max,
                              OuterRef, Q, Subquery, Sum, Value, When)
from django.db.models.deletion import ProtectedError
from django.db.models.functions import Cast, Coalesce, Replace
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from exception_log import manager
from mails.views import send_mail
from PIL import Image
from sparrow.decorators import check_view_permission
from stronghold.decorators import public
from task.models import Message, Task

from pws.forms import CompanyForm, CompanyParameterForm
from pws.models import (ActiveOperators, BoardThickness, Company,
                        CompanyParameter, CompanyUser, CompareData, Efficiency,
                        Layer, ManageAutoAllocation, NcCategory, NonConformity,
                        NonConformityDetail, Operator, OperatorLogs, Order,
                        Order_Attachment, OrderAllocationFlow, OrderException,
                        OrderFlowMapping, OrderProcess, OrderScreen,
                        OrderScreenParameter, OrderTechParameter,
                        PerformanceIndex, PreDefineExceptionProblem, Service,
                        SkillMatrix, SubGroupOfOperator, TechnicalHelp,
                        UserEfficiencyLog)
from pws.service import ImportOrder, PWSEcPyService

img_uuid = str(uuid4())

# Create your views here.


@check_view_permission([{"customer": "pws_customers"}])
def customers_view(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_set_order_screen", "can_customer_place_order", "can_export_customers"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/customers.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def customer(request, company_id):
    try:
        company = None
        if company_id != "0":
            company = Company.objects.get(id=company_id)
            company_parameter = CompanyParameter.objects.get(company_id=company.id)
            company_form = CompanyForm(request.POST or None, instance=company)
            company_parameter_form = CompanyParameterForm(request.POST or None, instance=company_parameter)
        else:
            company_parameter_form = CompanyParameterForm(request.POST)
            company_form = CompanyForm(request.POST)
        return render(request, "pws/customer.html", {"form": company_parameter_form, "comp_form": company_form, "company": company})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_customer(request):
    try:
        with transaction.atomic():
            company_id = request.POST.get("company_id")
            gen_mail_ = request.POST.get("gen_mail_").lower()
            ord_rec_mail_ = request.POST.get("ord_rec_mail_").lower()
            ord_exc_gen_mail_ = request.POST.get("ord_exc_gen_mail_").lower()
            ord_exc_rem_mail_ = request.POST.get("ord_exc_rem_mail_").lower()
            ord_comp_mail_ = request.POST.get("ord_comp_mail_").lower()
            mail_from_ = request.POST.get("mail_from_").lower()
            int_exc_from_ = request.POST.get("int_exc_from_").lower()
            int_exc_to_ = request.POST.get("int_exc_to_").lower()
            int_exc_cc_ = request.POST.get("int_exc_cc_").lower()
            new_image = ""
            response = {}
            if company_id != "0":
                if Util.has_perm("edit_customers", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                if request.method == "POST":
                    company = Company.objects.get(id=company_id)
                    company_parameter = CompanyParameter.objects.get(company_id=company.id)
                    company_form = CompanyForm(request.POST or None, instance=company)
                    company_parameter_form = CompanyParameterForm(request.POST or None, instance=company_parameter)
                    if company_form.is_valid() and company_parameter_form.is_valid():
                        name = company_form.cleaned_data["name"]
                        if Company.objects.filter(Q(name__iexact=name, is_deleted=False), ~Q(id=company_parameter.company_id)):
                            response = {"code": 0, "msg": "Customer already exists."}
                        else:
                            company_form.save()
                            mail = company_parameter_form.save(commit=False)
                            mail.gen_mail = gen_mail_
                            mail.ord_rec_mail = ord_rec_mail_
                            mail.ord_exc_gen_mail = ord_exc_gen_mail_
                            mail.ord_exc_rem_mail = ord_exc_rem_mail_
                            mail.ord_comp_mail = ord_comp_mail_
                            mail.mail_from = mail_from_
                            mail.int_exc_from = int_exc_from_
                            mail.int_exc_to = int_exc_to_
                            mail.int_exc_cc = int_exc_cc_
                            mail.save()
                            c_ip = base_views.get_client_ip(request)
                            action = AuditAction.UPDATE
                            new_image = upload_company_logo(company, request)
                            log_views.insert("pws", "company", [company_id], action, request.user.id, c_ip, "Customer details update.")
                            response = {"code": 1, "msg": "Customer details update.", "new_image": new_image}
            else:
                if Util.has_perm("add_new_customers", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                company_form = CompanyForm(request.POST or None)
                company_parameter_form = CompanyParameterForm(request.POST or None)
                if company_form.is_valid():
                    name = company_form.cleaned_data["name"]
                    if not Company.objects.filter(name__iexact=name, is_deleted=False):
                        company_instance = company_form.save()
                        if company_parameter_form.is_valid():
                            company = company_parameter_form.save(commit=False)
                            company.company = company_instance
                            company.gen_mail = gen_mail_
                            company.ord_rec_mail = ord_rec_mail_
                            company.ord_exc_gen_mail = ord_exc_gen_mail_
                            company.ord_exc_rem_mail = ord_exc_rem_mail_
                            company.ord_comp_mail = ord_comp_mail_
                            company.mail_from = mail_from_
                            company.int_exc_from = int_exc_from_
                            company.int_exc_to = int_exc_to_
                            company.int_exc_cc = int_exc_cc_
                            company.save()
                            order_screen = list(OrderScreenParameter.objects.filter(parent_id__isnull=True).values_list("id", flat=True))
                            child_order_screen = OrderScreenParameter.objects.filter(parent_id__code__startswith="cmb").values("id", "code", "parent_id")
                            order_screen_bulk = []
                            for screen_id in order_screen:
                                display_values = []
                                for cs in child_order_screen:
                                    if cs["parent_id"] == screen_id:
                                        display_values.append(cs["id"])
                                display_ids = ",".join(str(x) for x in display_values)
                                order_screen_bulk.append(OrderScreen(company_id=company_instance.id, order_screen_parameter_id=screen_id, is_deleted=True, display_ids=display_ids))
                            OrderScreen.objects.bulk_create(order_screen_bulk)
                            OrderScreen.objects.filter(order_screen_parameter__code="cmb_service", company_id=company_instance.id).update(is_compulsory=True, is_deleted=False)
                            OrderFlowMapping.objects.create(company=company_instance)
                            c_ip = base_views.get_client_ip(request)
                            company = Company.objects.get(id=company_instance.id)
                            new_image = upload_company_logo(company, request)
                            action = AuditAction.INSERT
                            log_views.insert("pws", "company", [company_instance.id], action, request.user.id, c_ip, "Customer has been created.")
                            response = {"code": 1, "msg": "Customer has been created."}
                    else:
                        response = {"code": 0, "msg": "Customer already exists."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def upload_company_logo(company, request):
    new_image = ""
    is_file = request.FILES.get("company_img", False)
    if is_file:
        path = default_storage.save(img_uuid + ".png", ContentFile(request.FILES["company_img"].read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        with open(tmp_file, "rb") as image_file:
            image = Image.open(image_file)
            size = (256, 256)
            image.thumbnail(size, Image.ANTIALIAS)
            background = Image.new("RGBA", size, (255, 255, 255, 0))
            box_width = int((size[0] - image.size[0]) / 2)
            box_height = int((size[1] - image.size[1]) / 2)
            box = (box_width, box_height)
            background.paste(image, box)
            buffer = BytesIO()
            image.save(buffer, format="png")
            encoded_string = base64.b64encode(buffer.getvalue())
            image_input = encoded_string.decode("utf-8")
        os.remove(tmp_file)
        if encoded_string != "":
            company.company_img = new_image = image_input
    company.save()
    return new_image


def delete_customer(request):
    try:
        with transaction.atomic():
            if Util.has_perm("delete_customers", request.user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            else:
                company_ids = request.POST.get("ids")
                company_ids = company_ids.split(",")
                Company.objects.filter(id__in=company_ids).update(is_deleted=True)
                OrderFlowMapping.objects.filter(company_id__in=company_ids).update(is_deleted=True)
                SkillMatrix.objects.filter(company_id__in=company_ids).update(is_deleted=True)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.DELETE
                log_views.insert("pws", "company", company_ids, action, request.user.id, c_ip, "Customer has been deleted.")
                response = {"code": 1, "msg": "Customer has been deleted."}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_customer(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)

        if request.POST.get("customer"):
            query.add(Q(name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("gen_mail"):
            query.add(Q(companyparameter_company__gen_mail__icontains=request.POST["gen_mail"]), query.connector)
        if request.POST.get("ord_rec_mail"):
            query.add(Q(companyparameter_company__ord_rec_mail__icontains=request.POST["ord_rec_mail"]), query.connector)
        if request.POST.get("ord_exc_gen_mail"):
            query.add(Q(companyparameter_company__ord_exc_gen_mail__icontains=request.POST["ord_exc_gen_mail"]), query.connector)
        if request.POST.get("ord_exc_rem_mail"):
            query.add(Q(companyparameter_company__ord_exc_rem_mail__icontains=request.POST["ord_exc_rem_mail"]), query.connector)
        if request.POST.get("ord_comp_mail"):
            query.add(Q(companyparameter_company__ord_comp_mail__icontains=request.POST["ord_comp_mail"]), query.connector)
        if request.POST.get("mail_from"):
            query.add(Q(companyparameter_company__mail_from__icontains=request.POST["mail_from"]), query.connector)
        if request.POST.get("is_active"):
            query.add(Q(is_active=True if request.POST.get("is_active") == "Yes" else False), query.connector)
        if request.POST.get("is_req_files"):
            query.add(Q(companyparameter_company__is_req_files=True if request.POST.get("is_req_files") == "Yes" else False), query.connector)
        if request.POST.get("is_send_attachment"):
            query.add(Q(companyparameter_company__is_send_attachment=True if request.POST.get("is_send_attachment") == "Yes" else False), query.connector)
        if request.POST.get("is_exp_file_attachment"):
            query.add(Q(companyparameter_company__is_exp_file_attachment=True if request.POST.get("is_exp_file_attachment") == "Yes" else False), query.connector)
        query.add(Q(is_deleted=False), query.connector)
        recordsTotal = Company.objects.filter(query).count()
        companies = (
            Company.objects.prefetch_related("companyparameter_set")
            .filter(query)
            .values(
                "id",
                "name",
                "is_active",
            )
            .annotate(
                gen_mail=F("companyparameter_company__gen_mail"),
                ord_rec_mail=F("companyparameter_company__ord_rec_mail"),
                ord_exc_gen_mail=F("companyparameter_company__ord_exc_gen_mail"),
                ord_exc_rem_mail=F("companyparameter_company__ord_exc_rem_mail"),
                ord_comp_mail=F("companyparameter_company__ord_comp_mail"),
                mail_from=F("companyparameter_company__mail_from"),
                int_exc_from=F("companyparameter_company__int_exc_from"),
                int_exc_to=F("companyparameter_company__int_exc_to"),
                int_exc_cc=F("companyparameter_company__int_exc_cc"),
                is_req_files=F("companyparameter_company__is_req_files"),
                is_send_attachment=F("companyparameter_company__is_send_attachment"),
                is_exp_file_attachment=F("companyparameter_company__is_exp_file_attachment"),
                no_of_jobs=F("companyparameter_company__no_of_jobs"),
            )
            .order_by(sort_col)[start : (start + length)]
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        value_change = {False: "No", True: "Yes"}
        for company in companies:
            response["data"].append(
                {
                    "id": company["id"],
                    "name": company["name"],
                    "is_active": value_change[company["is_active"]],
                    "gen_mail": company["gen_mail"],
                    "ord_rec_mail": company["ord_rec_mail"],
                    "ord_exc_gen_mail": company["ord_exc_gen_mail"],
                    "ord_exc_rem_mail": company["ord_exc_rem_mail"],
                    "ord_comp_mail": company["ord_comp_mail"],
                    "mail_from": company["mail_from"],
                    "int_exc_from": company["int_exc_from"],
                    "int_exc_to": company["int_exc_to"],
                    "int_exc_cc": company["int_exc_cc"],
                    "is_req_files": value_change[company["is_req_files"]],
                    "is_send_attachment": value_change[company["is_send_attachment"]],
                    "is_exp_file_attachment": value_change[company["is_exp_file_attachment"]],
                    "no_of_jobs": company["no_of_jobs"] if company["no_of_jobs"] is not None else 0,
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_customer(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_customers", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)

        if request.POST.get("customer"):
            query.add(Q(name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("gen_mail"):
            query.add(Q(companyparameter_company__gen_mail__icontains=request.POST["gen_mail"]), query.connector)
        if request.POST.get("ord_rec_mail"):
            query.add(Q(companyparameter_company__ord_rec_mail__icontains=request.POST["ord_rec_mail"]), query.connector)
        if request.POST.get("ord_exc_gen_mail"):
            query.add(Q(companyparameter_company__ord_exc_gen_mail__icontains=request.POST["ord_exc_gen_mail"]), query.connector)
        if request.POST.get("ord_exc_rem_mail"):
            query.add(Q(companyparameter_company__ord_exc_rem_mail__icontains=request.POST["ord_exc_rem_mail"]), query.connector)
        if request.POST.get("ord_comp_mail"):
            query.add(Q(companyparameter_company__ord_comp_mail__icontains=request.POST["ord_comp_mail"]), query.connector)
        if request.POST.get("mail_from"):
            query.add(Q(companyparameter_company__mail_from__icontains=request.POST["mail_from"]), query.connector)
        if request.POST.get("is_active"):
            query.add(Q(is_active=True if request.POST.get("is_active") == "Yes" else False), query.connector)
        if request.POST.get("is_req_files"):
            query.add(Q(companyparameter_company__is_req_files=True if request.POST.get("is_req_files") == "Yes" else False), query.connector)
        if request.POST.get("is_send_attachment"):
            query.add(Q(companyparameter_company__is_send_attachment=True if request.POST.get("is_send_attachment") == "Yes" else False), query.connector)
        if request.POST.get("is_exp_file_attachment"):
            query.add(Q(companyparameter_company__is_exp_file_attachment=True if request.POST.get("is_exp_file_attachment") == "Yes" else False), query.connector)
        query.add(Q(is_deleted=False), query.connector)
        companies = (
            Company.objects.prefetch_related("companyparameter_set")
            .filter(query)
            .values(
                "name",
                "is_active",
            )
            .annotate(
                gen_mail=F("companyparameter_company__gen_mail"),
                ord_rec_mail=F("companyparameter_company__ord_rec_mail"),
                ord_exc_gen_mail=F("companyparameter_company__ord_exc_gen_mail"),
                ord_exc_rem_mail=F("companyparameter_company__ord_exc_rem_mail"),
                ord_comp_mail=F("companyparameter_company__ord_comp_mail"),
                is_req_files=F("companyparameter_company__is_req_files"),
                is_send_attachment=F("companyparameter_company__is_send_attachment"),
                is_exp_file_attachment=F("companyparameter_company__is_exp_file_attachment"),
                no_of_jobs=F("companyparameter_company__no_of_jobs"),
                mail_from=F("companyparameter_company__mail_from"),
                int_exc_from=F("companyparameter_company__int_exc_from"),
                int_exc_to=F("companyparameter_company__int_exc_to"),
                int_exc_cc=F("companyparameter_company__int_exc_cc"),
            )
            .order_by(order_by)[start : (start + length)]
        )
        query_result = []
        value_change = {False: "No", True: "Yes"}
        for company in companies:
            query_result.append(
                {
                    "name": company["name"],
                    "gen_mail": company["gen_mail"],
                    "ord_rec_mail": company["ord_rec_mail"],
                    "ord_exc_gen_mail": company["ord_exc_gen_mail"],
                    "ord_exc_rem_mail": company["ord_exc_rem_mail"],
                    "ord_comp_mail": company["ord_comp_mail"],
                    "mail_from": company["mail_from"],
                    "int_exc_from": company["int_exc_from"],
                    "int_exc_to": company["int_exc_to"],
                    "int_exc_cc": company["int_exc_cc"],
                    "no_of_jobs": company["no_of_jobs"] if company["no_of_jobs"] is not None else "0",
                    "is_active": value_change[company["is_active"]],
                    "is_req_files": value_change[company["is_req_files"]],
                    "is_send_attachment": value_change[company["is_send_attachment"]],
                    "is_exp_file_attachment": value_change[company["is_exp_file_attachment"]],
                }
            )
        headers = [
            {"title": "Customer name"},
            {"title": "General mail"},
            {"title": "Order receive mail"},
            {"title": "Exception mail to leader"},
            {"title": "Exception mail to customer"},
            {"title": "Order completion mail"},
            {"title": "Mail from"},
            {"title": "Internal exception from"},
            {"title": "Internal exception to"},
            {"title": "Internal exception cc"},
            {"title": "Number of jobs"},
            {"title": "Active"},
            {"title": "File required"},
            {"title": "Send prepared data in attachment"},
            {"title": "Send Exception file in Attachment"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "Customers.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order_process_flow(request):
    try:
        return render(request, "pws/order_process_flow.html")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order_flow(request, id):
    try:
        services = Service.objects.values("id", "name")
        processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"])).values("id", "name", "sequence", "code").order_by("sequence")
        applied_services = OrderFlowMapping.objects.filter(company__id=id, is_deleted=False).values("service_id", "process_ids")
        process_item = []
        service_item = []
        for service_process in applied_services:
            service_item.append(service_process["service_id"])

            if service_process["process_ids"] == "" or service_process["process_ids"] is None:
                process_item.append(list())
            else:
                process_item.append(list(map(int, service_process["process_ids"].split(","))))
        services_processes = dict(zip(service_item, process_item))
        return render(request, "pws/order_flow.html", {"services": services, "processes": processes, "services_processes": services_processes})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order_flow_search(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        if request.POST.get("company__name"):
            query.add(Q(company__name__icontains=request.POST["company__name"]), query.connector)
        if request.POST.get("service__name"):
            query.add(Q(service__name__icontains=request.POST["service__name"]), query.connector)

        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)
        query.add(Q(is_deleted=False), query.connector)
        recordTotal = OrderFlowMapping.objects.filter(query).values("company__id").distinct().count()
        service_process_orderFlow = (
            OrderFlowMapping.objects.filter(query)
            .values("company__name")
            .annotate(
                id=F("company__id"),
                name=F(
                    "company__name",
                ),
            )
            .distinct()
            .order_by(sort_col)[start : (start + length)]
        )
        company_ids = [company_id["id"] for company_id in service_process_orderFlow]
        services = OrderFlowMapping.objects.filter(company__id__in=company_ids, is_deleted=False).values("company__id", "service__name")
        service_names = {}
        for service in services:
            if service["company__id"] in service_names:
                if service_names[service["company__id"]] != "":
                    service_names[service["company__id"]] += ", " + service["service__name"] if service["service__name"] is not None else ""
                else:
                    service_names[service["company__id"]] += service["service__name"] if service["service__name"] is not None else ""
            else:
                service_names[service["company__id"]] = service["service__name"] if service["service__name"] is not None else ""
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordTotal,
            "recordsFiltered": recordTotal,
            "data": [],
        }

        for order_flow in service_process_orderFlow:
            response["data"].append(
                {
                    "id": order_flow["id"],
                    "company__name": order_flow["company__name"],
                    "service__name": service_names[order_flow["id"]] if order_flow["id"] in service_names else "",
                    "sort_col": sort_col,
                    "recordsTotal": recordTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order_flow_save(request):
    try:
        with transaction.atomic():
            company_id = request.POST.get("company_id")
            services_id = request.POST.getlist("services")
            services_ids = list(map(int, services_id))
            processes_ids = []
            for service_id in services_ids:
                processes_id = request.POST.getlist("processes" + str(service_id))
                processes_string = ",".join(map(str, processes_id))
                processes_ids.append(processes_string)
            service_process = dict(zip(services_ids, processes_ids))

            client_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE

            services_old = OrderFlowMapping.objects.filter(company__id=company_id).values("service_id")
            service_id_old = [service["service_id"] for service in services_old]
            remain_service = [service for service in service_id_old + services_ids if service not in service_id_old or service not in services_ids]
            OrderFlowMapping.objects.filter(company_id=company_id, service_id__in=remain_service).update(is_deleted=True)
            order_screen_services = str(services_id).replace("[", "").replace("'", "").replace("]", "")
            for service, process in service_process.items():
                if process == "":
                    process = None
                if not OrderFlowMapping.objects.filter(company_id=company_id, service_id=service):
                    OrderFlowMapping.objects.create(company_id=company_id, service_id=service, process_ids=process)
                else:
                    OrderFlowMapping.objects.filter(company_id=company_id, service_id=service).update(process_ids=process, is_deleted=False)
                    OrderScreen.objects.filter(order_screen_parameter__code="cmb_service", company_id=company_id).update(display_ids=order_screen_services)
            if len(service_process) == 0 :
                OrderFlowMapping.objects.filter(company_id=company_id).update(process_ids=None)
            all_service = OrderFlowMapping.objects.filter(~Q(service_id=None), company__id=company_id, is_deleted=False).values("service_id")
            service_ids = [str(x["service_id"]) for x in all_service]
            service_id = ",".join(service_ids)
            OrderScreen.objects.filter(order_screen_parameter__code="cmb_service", company_id=company_id).update(display_ids=service_id)
            log_views.insert(
                "pws",
                "OrderFlowMapping",
                [company_id],
                action,
                request.user.id,
                client_ip,
                "Company order flow updated",
            )
            response = {"code": 1, "msg": "Order flow Updated."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def place_order(request):
    return render(request, "pws/place_order.html")


@check_view_permission([{"order_allocations": "pws_order_allocation"}])
def order_allocations(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = [
            "reserve_order_allocation",
            "release_order_allocation",
            "can_auto_assignment",
            "can_define_auto_assignment",
            "add_skill_matrix_order_allocation",
            "reserve_multiple_order_allocation",
            "manage_auto_order_allocation",
            "can_export_order_allocation"
        ]
        permissions = Util.get_permission_role(user, perms)
        u_id = Operator.objects.get(user__username=request.user)
        manage_auto_allocation = ManageAutoAllocation.objects.values("id", "stop_start_time", "stop_end_time")
        return render(request, "pws/order_allocations.html", {"manage_auto_allocation" : manage_auto_allocation, "u_id": u_id, "permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"user_efficiencies": "pws_user_efficiency"}])
def user_efficiencies(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["add_new_user_efficiency", "edit_user_efficiency", "can_export_user_efficiency"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/user_efficiencies.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_order": "orders"}])
def orders(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = [
            "can_add_new_file",
            "view_file_history",
            "can_add_nc",
            "can_add_remark",
            "can_view_files",
            "can_change_status",
            "can_reserve",
            "can_release",
            "can_send_to_next",
            "can_back_to_previous",
            "can_send_to_fqc",
            "can_register_exception",
            "reserve_multiple_report_orders",
            "can_export_orders",
        ]
        permissions = Util.get_permission_role(user, perms)
        exception_problems_id = PreDefineExceptionProblem.objects.filter(is_problem=True, is_deleted=False).values("code", "id").first()
        con = {"exception_problems_id": exception_problems_id, "permissions": json.dumps(permissions)}
        return render(request, "pws/reports/orders.html", con)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_work_details": "reports_work_details"}])
def work_details_reports(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_work_details_report"]
        permissions = Util.get_permission_role(user, perms)
        planet_engineer = "No"
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("id", "operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    planet_engineer = "Yes"
        context = {"planet_engineer": planet_engineer, "operator_id": operator_id["id"], "permissions": json.dumps(permissions)}
        return render(request, "pws/reports/work_details_reports.html", context)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_work_details_reports(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        action_query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "layer":
            sort_col = "layer_column"
        if sort_col == "-layer":
            sort_col = "-layer_column"
        if request.POST.get("company_id"):
            query.add(Q(order__company_id=request.POST["company_id"]), query.connector)
        if request.POST.get("operator_id"):
            query.add(Q(operator_id=request.POST["operator_id"]), query.connector)
        if request.POST.get("start_date__date") and request.POST.get("end_date__date") is not None:
            action_query.add(
                Q(
                    action_on__range=[
                        datetime.datetime.strptime(str(request.POST["start_date__date"]) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST["end_date__date"]) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                action_query.connector,
            )
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(request.POST["start_date__date"]) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST["end_date__date"]) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        action_date_record = []
        if "load_data" in request.POST:
            action_query.add(Q(content_type_id__model="order"), action_query.connector)
            action_date_record = Auditlog.objects.filter(action_query).values(
                "object_id",
                "action_on",
            )
        action_ids = [x["object_id"] for x in action_date_record]
        query.add(Q(order_id__in=action_ids), query.connector)
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    query.add(Q(operator__user__id=request_user_id["id"]), query.connector)
        recordsTotal = UserEfficiencyLog.objects.filter(query).count()
        records = (
            UserEfficiencyLog.objects.filter(query)
            .values("id", "company__id", "prep_time", "order_from_status", "order_to_status", "layer_point", "total_work_efficiency", "extra_point", "preparation")
            .annotate(
                order_id=F("order_id"),
                order_next_status=F("order__order_next_status"),
                remarks=F("order__remarks"),
                layer=F("order__layer"),
                order_date=F("order__order_date"),
                order_number=F("order__order_number"),
                operator=F("operator__user__username"),
                customer=F("order__company__name"),
                service=F("order__service__name"),
                action_date=F("created_on"),
                customer_order_nr=F("order__customer_order_nr"),
                delivery_date=F("order__delivery_date"),
                sub_group=F("operator__sub_group_of_operator__sub_group_name"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            )
            .order_by(sort_col)[start : (start + length)]
        )
        company_ids = [record["company__id"] for record in records]
        orders_ids = [record["order_id"] for record in records]
        nc_count = NonConformity.objects.filter(company__in=company_ids, order_id__in=orders_ids).values("order_id").annotate(nc_count=Count("id"))
        nc_counts = Util.get_dict_from_quryset("order_id", "nc_count", nc_count)
        layers_code = [order_["layer"] for order_ in records]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        remarks_list = [order_["id"] for order_ in records]
        remarks = (
            Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list, comment_type__code="Efficeiency_Remarks")
            .values("entity_id", "remark").order_by("created_on")
        )
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        for data in records:
            time_taken = None
            if data["prep_time"] is not None:
                pre = int(data["prep_time"])
                hour = pre // 3600
                pre %= 3600
                minutes = pre // 60
                pre %= 60
                preparation_time = str(hour) + ":" + str(minutes).zfill(2)
                time_taken = int(data["prep_time"])
            response["data"].append(
                {
                    "id": data["id"],
                    "order_id": data["order_id"],
                    "order_number": data["order_number"],
                    "service": data["service"],
                    "layer": layers[data["layer"]] if data["layer"] in layers else None,
                    "remarks": "<span>" + str(remarks_disc[data["id"]]) + "<span>" if data["id"] in remarks_disc else "",
                    "order_date": Util.get_local_time(data["order_date"], False),
                    "operator": data["operator"],
                    "customer": data["customer"],
                    "action_date": Util.get_local_time(data["action_date"], True),
                    "order_from_status": dict(order_status)[data["order_from_status"]] if data["order_from_status"] in dict(order_status) else " ",
                    "order_to_status": dict(order_status)[data["order_to_status"]] if data["order_to_status"] in dict(order_status) else "-",
                    "company__id": dict(nc_counts)[data["order_id"]] if data["order_id"] in dict(nc_counts) else "0",
                    "prep_time": preparation_time if time_taken is not None else "",
                    "layer_point": data["layer_point"],
                    "customer_order_nr": data["customer_order_nr"],
                    "preparation": data["preparation"],
                    "sub_group": data["sub_group"],
                    "delivery_date": Util.get_local_time(data["delivery_date"], True),
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def work_details_reports_export(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_work_details_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        company_id = request.POST.get("company_id")
        operator_id = request.POST.get("operator_id")
        from_date = request.POST.get("from")
        to_date = request.POST.get("to")
        query = Q()
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        action_query = Q()
        if company_id:
            query.add(Q(order__company_id=company_id), query.connector)
        if operator_id:
            query.add(Q(operator_id=operator_id), query.connector)
        if from_date and to_date is not None:
            action_query.add(
                Q(
                    action_on__range=[
                        datetime.datetime.strptime(str(from_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(to_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                action_query.connector,
            )
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(from_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(to_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        action_date_record = []
        action_query.add(Q(content_type_id__model="order"), action_query.connector)
        action_date_record = Auditlog.objects.filter(action_query).values(
            "object_id",
            "action_on",
        )
        action_ids = [x["object_id"] for x in action_date_record]
        query.add(Q(order_id__in=action_ids), query.connector)
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    query.add(Q(operator__user__id=request_user_id["id"]), query.connector)
        records = (
            UserEfficiencyLog.objects.filter(query)
            .select_related("order_set")
            .values("id", "order_from_status", "prep_time", "created_on", "layer_point", "extra_point", "total_work_efficiency", "preparation")
            .annotate(
                order_id=F("order_id"),
                order_number=F("order__order_number"),
                customer=F("order__company__name"),
                order_date=F("order__order_date"),
                service=F("order__service__name"),
                layer=F("order__layer"),
                order_next_status=F("order_to_status"),
                operator=F("operator__user__username"),
                remarks=F("order__remarks"),
                customer_order_nr=F("order__customer_order_nr"),
                delivery_date=F("order__delivery_date"),
                sub_group=F("operator__sub_group_of_operator__sub_group_name"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )
        remarks_list = [order_["id"] for order_ in records]
        remarks = (
            Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list, comment_type__code="Efficeiency_Remarks")
            .values("entity_id", "remark").order_by("created_on")
        )
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        layers_code = [order_["layer"] for order_ in records]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)
        query_result = []
        for data in records:
            time_taken = None
            if data["prep_time"] is not None:
                pre = int(data["prep_time"])
                hour = pre // 3600
                pre %= 3600
                minutes = pre // 60
                pre %= 60
                preparation_time = str(hour) + ":" + str(minutes).zfill(2)
                time_taken = int(data["prep_time"])
            query_result.append(
                {
                    "order_number": data["order_number"],
                    "customer_order_nr": data["customer_order_nr"],
                    "customer": data["customer"],
                    "order_date": Util.get_local_time(data["order_date"], False),
                    "service": data["service"],
                    "layer": layers[data["layer"]] if data["layer"] in layers else None,
                    "worked_section": dict(order_status)[data["order_from_status"]] if data["order_from_status"] in dict(order_status) else " ",
                    "move_to_section": dict(order_status)[data["order_next_status"]] if data["order_next_status"] in dict(order_status) else " ",
                    "preparation": data["preparation"],
                    "operator": data["operator"],
                    "sub_group": data["sub_group"],
                    "action_date": Util.get_local_time(data["created_on"], True),
                    "delivery_date": Util.get_local_time(data["delivery_date"], True),
                    "remarks": BeautifulSoup(remarks_disc[data["id"]], features="html5lib").get_text() if data["id"] in remarks_disc else "",
                    "prep_time": preparation_time if time_taken is not None else "",
                    "layer_point": data["layer_point"],
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Customer"},
            {"title": "Order date"},
            {"title": "Service"},
            {"title": "Layers"},
            {"title": "Worked section"},
            {"title": "Move to section"},
            {"title": "Preparation"},
            {"title": "Operator name"},
            {"title": "Sub group"},
            {"title": "Action date"},
            {"title": "Delivery date"},
            {"title": "Remarks"},
            {"title": "Time taken"},
            {"title": "User Efficiency points"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "work_details_reports.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_work_summary": "reports_work_summary"}])
def work_summary_reports(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_work_summary_report"]
        permissions = Util.get_permission_role(user, perms)
        planet_engineer = "No"
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("id", "operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    planet_engineer = "Yes"
        context = {"planet_engineer": planet_engineer, "operator_id": operator_id["id"], "permissions": json.dumps(permissions)}
        return render(request, "pws/reports/work_summary_reports.html", context)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_work_summary_reports(request):
    try:
        if "load_data" in request.POST:
            request.POST = Util.get_post_data(request)
            query = Q()
            query1 = Q()
            start = int(request.POST.get("start"))
            length = int(request.POST.get("length"))
            sort_col = Util.get_sort_column(request.POST)
            if request.POST.get("company_id"):
                query.add(Q(order__company_id=request.POST["company_id"]), query.connector)
            if request.POST.get("operator_id"):
                query.add(Q(operator_id=request.POST["operator_id"]), query.connector)
            if request.POST.get("start_date__date") and request.POST.get("end_date__date") is not None:
                query.add(
                    Q(
                        created_on__range=[
                            datetime.datetime.strptime(str(request.POST["start_date__date"]) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(request.POST["end_date__date"]) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query.connector,
                )
                query1.add(
                    Q(
                        created_on__range=[
                            datetime.datetime.strptime(str(request.POST["start_date__date"]) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(request.POST["end_date__date"]) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query1.connector,
                )
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
            operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
            if operator_id:
                if operator_id["operator_type"]:
                    if operator_id["operator_type"] == "PLANET_ENG":
                        query.add(Q(operator__user__id=request_user_id["id"]), query.connector)
            recordsTotal = (
                UserEfficiencyLog.objects.filter(query)
                .values("company__name", "created_on__date", "operator__user__username")
                .annotate(
                    layer_point=Sum((F('layer_point') / 450.0) * 100, output_field=FloatField()),
                    order_count=Count("order_id", distinct=True),
                )
            ).count()
            records = (
                UserEfficiencyLog.objects.filter(query)
                .values("company__name", "created_on__date", "operator__user__username")
                .annotate(
                    layer_point=Sum((F('layer_point') / 450.0) * 100, output_field=FloatField()),
                    order_count=Count("order_id", distinct=True),
                    sub_group=F("operator__sub_group_of_operator__sub_group_name"),
                )
                .order_by(sort_col)[start : (start + length)]
            )

            nc_count = (
                NonConformity.objects.filter(query1)
                .prefetch_related("nonconformitydetail_set")
                .values("company__name", "nonconformitydetail__operator__user__username", "created_on__date")
                .annotate(nc_count=Count("id"))
            )
            nc_count_sum = {}
            for nc_count_ in nc_count:
                nc_count_sum[nc_count_["created_on__date"], nc_count_["company__name"], nc_count_["nonconformitydetail__operator__user__username"]] = nc_count_["nc_count"]
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }
            for data in records:
                response["data"].append(
                    {
                        # "id": data["id"],
                        "created_on__date": datetime.datetime.strptime(str(data["created_on__date"]).strip(), "%Y-%m-%d").strftime("%d-%m-%Y"),
                        "company__name": data["company__name"],
                        "operator__user__username": data["operator__user__username"],
                        "layer_point": Util.decimal_to_str(request, data["layer_point"]),
                        "order_count": data["order_count"],
                        "sub_group": data["sub_group"],
                        "company__id": nc_count_sum[data["created_on__date"], data["company__name"], data["operator__user__username"]]
                        if (data["created_on__date"], data["company__name"], data["operator__user__username"]) in nc_count_sum
                        else "0",
                        "sort_col": sort_col,
                        "recordsTotal": recordsTotal,
                    }
                )
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def work_summary_reports_export(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_work_summary_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        query1 = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        company_id = request.POST.get("company_id")
        operator_id = request.POST.get("operator_id")
        from_date = request.POST.get("from")
        to_date = request.POST.get("to")
        if from_date and to_date is not None:
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(from_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(to_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
            query1.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(from_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(to_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query1.connector,
            )
        if company_id:
            query.add(Q(order__company_id=company_id), query.connector)
        if operator_id:
            query.add(Q(operator_id=operator_id), query1.connector)
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    query.add(Q(operator__user__id=request_user_id["id"]), query.connector)
        records = (
            UserEfficiencyLog.objects.filter(query)
            .values("company__name", "created_on__date", "operator__user__username")
            .annotate(
                layer_point=Sum((F('layer_point') / 450.0) * 100, output_field=FloatField()),
                order_count=Count("order_id", distinct=True),
                sub_group=F("operator__sub_group_of_operator__sub_group_name"),
            ).order_by(order_by)[start : (start + length)]
        )
        nc_count = (
            NonConformity.objects.filter(query1)
            .prefetch_related("nonconformitydetail_set")
            .values("company__name", "nonconformitydetail__operator__user__username", "created_on__date")
            .annotate(nc_count=Count("id"))
        )
        nc_count_sum = {}
        for nc_count_ in nc_count:
            nc_count_sum[nc_count_["created_on__date"], nc_count_["company__name"], nc_count_["nonconformitydetail__operator__user__username"]] = nc_count_["nc_count"]
        query_result = []
        for data in records:
            query_result.append(
                {
                    "created_on": datetime.datetime.strptime(str(data["created_on__date"]).strip(), "%Y-%m-%d").strftime("%d-%m-%Y"),
                    "operator": data["operator__user__username"],
                    "sub_group": data["sub_group"],
                    "customer": data["company__name"],
                    "layer_point": Util.decimal_to_str(request, data["layer_point"]),
                    "order_count": data["order_count"],
                    "company__id": nc_count_sum[data["created_on__date"], data["company__name"], data["operator__user__username"]]
                    if (data["created_on__date"], data["company__name"], data["operator__user__username"]) in nc_count_sum
                    else "0",
                }
            )
        headers = [
            {"title": "Date"},
            {"title": "Operator name"},
            {"title": "Sub group"},
            {"title": "Customer"},
            {"title": "Efficiency point"},
            {"title": "order counts"},
            {"title": "NC count"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "work_summary_reports.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"customer_user": "pws_customer_users"}])
def customer_users_view(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["add_new_customer_users", "edit_customer_users", "delete_customer_users", "can_export_customer_users"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/customer_users.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def customer_user(request, user_id):
    user = None
    company_user = None
    user_role = None
    if user_id != "0":
        user = User.objects.get(id=user_id)
        company_user = CompanyUser.objects.get(user_id=user.id)
        user_role = UserGroup.objects.get(user_id=user.id)
    return render(request, "pws/customer_user.html", {"user_role": user_role, "user": user, "comp_user": company_user})


def save_customer_user(request):
    try:
        with transaction.atomic():
            user_id = request.POST.get("user_id")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")
            is_active = request.POST.get("is_active")
            company = request.POST.get("company")
            group = request.POST.get("group")
            ip_restriction = "ip_restriction" in request.POST

            if is_active is None:
                is_active = False
            else:
                is_active = True

            if user_id != "0":
                if Util.has_perm("edit_customer_users", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                else:
                    if User.objects.filter(Q(username__iexact=username), ~Q(id=user_id)):
                        response = {"code": 0, "msg": "Customer user already exist."}
                    else:
                        user = User.objects.filter(id=user_id).update(first_name=first_name, last_name=last_name, username=username, email=email, is_active=is_active)
                        UserGroup.objects.filter(user_id=user_id).update(group_id=group)
                        CompanyUser.objects.filter(user_id=user_id).update(company_id=company)
                        c_ip = base_views.get_client_ip(request)
                        action = AuditAction.UPDATE
                        log_views.insert("pws", "companyuser", [user_id], action, request.user.id, c_ip, "Customer-user details update.")
                        response = {"code": 1, "msg": "Customer-user details update."}
            else:
                if Util.has_perm("add_new_customer_users", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                else:
                    if not User.objects.filter(username__iexact=username):
                        password = make_password(password)
                        user = User.objects.create(first_name=first_name, last_name=last_name, username=username, password=password, email=email, is_active=is_active)
                        UserProfile.objects.create(user_id=user.id, user_type=1, partner_id=0, color_scheme=settings.DEFAULT_PORTAL_COLOR_SCHEME, ip_restriction=ip_restriction)
                        UserGroup.objects.create(user_id=user.id, group_id=group)
                        CompanyUser.objects.create(user_id=user.id, company_id=company)
                        c_ip = base_views.get_client_ip(request)
                        action = AuditAction.INSERT
                        log_views.insert("pws", "companyuser", [user.id], action, request.user.id, c_ip, "Customer-user has been created.")
                        response = {"code": 1, "msg": "Customer-user has been created."}
                    else:
                        response = {"code": 0, "msg": "Customer user already exist."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def customer_user_change_password(request):
    try:
        with transaction.atomic():
            user_id = request.POST.get("id")
            user = User.objects.get(id=user_id)
            user.password = make_password(str(request.POST["password"]).strip())
            user.save()
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            log_views.insert("pws", "companyuser", [user_id], action, request.user.id, c_ip, "Password updated.")
            response = {"code": 1, "msg": "Password updated."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_customer_user(request):
    try:
        with transaction.atomic():
            if Util.has_perm("delete_customer_users", request.user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            else:
                user_ids = request.POST.get("ids")
                user_ids = user_ids.split(",")
                for id in user_ids:
                    user = User.objects.filter(id=id).values("username", "id").first()
                    username = user["username"] + "_" + str(user["id"]) + "_" + "dlt"
                    User.objects.filter(id=id).update(username=username)
                CompanyUser.objects.filter(user_id__in=user_ids).update(is_deleted=True)
                UserProfile.objects.filter(user_id__in=user_ids).update(is_deleted=True)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.DELETE
                log_views.insert("pws", "companyuser", user_ids, action, request.user.id, c_ip, "Customer-user has been deleted.")
                response = {"code": 1, "msg": "Customer-user has been deleted."}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_customer_user(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if request.POST.get("username"):
            query.add(Q(user__username__icontains=request.POST["username"]), query.connector)
        if request.POST.get("first_name"):
            query.add(Q(user__first_name__icontains=request.POST["first_name"]), query.connector)
        if request.POST.get("last_name"):
            query.add(Q(user__last_name__icontains=request.POST["last_name"]), query.connector)
        if request.POST.get("customer_name"):
            query.add(Q(company__name__icontains=request.POST["customer_name"]), query.connector)
        if request.POST.get("email"):
            query.add(Q(user__email__icontains=request.POST["email"]), query.connector)
        if request.POST.get("registration_date"):
            query.add(
                Q(
                    user__date_joined__range=[
                        datetime.datetime.strptime(str(request.POST.get("registration_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("registration_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        is_active = request.POST.get("is_active")
        is_active = True if is_active == "Yes" else False
        if request.POST.get("is_active"):
            query.add(Q(user__is_active=is_active), query.connector)
        query.add(Q(is_deleted=False), query.connector)
        recordsTotal = CompanyUser.objects.filter(query).count()
        company_users = (
            CompanyUser.objects.filter(query)
            .values("user__id", "company__name")
            .annotate(
                username=F("user__username"),
                first_name=F("user__first_name"),
                last_name=F("user__last_name"),
                email=F("user__email"),
                is_active=F("user__is_active"),
                created_on=F("user__date_joined"),
            )
            .order_by(sort_col)[start : (start + length)]
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        user_ids = [user["user__id"] for user in company_users]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")

        role_data = {}
        for user_role in user_roles:
            role_name = user_role["group__name"]
            if user_role["user_id"] in role_data:
                role_name = role_name + ", " + role_data[user_role["user_id"]]
            role_data[user_role["user_id"]] = role_name

        for user in company_users:
            response["data"].append(
                {
                    "id": user["user__id"],
                    "username": user["username"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "company__name": user["company__name"],
                    "is_active": "Yes" if user["is_active"] else "No",
                    "user_role": role_data[user["user__id"]] if user["user__id"] in role_data else "",
                    "email": user["email"],
                    "created_on": Util.get_local_time(user["created_on"], True),
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_customer_user(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_customer_users", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(user__id__in=selected_ids), query.connector)
        if request.POST.get("username"):
            query.add(Q(user__username__icontains=request.POST["username"]), query.connector)
        if request.POST.get("first_name"):
            query.add(Q(user__first_name__icontains=request.POST["first_name"]), query.connector)
        if request.POST.get("last_name"):
            query.add(Q(user__last_name__icontains=request.POST["last_name"]), query.connector)
        if request.POST.get("customer_name"):
            query.add(Q(company__name__icontains=request.POST["customer_name"]), query.connector)
        if request.POST.get("email"):
            query.add(Q(user__email__icontains=request.POST["email"]), query.connector)
        if request.POST.get("registration_date"):
            query.add(
                Q(
                    user__date_joined__range=[
                        datetime.datetime.strptime(str(request.POST.get("registration_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("registration_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        is_active = request.POST.get("is_active")
        is_active = True if is_active == "Yes" else False
        if request.POST.get("is_active"):
            query.add(Q(user__is_active=is_active), query.connector)

        query.add(Q(is_deleted=False), query.connector)
        company_users = (
            CompanyUser.objects.filter(query)
            .values("user__id", "company__name")
            .annotate(
                username=F("user__username"),
                first_name=F("user__first_name"),
                last_name=F("user__last_name"),
                email=F("user__email"),
                is_active=F("user__is_active"),
                created_on=F("user__date_joined"),
            ).order_by(order_by)[start : (start + length)]
        )
        query_result = []

        user_ids = [user["user__id"] for user in company_users]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")

        role_data = {}
        for user_role in user_roles:
            role_name = user_role["group__name"]
            if user_role["user_id"] in role_data:
                role_name = role_name + ", " + role_data[user_role["user_id"]]
            role_data[user_role["user_id"]] = role_name

        for user in company_users:
            query_result.append(
                {
                    "username": user["username"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "company__name": user["company__name"],
                    "is_active": "Yes" if user["is_active"] else "No",
                    "email": user["email"],
                    "user_role": role_data[user["user__id"]] if user["user__id"] in role_data else "",
                    "registration_date": Util.get_local_time(user["created_on"], True),
                }
            )
        headers = [
            {"title": "Username"},
            {"title": "First name"},
            {"title": "Last name"},
            {"title": "Company"},
            {"title": "Active"},
            {"title": "Email id"},
            {"title": "Role"},
            {"title": "Created on"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "Customer-users.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def set_order_screen(request, company_id):
    try:
        query = Q()
        query.add(Q(orderscreen__company_id=company_id), query.connector)
        query.add(Q(parent_id__isnull=True), query.connector)

        order_screens = (
            OrderScreenParameter.objects.filter(query)
            .prefetch_related("orderscreen")
            .values(
                "id",
                "code",
                "name",
                "orderscreen__default_value",
                "orderscreen__id",
                "orderscreen__display_ids",
                "orderscreen__is_compulsory",
                "orderscreen__is_deleted",
            )
            .order_by("sequence")
        )
        parameter_name = {"Service": "Service type", "Board Name": "PCB Name"}
        is_compulsory = {"cmb_service": True}
        is_selected = {"cmb_service": False}
        order_screen_cmb_service = Service.objects.values("code", "name")
        order_screen_cmb_service = Util.get_dict_from_quryset("code", "name", order_screen_cmb_service)
        order_screen_parameter = OrderScreenParameter.objects.values("code", "name")
        order_screen_parameter = Util.get_dict_from_quryset("code", "name", order_screen_parameter)
        order_screen_params = []
        for screen in order_screens:
            order_screen_params.append(
                {
                    "id": screen["id"],
                    "code": screen["code"],
                    "name": parameter_name[screen["name"]] if screen["name"] in parameter_name else screen["name"],
                    "orderscreen__default_value": screen["orderscreen__default_value"],
                    "default_display_value": order_screen_cmb_service[screen["orderscreen__default_value"]]
                    if screen["orderscreen__default_value"] in order_screen_cmb_service
                    else screen["orderscreen__default_value"]
                    if screen["code"] == "cmb_service"
                    else order_screen_parameter[screen["orderscreen__default_value"]]
                    if screen["orderscreen__default_value"] in order_screen_parameter
                    else screen["orderscreen__default_value"],
                    "orderscreen__id": screen["orderscreen__id"],
                    "orderscreen__display_ids": screen["orderscreen__display_ids"],
                    "orderscreen__is_compulsory": is_compulsory[screen["code"]] if screen["code"] in is_compulsory else screen["orderscreen__is_compulsory"],
                    "orderscreen__is_deleted": is_selected[screen["code"]] if screen["code"] in is_selected else screen["orderscreen__is_deleted"],
                }
            )
        return render(request, "pws/set_order_screen.html", {"order_screen": order_screen_params, "company_id": company_id})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def set_order_screen_copy(request, company_id):
    try:
        select_customer = request.POST.get("select_customer")
        query = Q()
        query.add(Q(orderscreen__company_id=company_id), query.connector)
        query.add(Q(parent_id__isnull=True), query.connector)
        order_screens = (
            OrderScreenParameter.objects.filter(query)
            .prefetch_related("orderscreen")
            .values(
                "id",
                "code",
                "name",
                "orderscreen__default_value",
                "orderscreen__id",
                "orderscreen__display_ids",
                "orderscreen__is_compulsory",
                "orderscreen__is_deleted",
            )
            .order_by("sequence")
        )
        parameter_name = {"Service": "Service type", "Board Name": "PCB Name"}
        is_compulsory = {"cmb_service": True}
        is_selected = {"cmb_service": False}
        order_screen_cmb_service = Service.objects.values("code", "name")
        order_screen_cmb_service = Util.get_dict_from_quryset("code", "name", order_screen_cmb_service)
        order_screen_parameter = OrderScreenParameter.objects.values("code", "name")
        order_screen_parameter = Util.get_dict_from_quryset("code", "name", order_screen_parameter)
        order_screen_params = []
        for screen in order_screens:
            order_screen_params.append(
                {
                    "id": screen["id"],
                    "code": screen["code"],
                    "name": parameter_name[screen["name"]] if screen["name"] in parameter_name else screen["name"],
                    "orderscreen__default_value": screen["orderscreen__default_value"],
                    "default_display_value": order_screen_cmb_service[screen["orderscreen__default_value"]]
                    if screen["orderscreen__default_value"] in order_screen_cmb_service
                    else screen["orderscreen__default_value"]
                    if screen["code"] == "cmb_service"
                    else order_screen_parameter[screen["orderscreen__default_value"]]
                    if screen["orderscreen__default_value"] in order_screen_parameter
                    else screen["orderscreen__default_value"],
                    "orderscreen__id": screen["orderscreen__id"],
                    "orderscreen__display_ids": screen["orderscreen__display_ids"],
                    "orderscreen__is_compulsory": is_compulsory[screen["code"]] if screen["code"] in is_compulsory else screen["orderscreen__is_compulsory"],
                    "orderscreen__is_deleted": is_selected[screen["code"]] if screen["code"] in is_selected else screen["orderscreen__is_deleted"],
                }
            )
        return render(request, "pws/set_order_screen.html", {"order_screen": order_screen_params, "company_id": select_customer})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_order_screen_master(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_set_order_screen", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            selected_params = []
            is_compulsory_params = []
            company_id = request.POST.get("company_id")
            select_customer = request.POST.get("select_customer")
            child_data = json.loads(request.POST.get("child_data"))
            if request.POST.get("select"):
                selected_params = request.POST.getlist("select")
                selected_params.append("cmb_service")
            if request.POST.get("is_compulsory"):
                is_compulsory_params = request.POST.getlist("is_compulsory")
                is_compulsory_params.append("cmb_service")
            company_params = list(OrderScreen.objects.filter(company_id=company_id).values_list("order_screen_parameter__code", flat=True))
            remove_params = [x for x in company_params if x not in selected_params]
            selected_params = [x for x in selected_params if x not in remove_params]
            is_not_compulsory_params = [x for x in company_params if x not in is_compulsory_params]

            if len(is_compulsory_params) > 0:
                OrderScreen.objects.filter(order_screen_parameter__code__in=is_compulsory_params, company_id=company_id).update(is_compulsory=True)
            if len(is_not_compulsory_params) > 0:
                OrderScreen.objects.filter(order_screen_parameter__code__in=is_not_compulsory_params, company_id=company_id).update(is_compulsory=False)
            if len(remove_params) > 0:
                OrderScreen.objects.filter(order_screen_parameter__code__in=remove_params, company_id=company_id).update(is_deleted=True)
            if len(selected_params) > 0:
                OrderScreen.objects.filter(order_screen_parameter__code__in=selected_params, company_id=company_id).update(is_deleted=False)
            if select_customer != "0":
                orderscreen_data = OrderScreen.objects.filter(company_id=select_customer).values("order_screen_parameter", "display_ids", "default_value", "is_compulsory", "is_deleted")
                for data in orderscreen_data:
                    OrderScreen.objects.filter(~Q(order_screen_parameter__code="cmb_service"), order_screen_parameter_id=data["order_screen_parameter"], company_id=company_id).update(
                        display_ids=data["display_ids"], default_value=data["default_value"]
                    )
            if len(child_data) > 0:
                for ch in child_data:
                    parent_id = ch["parent_id"]
                    default_value = None
                    default_value1 = ch["default_value1"]
                    default_value2 = str(ch["default_value2"]).strip()
                    default_value3 = str(ch["default_value3"]).strip()
                    if default_value1 is not None and default_value1 != "" and default_value1 != "None":
                        default_value = default_value1
                    elif default_value2 is not None and default_value2 != "" and default_value2 != "None":
                        default_value = default_value2
                    elif default_value3 is not None and default_value3 != "" and default_value3 != "None":
                        default_value = default_value3
                    display_ids = ""
                    if request.POST.get("select"):
                        display_ids = ",".join(ch["select"])
                    OrderScreen.objects.filter(order_screen_parameter_id=parent_id, company_id=company_id).update(display_ids=display_ids, default_value=default_value)
            return HttpResponse(AppResponse.get({"code": 1, "msg": "Order screen saved"}), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"operator": "pws_operators"}])
def operators(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_operators"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/operators.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def operator(request, operator_id):
    try:
        user = None
        operator = None
        operator_role = None
        company = None
        user_profile = None
        ip_restriction = True
        doj = ""
        doc = ""
        dor = ""
        sub_group = None
        subgroup_of_operators = SubGroupOfOperator.objects.filter(is_deleted=False).values("id", "sub_group_name").order_by("id")
        subgroup_of_operators_list = []
        for data in subgroup_of_operators:
            subgroup_of_operators_list.append({"id": data["id"], "sub_group_name": data["sub_group_name"]})
        if operator_id != "0":
            user = User.objects.get(id=operator_id)
            user_profile = UserProfile.objects.filter(user_id=user.id).first()
            ip_restriction = user_profile.ip_restriction
            operator = Operator.objects.get(user_id=user.id)
            company = operator.company_ids
            if operator.sub_group_of_operator:
                id_sub_group = operator.sub_group_of_operator.id
                sub_group = SubGroupOfOperator.objects.filter(id=id_sub_group, is_deleted=False).values("id", "sub_group_name").first()
            operator_role = UserGroup.objects.get(user_id=user.id)
            if operator.doj:
                doj = datetime.datetime.strptime(str(operator.doj).strip(), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
            if operator.doc:
                doc = datetime.datetime.strptime(str(operator.doc).strip(), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
            if operator.dor:
                dor = datetime.datetime.strptime(str(operator.dor).strip(), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
        context = {
            "ope_role": operator_role,
            "user": user, "opera": operator,
            "comp": company,
            "ip_restriction": ip_restriction,
            "doj": doj,
            "doc": doc,
            "dor": dor,
            "subgroup_of_operators" : json.dumps(subgroup_of_operators_list),
            "sub_group": sub_group
        }
        return render(request, "pws/operator.html", context)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_operator(request):
    try:
        with transaction.atomic():
            operator_id = request.POST.get("operator_id")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            operator_group = request.POST.get("operator_group")
            group = request.POST.get("group")
            password = request.POST.get("password")
            is_active = request.POST.get("is_active")
            operator_type = request.POST.get("operator_type")
            company_ids = request.POST.getlist("company_ids")
            shift = request.POST.get("shift")
            permanent_shift = request.POST.get("permanent_shift")
            emp_code = request.POST.get("emp_code")
            user_sub_group_data = request.POST.get("user_sub_group_data")
            sub_group_of_operator = None
            if user_sub_group_data:
                is_exist_sub_group = SubGroupOfOperator.objects.filter(sub_group_name=user_sub_group_data, is_deleted=False).values("id").first()
                if is_exist_sub_group:
                    sub_group_of_operator = is_exist_sub_group["id"]
                else:
                    sub_group_ = SubGroupOfOperator.objects.create(sub_group_name=user_sub_group_data)
                    sub_group_of_operator = sub_group_.id
            show_own_records_only = request.POST.get("show_own_records_only")
            ip_restriction = "ip_restriction" in request.POST
            company_ids = ",".join(company_ids)
            doj = request.POST.get("doj")
            if doj:
                doj = datetime.datetime.strptime(str(doj).strip(), "%d/%m/%Y").strftime("%Y-%m-%d %H:%M")
            else:
                doj = None
            doc = request.POST.get("doc")
            if doc:
                doc = datetime.datetime.strptime(str(doc).strip(), "%d/%m/%Y").strftime("%Y-%m-%d %H:%M")
            else:
                doc = None
            dor = request.POST.get("dor")
            if dor:
                dor = datetime.datetime.strptime(str(dor).strip(), "%d/%m/%Y").strftime("%Y-%m-%d %H:%M")
            else:
                dor = None
            remark = request.POST.get("remark")

            if is_active is None:
                is_active = False
            else:
                is_active = True

            if show_own_records_only is None:
                show_own_records_only = False
            else:
                show_own_records_only = True

            if operator_id != "0":
                if Util.has_perm("edit_operators", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                else:
                    if User.objects.filter(Q(username__iexact=username), ~Q(id=operator_id)):
                        response = {"code": 0, "msg": "Operator already exist."}
                    else:
                        user = User.objects.filter(id=operator_id).update(first_name=first_name, username=username, last_name=last_name, email=email, is_active=is_active)
                        UserProfile.objects.filter(user_id=operator_id).update(ip_restriction=ip_restriction)
                        UserGroup.objects.filter(user_id=operator_id).update(group_id=group)
                        Operator.objects.filter(user_id=operator_id).update(
                            company_ids=company_ids,
                            operator_group=operator_group,
                            operator_type=operator_type,
                            is_active=is_active,
                            shift=shift,
                            permanent_shift=permanent_shift,
                            show_own_records_only=show_own_records_only,
                            doj=doj,
                            doc=doc,
                            dor=dor,
                            remark=remark,
                            emp_code=emp_code,
                            sub_group_of_operator_id=sub_group_of_operator,
                        )
                        c_ip = base_views.get_client_ip(request)
                        action = AuditAction.UPDATE
                        log_views.insert("pws", "operator", [operator_id], action, request.user.id, c_ip, "Operator details update.")
                        response = {"code": 1, "msg": "Operator details update."}
            else:
                if Util.has_perm("add_new_operators", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                else:
                    if not User.objects.filter(username__iexact=username):
                        password = make_password(password)
                        user = User.objects.create(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
                        UserProfile.objects.create(user_id=user.id, user_type=1, partner_id=0, color_scheme=settings.DEFAULT_COLOR_SCHEME, ip_restriction=ip_restriction)
                        UserGroup.objects.create(user_id=user.id, group_id=group)
                        Operator.objects.create(
                            user_id=user.id,
                            company_ids=company_ids,
                            operator_group=operator_group,
                            operator_type=operator_type,
                            is_active=is_active,
                            shift=shift,
                            permanent_shift=permanent_shift,
                            show_own_records_only=show_own_records_only,
                            doj=doj,
                            doc=doc,
                            dor=dor,
                            remark=remark,
                            emp_code=emp_code,
                            sub_group_of_operator_id=sub_group_of_operator,
                        )
                        c_ip = base_views.get_client_ip(request)
                        action = AuditAction.INSERT
                        log_views.insert("pws", "operator", [user.id], action, request.user.id, c_ip, "Operator has been created.")
                        response = {"code": 1, "msg": "Operator has been created."}
                    else:
                        response = {"code": 0, "msg": "Operator already exist."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def create_sub_group_of_operator(request):
    try:
        with transaction.atomic():
            sub_group = request.POST.get("sub_group")
            if sub_group:
                is_exist_sub_group = SubGroupOfOperator.objects.filter(sub_group_name=sub_group, is_deleted=False).values("id").first()
                if is_exist_sub_group:
                    response = {"code": 0}
                    return HttpResponse(json.dumps(response), content_type="json")
                else:
                    SubGroupOfOperator.objects.create(sub_group_name=sub_group)
                    c_ip = base_views.get_client_ip(request)
                    action = AuditAction.INSERT
                    log_views.insert("pws", "operator", [request.user.id], action, request.user.id, c_ip, "Sub group (" + sub_group + ") has been created.")
                    subgroup_of_operators = SubGroupOfOperator.objects.filter(is_deleted=False).values("id", "sub_group_name").order_by("id")
                    subgroup_of_operators_list = []
                    for data in subgroup_of_operators:
                        subgroup_of_operators_list.append({"id": data["id"], "sub_group_name": data["sub_group_name"]})
                    response = {"code": 1, "subgroup_of_operators" : subgroup_of_operators_list}
                    return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_sub_group_of_operator(request):
    try:
        with transaction.atomic():
            sub_group_id = request.POST.get("sub_group_id")
            is_exist_sub_group = SubGroupOfOperator.objects.filter(id=sub_group_id, is_deleted=False).values("id", "sub_group_name").first()
            if is_exist_sub_group:
                all_operator = Operator.objects.filter(sub_group_of_operator=sub_group_id).values("id", "user__username")
                operator_sub_group_delete_id = [x["id"] for x in all_operator]
                Operator.objects.filter(sub_group_of_operator=sub_group_id).update(sub_group_of_operator=None)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.DELETE
                sub_group_dlt_log = str(operator_sub_group_delete_id) + " This all operators sub groups are removed"
                log_views.insert("pws", "subgroupofoperator", [sub_group_id], action, request.user.id, c_ip, sub_group_dlt_log)
                log_views.insert("pws", "operator", [request.user.id], action, request.user.id, c_ip, "Sub group (" + is_exist_sub_group["sub_group_name"] + ") has been deleted.")
                SubGroupOfOperator.objects.filter(id=sub_group_id).update(is_deleted=True)
                subgroup_of_operators = SubGroupOfOperator.objects.filter(is_deleted=False).values("id", "sub_group_name").order_by("id")
                subgroup_of_operators_list = []
                for data in subgroup_of_operators:
                    subgroup_of_operators_list.append({"id": data["id"], "sub_group_name": data["sub_group_name"]})
                response = {"code": 1, "subgroup_of_operators" : subgroup_of_operators_list}
                return HttpResponse(json.dumps(response), content_type="json")
            else:
                response = {"code": 0, "msg": "Sub group has been deleted by another operator. <br><br> Please reload the page to check latest status."}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def edit_sub_group_of_operator(request):
    try:
        with transaction.atomic():
            sub_group_id = request.POST.get("sub_group_id")
            sub_group_name = request.POST.get("sub_group_name")
            is_exist_sub_group = SubGroupOfOperator.objects.filter(~Q(id=sub_group_id), sub_group_name=sub_group_name, is_deleted=False).values("id").first()
            if is_exist_sub_group:
                response = {"code": 0, "msg": "Sub group already exist."}
                return HttpResponse(json.dumps(response), content_type="json")
            else:
                all_operator = Operator.objects.filter(sub_group_of_operator=sub_group_id).values("id", "user__username")
                operator_sub_group_delete_id = [x["id"] for x in all_operator]
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.UPDATE
                sub_group = SubGroupOfOperator.objects.filter(id=sub_group_id).values("sub_group_name").first()
                sub_group_dlt_log = (
                    str(operator_sub_group_delete_id) + " This all operators sub groups are modified from ("
                    + sub_group["sub_group_name"] + " to " + sub_group_name + ")"
                )
                log_views.insert("pws", "subgroupofoperator", [sub_group_id], action, request.user.id, c_ip, sub_group_dlt_log)
                log_views.insert(
                    "pws", "operator", [request.user.id], action, request.user.id, c_ip, "Sub group updated from " + sub_group["sub_group_name"] + " to " + sub_group_name + "."
                )
                SubGroupOfOperator.objects.filter(id=sub_group_id).update(sub_group_name=sub_group_name)
                subgroup_of_operators = SubGroupOfOperator.objects.filter(is_deleted=False).values("id", "sub_group_name").order_by("id")
                subgroup_of_operators_list = []
                for data in subgroup_of_operators:
                    subgroup_of_operators_list.append({"id": data["id"], "sub_group_name": data["sub_group_name"]})
                response = {"code": 1, "subgroup_of_operators" : subgroup_of_operators_list}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def operator_change_password(request):
    try:
        with transaction.atomic():
            user_id = request.POST.get("id")
            user = User.objects.get(id=user_id)
            user.password = make_password(str(request.POST["password"]).strip())
            user.save()
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            log_views.insert("pws", "operator", [user_id], action, request.user.id, c_ip, "Password updated.")
            response = {"code": 1, "msg": "Password updated."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_operators(request):
    try:
        with transaction.atomic():
            if Util.has_perm("delete_operators", request.user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            else:
                user_ids = request.POST.get("ids")
                user_ids = user_ids.split(",")
                for id in user_ids:
                    user = User.objects.filter(id=id).values("username", "id").first()
                    username = user["username"] + "_" + str(user["id"]) + "_" + "dlt"
                    User.objects.filter(id=id).update(username=username)
                Operator.objects.filter(user_id__in=user_ids).update(is_deleted=True)
                UserProfile.objects.filter(user_id__in=user_ids).update(is_deleted=True)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.DELETE
                log_views.insert("pws", "operator", user_ids, action, request.user.id, c_ip, "Operator has been deleted.")
                response = {"code": 1, "msg": "Operator has been deleted."}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_operator(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)

        if request.POST.get("username"):
            query.add(Q(user__username__icontains=request.POST["username"]), query.connector)
        if request.POST.get("first_name"):
            query.add(Q(user__first_name__icontains=request.POST["first_name"]), query.connector)
        if request.POST.get("last_name"):
            query.add(Q(user__last_name__icontains=request.POST["last_name"]), query.connector)
        operator_types = dict(operator_type)
        if request.POST.get("operator_type"):
            name = request.POST.get("operator_type").lower()
            oper_code = [key for key, value in operator_types.items() if name in value.lower()]
            query.add(Q(operator_type__in=oper_code), query.connector)
        operator_groups = dict(operator_group)
        if request.POST.get("operator_group"):
            name = request.POST.get("operator_group").lower()
            group_code = [key for key, value in operator_groups.items() if name in value.lower()]
            query.add(Q(operator_group__in=group_code), query.connector)
        shifts = dict(shift)
        if request.POST.get("shift"):
            name = request.POST.get("shift").lower()
            shift_code = [key for key, value in shifts.items() if name in value.lower()]
            query.add(Q(shift__in=shift_code), query.connector)
        permanent_shifts = dict(permanent_shift)
        if request.POST.get("permanent_shift"):
            name = request.POST.get("permanent_shift").lower()
            permanent_shift_code = [key for key, value in permanent_shifts.items() if name in value.lower()]
            query.add(Q(permanent_shift__in=permanent_shift_code), query.connector)
        if request.POST.get("email"):
            query.add(Q(user__email__icontains=request.POST["email"]), query.connector)
        is_active = request.POST.get("is_active")
        is_active = True if is_active == "Yes" else False
        if request.POST.get("is_active"):
            query.add(Q(is_active=is_active), query.connector)
        query.add(Q(is_deleted=False), query.connector)
        recordsTotal = Operator.objects.filter(query).count()
        sort_col_ = [
            "minimum_efficiency",
            "-minimum_efficiency",
            "target_efficiency",
            "-target_efficiency"
        ]
        users = (
            Operator.objects.filter(query)
            .values("user__id", "operator_type", "operator_group", "is_active", "created_on", "ec_user", "shift", "permanent_shift", "doj")
            .annotate(
                username=F("user__username"),
                first_name=F("user__first_name"),
                last_name=F("user__last_name"),
                email=F("user__email"),
            )
            .order_by(sort_col if sort_col not in sort_col_ else "created_on")
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        user_ids = [user["user__id"] for user in users]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")

        role_data = {}
        for user_role in user_roles:
            role_name = user_role["group__name"]
            if user_role["user_id"] in role_data:
                role_name = role_name + ", " + role_data[user_role["user_id"]]
            role_data[user_role["user_id"]] = role_name

        month = {}
        year = {}
        year_ = {}
        performance_indexes = PerformanceIndex.objects.filter(is_deleted=False).values("years_of_experience", "target_efficiency", "minimum_efficiency")
        for performance_index in performance_indexes:
            exp_ = performance_index["years_of_experience"].split("_")[1]
            if exp_ == "month":
                month[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
            if exp_ == "year":
                year[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
            if exp_ == "years":
                year_[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
        for user in users:
            current_time = datetime.datetime.now()
            created_on_time = user["doj"]
            time_diff = relativedelta(current_time, created_on_time)
            time_year = None
            time_month = None
            time_days = None
            time_hours = None
            time_minutes = None
            time_seconds = None
            target_efficiency = None
            minimum_efficiency = None
            if time_diff.years:
                time_year = time_diff.years
            elif time_diff.months:
                if int(time_diff.months) >= 6:
                    time_year = 0
                else:
                    time_month = time_diff.months
            elif time_diff.days:
                time_days = time_diff.days
            elif time_diff.hours:
                time_hours = time_diff.hours
            elif time_diff.minutes:
                time_minutes = time_diff.minutes
            elif time_diff.seconds:
                time_seconds = time_diff.seconds
            if time_diff:
                if time_month or time_days or time_hours or time_minutes or time_seconds:
                    for key, value in month.items():
                        if time_month:
                            if int(time_month) <= int(key):
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
                        else:
                            target_efficiency = value["target_efficiency"]
                            minimum_efficiency = value["minimum_efficiency"]
                if time_year is not None:
                    if int(time_year) > 0:
                        for key, value in year.items():
                            if int(time_year) < int(key):
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
                        if int(time_year) >= 2:
                            for key, value in year_.items():
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
                    if int(time_year) == 0:
                        for key, value in year.items():
                            if key == "1":
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
            else:
                target_efficiency = int(0)
                minimum_efficiency = int(0)
            response["data"].append(
                {
                    "id": user["user__id"],
                    "username": user["username"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "email": user["email"],
                    "user_role": role_data[user["user__id"]] if user["user__id"] in role_data else "",
                    "operator_group": dict(operator_group)[user["operator_group"]] if user["operator_group"] in dict(operator_group) else "",
                    "is_active": "Yes" if user["is_active"] else "No",
                    "created_on": Util.get_local_time(user["created_on"], True),
                    "operator_type": dict(operator_type)[user["operator_type"]] if user["operator_type"] in dict(operator_type) else "",
                    "shift": dict(shift)[user["shift"]] if user["shift"] in dict(shift) else "",
                    "permanent_shift": dict(permanent_shift)[user["permanent_shift"]] if user["permanent_shift"] in dict(permanent_shift) else "",
                    "target_efficiency": target_efficiency if target_efficiency else 0,
                    "minimum_efficiency": minimum_efficiency if minimum_efficiency else 0,
                    "doj": Util.get_local_time(user["doj"], False),
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        sort_col_asc = ["target_efficiency", "minimum_efficiency"]
        sort_col_desc = ["-target_efficiency", "-minimum_efficiency"]
        if sort_col in sort_col_desc:
            response["data"] = sorted(response["data"], key=lambda i: i[sort_col[1:]], reverse=True)
        if sort_col in sort_col_asc:
            response["data"] = sorted(response["data"], key=lambda i: i[sort_col])
        response["data"] = response["data"][start : (start + length)]
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_operators(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_operators", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(user__id__in=selected_ids), query.connector)

        if request.POST.get("username"):
            query.add(Q(user__username__icontains=request.POST["username"]), query.connector)
        if request.POST.get("first_name"):
            query.add(Q(user__first_name__icontains=request.POST["first_name"]), query.connector)
        if request.POST.get("last_name"):
            query.add(Q(user__last_name__icontains=request.POST["last_name"]), query.connector)
        operator_types = dict(operator_type)
        if request.POST.get("operator_type"):
            name = request.POST.get("operator_type").lower()
            oper_code = [key for key, value in operator_types.items() if name in value.lower()]
            query.add(Q(operator_type__in=oper_code), query.connector)
        operator_groups = dict(operator_group)
        if request.POST.get("operator_group"):
            name = request.POST.get("operator_group").lower()
            group_code = [key for key, value in operator_groups.items() if name in value.lower()]
            query.add(Q(operator_group__in=group_code), query.connector)
        shifts = dict(shift)
        if request.POST.get("shift"):
            name = request.POST.get("shift").lower()
            shift_code = [key for key, value in shifts.items() if name in value.lower()]
            query.add(Q(shift__in=shift_code), query.connector)
        permanent_shifts = dict(permanent_shift)
        if request.POST.get("permanent_shift"):
            name = request.POST.get("permanent_shift").lower()
            permanent_shift_code = [key for key, value in permanent_shifts.items() if name in value.lower()]
            query.add(Q(permanent_shift__in=permanent_shift_code), query.connector)
        if request.POST.get("email"):
            query.add(Q(user__email__icontains=request.POST["email"]), query.connector)
        is_active = request.POST.get("is_active")
        is_active = True if is_active == "Yes" else False
        if request.POST.get("is_active"):
            query.add(Q(is_active=is_active), query.connector)

        query.add(Q(is_deleted=False), query.connector)
        sort_col_ = [
            "minimum_efficiency",
            "-minimum_efficiency",
            "target_efficiency",
            "-target_efficiency"
        ]
        users = (
            Operator.objects.filter(query)
            .values("user__id", "company_ids", "operator_type", "operator_group", "is_active", "created_on", "ec_user", "shift", "permanent_shift", "doj")
            .annotate(
                username=F("user__username"),
                first_name=F("user__first_name"),
                last_name=F("user__last_name"),
                email=F("user__email"),
            )
            .order_by(order_by if order_by not in sort_col_ else "created_on")
        )
        user_ids = [user["user__id"] for user in users]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")
        role_data = {}
        for user_role in user_roles:
            role_name = user_role["group__name"]
            if user_role["user_id"] in role_data:
                role_name = role_name + ", " + role_data[user_role["user_id"]]
            role_data[user_role["user_id"]] = role_name

        month = {}
        year = {}
        year_ = {}
        performance_indexes = PerformanceIndex.objects.filter(is_deleted=False).values("years_of_experience", "target_efficiency", "minimum_efficiency")
        for performance_index in performance_indexes:
            exp_ = performance_index["years_of_experience"].split("_")[1]
            if exp_ == "month":
                month[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
            if exp_ == "year":
                year[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
            if exp_ == "years":
                year_[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
        query_result = []
        for user in users:
            current_time = datetime.datetime.now()
            created_on_time = user["doj"]
            time_diff = relativedelta(current_time, created_on_time)
            time_year = None
            time_month = None
            time_days = None
            time_hours = None
            time_minutes = None
            time_seconds = None
            target_efficiency = None
            minimum_efficiency = None
            if time_diff.years:
                time_year = time_diff.years
            elif time_diff.months:
                if int(time_diff.months) >= 6:
                    time_year = 0
                else:
                    time_month = time_diff.months
            elif time_diff.days:
                time_days = time_diff.days
            elif time_diff.hours:
                time_hours = time_diff.hours
            elif time_diff.minutes:
                time_minutes = time_diff.minutes
            elif time_diff.seconds:
                time_seconds = time_diff.seconds
            if time_diff:
                if time_month or time_days or time_hours or time_minutes or time_seconds:
                    for key, value in month.items():
                        if time_month:
                            if int(time_month) <= int(key):
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
                        else:
                            target_efficiency = value["target_efficiency"]
                            minimum_efficiency = value["minimum_efficiency"]
                if time_year is not None:
                    if int(time_year) > 0:
                        for key, value in year.items():
                            if int(time_year) < int(key):
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
                        if int(time_year) >= 2:
                            for key, value in year_.items():
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
                    if int(time_year) == 0:
                        for key, value in year.items():
                            if key == "1":
                                target_efficiency = value["target_efficiency"]
                                minimum_efficiency = value["minimum_efficiency"]
            else:
                target_efficiency = int(0)
                minimum_efficiency = int(0)
            query_result.append(
                {
                    "username": user["username"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "email": user["email"],
                    "user_role": role_data[user["user__id"]] if user["user__id"] in role_data else "",
                    "operator_group": dict(operator_group)[user["operator_group"]] if user["operator_group"] in dict(operator_group) else "",
                    "is_active": "Yes" if user["is_active"] else "No",
                    "created_on": Util.get_local_time(user["created_on"], True),
                    "operator_type": dict(operator_type)[user["operator_type"]] if user["operator_type"] in dict(operator_type) else "",
                    "shift": dict(shift)[user["shift"]] if user["shift"] in dict(shift) else "",
                    "permanent_shift": dict(permanent_shift)[user["permanent_shift"]] if user["permanent_shift"] in dict(permanent_shift) else "",
                    "target_efficiency": target_efficiency if target_efficiency else 0,
                    "minimum_efficiency": minimum_efficiency if minimum_efficiency else 0,
                }
            )
        headers = [
            {"title": "Operator name"},
            {"title": "First name"},
            {"title": "Last name"},
            {"title": "Email"},
            {"title": "Role"},
            {"title": "Group"},
            {"title": "Active"},
            {"title": "Created on"},
            {"title": "User type"},
            {"title": "Today shift"},
            {"title": "Permanent shift"},
            {"title": "Target efficiency"},
            {"title": "Minimum efficiency"},
        ]
        sort_col_asc = ["target_efficiency", "minimum_efficiency"]
        sort_col_desc = ["-target_efficiency", "-minimum_efficiency"]
        if order_by in sort_col_desc:
            query_result = sorted(query_result, key=lambda i: i[order_by[1:]], reverse=True)
        if order_by in sort_col_asc:
            query_result = sorted(query_result, key=lambda i: i[order_by])
        query_result = query_result[start : (start + length)]
        return Util.export_to_xls(headers, query_result[:5000], "Operators.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def set_order_screen_params(request):
    try:
        parent_id = request.POST.get("id")
        company_id = request.POST.get("company_id")
        default_value = request.POST.get("default_value")
        code = request.POST.get("code")
        is_cmb = False
        is_txt = False
        is_chk = False
        if str(code).startswith("txt_"):
            is_txt = True
        if str(code).startswith("cmb_"):
            is_cmb = True
        if str(code).startswith("chk_"):
            is_chk = True
        screen_master = OrderScreen.objects.filter(order_screen_parameter_id=parent_id, company_id=company_id).values("display_ids", "default_value").first()
        display_ids = []
        if "display_ids" in screen_master and screen_master["display_ids"]:
            display_ids = [int(x) for x in str(screen_master["display_ids"]).split(",")]
        order_screen_params = (
            OrderScreenParameter.objects.filter(parent_id=parent_id)
            .values(
                "id",
                "code",
                "name",
                "sequence",
            )
            .order_by("sequence")
        )
        service_pro = OrderFlowMapping.objects.filter(company=company_id, is_deleted=False).values("service__name")
        service_pro = [x["service__name"] for x in service_pro]
        if code == "cmb_service":
            order_screen_params = Service.objects.values("id", "code", "name")

        con = {
            "service_pro": service_pro,
            "service_pro_code": code,
            "order_screen_params": order_screen_params,
            "default_value": default_value,
            "display_ids": display_ids,
            "is_cmb": is_cmb,
            "is_txt": is_txt,
            "is_chk": is_chk,
        }
        return render(request, "pws/set_order_screen_params.html", con)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"design": "job_processing_design"}])
def designs_view(request, type):
    try:
        user = User.objects.get(id=request.user.id)
        perms = [
            "can_add_new_file",
            "view_file_history",
            "reserve_order_design",
            "release_order_design",
            "send_to_next_design",
            "back_to_previous_design",
            "view_file_design",
            "generate_exception_design",
            "cancel_order_design",
            "can_export_job_processing_design",
        ]
        permissions = Util.get_permission_role(user, perms)
        exception_problems_id = PreDefineExceptionProblem.objects.filter(is_problem=True, is_deleted=False).values("code", "id").first()
        return render(
            request,
            "pws/designs.html",
            {"type": type, "exception_problems_id": exception_problems_id, "permissions": json.dumps(permissions)},
        )
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"preparation": "job_processing_preparation"}])
def preparations_view(request, type):
    try:
        user = User.objects.get(id=request.user.id)
        perms = [
            "can_add_new_file",
            "view_file_history",
            "reserve_order_preparation",
            "release_order_preparation",
            "send_to_next_preparation",
            "back_to_previous_preparation",
            "view_file_preparation",
            "generate_exception_preparation",
            "cancel_order_preparation",
            "can_export_job_processing_preparation",
        ]
        permissions = Util.get_permission_role(user, perms)
        exception_problems_id = PreDefineExceptionProblem.objects.filter(is_problem=True, is_deleted=False).values("code", "id").first()
        return render(
            request,
            "pws/preparations.html",
            {"type": type, "exception_problems_id": exception_problems_id, "permissions": json.dumps(permissions)},
        )
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"production": "job_processing_panel_production"}])
def productions_view(request, type):
    try:
        user = User.objects.get(id=request.user.id)
        perms = [
            "can_add_new_file",
            "view_file_history",
            "reserve_order_production",
            "release_order_production",
            "send_to_next_production",
            "back_to_previous_production",
            "view_file_production",
            "generate_exception_production",
            "cancel_order_production",
            "reserve_and_send_next_multiple_production",
            "can_export_job_processing_panel_preparation",
        ]
        permissions = Util.get_permission_role(user, perms)
        exception_problems_id = PreDefineExceptionProblem.objects.filter(is_problem=True, is_deleted=False).values("code", "id").first()
        return render(
            request,
            "pws/productions.html",
            {"type": type, "exception_problems_id": exception_problems_id, "permissions": json.dumps(permissions)},
        )
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiency_log(request, order_id, prep_time_, order_to_status, efficeiency_remark, back_to_previous):
    try:
        order = Order.objects.filter(id=order_id).values("id", "service__id", "company__id", "order_status", "operator", "layer", "operator__user_id").first()
        layer = order["layer"] if order["layer"] != "" and order["layer"] is not None else ""
        process__code = order["order_status"]
        preparation = None
        if order_to_status == "ppa_exception":
            process__code = "ppa_exception"
        if order_to_status == "exception":
            process__code = "exception"
        if back_to_previous:
            if back_to_previous == "back_to_previous":
                process__code = "back_to_previous"
                preparation = "Back to previous"
        if order["order_status"] == "incoming" and order_to_status == "ppa_exception":
            preparation = "Full preparation"
        if order["order_status"] == "incoming" and order_to_status == "panel":
            preparation = "Full preparation"
        if order["order_status"] == "incoming" and order_to_status == "SICC":
            preparation = "CC required"
        if order["order_status"] == "SI" and order_to_status == "ppa_exception":
            preparation = "Full preparation"
        if order["order_status"] == "SI" and order_to_status == "panel":
            preparation = "Full preparation"
        if order["order_status"] == "SI" and order_to_status == "SICC":
            preparation = "CC required"
        if order["order_status"] == "SICC" and order_to_status == "ppa_exception":
            preparation = "CC required"
        if order["order_status"] == "SICC" and order_to_status == "panel":
            preparation = "CC required"
        efficiency = (
            Efficiency.objects
            .filter(
                company_id=order["company__id"],
                service_id=order["service__id"],
                process__code=process__code,
                is_deleted=False
            ).values("layer", "multi_layer").first()
        )
        layer_point = ""
        layer_ = ""
        layer_ = layer[0:2]
        if efficiency is None:
            layer_ = ""
            layer_point = 0
        else:
            if layer != "":
                if int(layer_) <= 2:
                    layer_ = "1/2 Layers"
                    layer_point = efficiency["layer"] if efficiency["layer"] is not None else 0
                else:
                    layer_ = "Multi Layers"
                    layer_point = efficiency["multi_layer"] if efficiency["multi_layer"] is not None else 0
            else:
                layer_ = ""
                layer_point = 0
        operator_knowledge_list = []
        operator_shift_id = order["operator"]
        operator_shift = Operator.objects.filter(id=operator_shift_id).values("shift", "doj").first()

        # For shift and operator knowledge leader
        shift = None
        if operator_shift:
            shift = operator_shift["shift"]
            operator_shift_ = operator_shift["shift"]
            if operator_shift_ == "first_shift":
                operator_knowledge_leader = Operator.objects.filter(shift="first_shift", is_deleted=False, operator_type="KNOWLEDGE_LEA").values("id")
                if operator_knowledge_leader:
                    for data in operator_knowledge_leader:
                        operator_knowledge_list.append(data["id"])
            if operator_shift_ == "second_shift":
                operator_knowledge_leader = Operator.objects.filter(shift="second_shift", is_deleted=False, operator_type="KNOWLEDGE_LEA").values("id")
                if operator_knowledge_leader:
                    for data in operator_knowledge_leader:
                        operator_knowledge_list.append(data["id"])
            if operator_shift_ == "third_shift":
                operator_knowledge_leader = Operator.objects.filter(shift="third_shift", is_deleted=False, operator_type="KNOWLEDGE_LEA").values("id")
                if operator_knowledge_leader:
                    for data in operator_knowledge_leader:
                        operator_knowledge_list.append(data["id"])
        operator_knowledge_list_ = ",".join(map(str, operator_knowledge_list))
        if operator_knowledge_list_ == "":
            operator_knowledge_list_ = None

        # For Target efficiency and Minimum efficiency
        month = {}
        year = {}
        year_ = {}
        performance_indexes = PerformanceIndex.objects.filter(is_deleted=False).values("years_of_experience", "target_efficiency", "minimum_efficiency")
        for performance_index in performance_indexes:
            exp_ = performance_index["years_of_experience"].split("_")[1]
            if exp_ == "month":
                month[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
            if exp_ == "year":
                year[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
            if exp_ == "years":
                year_[performance_index["years_of_experience"].split("_")[0]] = {
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"]
                }
        current_time = datetime.datetime.now()
        created_on_time = operator_shift["doj"]
        time_diff = relativedelta(current_time, created_on_time)
        time_year = None
        time_month = None
        time_days = None
        time_hours = None
        time_minutes = None
        time_seconds = None
        target_efficiency = None
        minimum_efficiency = None
        if time_diff.years:
            time_year = time_diff.years
        elif time_diff.months:
            if int(time_diff.months) >= 6:
                time_year = 0
            else:
                time_month = time_diff.months
        elif time_diff.days:
            time_days = time_diff.days
        elif time_diff.hours:
            time_hours = time_diff.hours
        elif time_diff.minutes:
            time_minutes = time_diff.minutes
        elif time_diff.seconds:
            time_seconds = time_diff.seconds
        if time_diff:
            if time_month or time_days or time_hours or time_minutes or time_seconds:
                for key, value in month.items():
                    if time_month:
                        if int(time_month) <= int(key):
                            target_efficiency = value["target_efficiency"]
                            minimum_efficiency = value["minimum_efficiency"]
                    else:
                        target_efficiency = value["target_efficiency"]
                        minimum_efficiency = value["minimum_efficiency"]
            if time_year is not None:
                if int(time_year) >= 0:
                    for key, value in year.items():
                        if int(time_year) < int(key):
                            target_efficiency = value["target_efficiency"]
                            minimum_efficiency = value["minimum_efficiency"]
                    if int(time_year) >= 2:
                        for key, value in year_.items():
                            target_efficiency = value["target_efficiency"]
                            minimum_efficiency = value["minimum_efficiency"]
                if int(time_year) == 0:
                    for key, value in year.items():
                        if key == "1":
                            target_efficiency = value["target_efficiency"]
                            minimum_efficiency = value["minimum_efficiency"]
        else:
            target_efficiency = int(0)
            minimum_efficiency = int(0)

        user_effi = UserEfficiencyLog.objects.create(
            operator_id=order["operator"],
            order_id=order_id,
            order_from_status=order["order_status"],
            order_to_status=order_to_status,
            order_layer=layer,
            company_id=order["company__id"],
            prep_time=prep_time_,
            layer=layer_,
            layer_point=layer_point,
            action_code="",
            extra_point=0,
            total_work_efficiency=layer_point,
            service_id=order["service__id"],
            knowledge_leaders=operator_knowledge_list_,
            preparation=preparation,
            operator_shift=shift,
            target_efficiency=target_efficiency,
            minimum_efficiency=minimum_efficiency
        )
        if efficeiency_remark != "":
            auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on").last()
            prep_by = order["operator__user_id"]
            prep_on = auditlog["action_on"]
            base_views.create_remark("pws", "userefficiencylog", user_effi.id, efficeiency_remark, "", request.user.id, "remarks", "Efficeiency_Remarks", "", "", prep_by, prep_on)
            base_views.create_remark("pws", "order", order_id, efficeiency_remark, "", request.user.id, "remarks", "Efficeiency_Remarks", "", "", prep_by, prep_on)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def reserve_and_send_to_next_(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("reserve_and_send_next_multiple_production", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id").first()
            request_user_id = request_user_id["id"]
            operator_list = request.POST.get("operator_list")
            order_list = request.POST.get("order_resrve_send_to_next")
            panel_no = request.POST.get("panel_no")
            panel_qty = request.POST.get("panel_qty")
            order_list = order_list.replace(" ", "").split(",")
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.INSERT
            for cus_order_id in order_list:
                isorder = Order.objects.filter(order_status="panel", customer_order_nr=cus_order_id).values("id").first()
                if isorder:
                    order_id = isorder["id"]
                    operator = Order.objects.filter(id=order_id).values("id", "operator", "operator_id__user__username", "operator_id", "operator__shift").first()
                    if operator["operator"]:
                        operator__user__username = operator["operator_id__user__username"]
                        order_release_operator = "Operator" + " " + "<b>" + " " + operator__user__username + " " + "</b>" + " " + "is released"
                        Order.objects.filter(id=order_id).update(operator=None)
                        action = AuditAction.UPDATE
                        log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_release_operator)
                        reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
                        login_time = reserved_order["logged_in_time"]
                        ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
                        is_active_operator = ActiveOperators.objects.filter(operator_id_id=operator["operator_id"])
                        if len(is_active_operator) == 0:
                            ActiveOperators.objects.create(operator_id_id=operator["operator_id"], logged_in_time=login_time, shift_id=operator["operator__shift"])
                    Order.objects.filter(id=order_id).update(operator=operator_list)
                    operator = Order.objects.filter(id=order_id).values("id", "operator", "operator_id__user__username", "operator_id", "operator__shift").first()
                    order_reserve_operator = "Operator" + " " + "<b>" + " " + operator["operator_id__user__username"] + " " + "</b>" + " " + "is reserved"
                    log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_reserve_operator)
                    operator_id = Operator.objects.filter(user__username=operator["operator_id__user__username"]).values("id", "shift")
                    is_operator_login = OperatorLogs.objects.filter(operator_id_id=operator_id[0]["id"], logged_in_time__isnull=False).values("logged_in_time").first()
                    operator_login_time = None
                    if is_operator_login:
                        operator_login_time = is_operator_login["logged_in_time"]
                    active_operator = ActiveOperators.objects.filter(operator_id_id=operator_id[0]["id"], reserved_order_id_id=None)
                    if active_operator:
                        ActiveOperators.objects.filter(operator_id_id=operator_id[0]["id"], reserved_order_id_id=None).update(
                            shift_id=operator_id[0]["shift"], logged_in_time=operator_login_time, reserved_order_id_id=operator["id"]
                        )
                    else:
                        ActiveOperators.objects.create(
                            operator_id_id=operator_id[0]["id"], shift_id=operator_id[0]["shift"], reserved_order_id_id=operator["id"], logged_in_time=operator_login_time
                        )
                    order = Order.objects.filter(id=order_id).values("id", "service__id", "company__id", "order_status", "operator").first()
                    auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on", "descr").last()
                    process_start_time = auditlog["action_on"].replace(tzinfo=None)
                    current_time = datetime.datetime.now()
                    diff = current_time - process_start_time
                    second = diff.days * 86400 + diff.seconds
                    minutes = second // 60
                    second %= 60
                    prep_time_ = Decimal(str(minutes) + "." + str(second).zfill(2))
                    prep_time_ = diff.days * 86400 + diff.seconds
                    next_status = "upload_panel"
                    user_efficiency_log(request, order_id, prep_time_, next_status, "", "")
                    Order.objects.filter(id=order_id).update(
                        order_status=next_status,
                        order_next_status=None,
                        order_previous_status=order["order_status"],
                        in_time=datetime.datetime.now(),
                        operator=operator_list,
                        panel_no=panel_no,
                        panel_qty=panel_qty,
                    )
                    status = "panel"
                    order_next_status = (
                        "Order sent to " + " " + "<b>" + " " + dict(order_status)[next_status] + " "
                        + "</b>" + " " + "from" + " " + "<b>" + " " + dict(order_status)[status] + " " + "</b>"
                    )
                    log_views.insert_("pws", "order", [order_id], action, request_user_id, c_ip, order_next_status, order["operator"], prep_time_)
                    log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_reserve_operator)
            response = {"code": 1, "msg": "Orders reserve and sent to the next stage successfully."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def reserve_multiple(request):
    try:
        with transaction.atomic():
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id").first()
            request_user_id = request_user_id["id"]
            operator_list = request.POST.get("operator_list")
            order_status = ["exception"]
            order_list = request.POST.get("order_resrve_multiple").replace(" ", "")
            c_ip = base_views.get_client_ip(request)
            order_list_ = []
            if "," in order_list:
                order_list = order_list.split(",")
                for order_id in order_list:
                    isorder = Order.objects.filter(~Q(order_status__in=order_status), customer_order_nr=order_id).values("id").first()
                    if isorder:
                        if isorder["id"] not in order_list_:
                            order_list_.append(isorder["id"])
            else:
                isorder = Order.objects.filter(~Q(order_status__in=order_status), customer_order_nr=order_list).values("id").first()
                if isorder:
                    order_list_.append(isorder["id"])
            for order_id in order_list_:
                operator = Order.objects.filter(id=order_id).values("id", "operator", "operator_id", "operator__shift").first()
                if operator["operator"]:
                    operator_id = Operator.objects.filter(id=operator["operator_id"]).values("user__username").first()
                    operator_username = operator_id["user__username"]
                    order_release_operator = "Operator" + " " + "<b>" + " " + operator_username + " " + "</b>" + " " + "is released"
                    Order.objects.filter(id=order_id).update(operator=None)
                    action = AuditAction.UPDATE
                    log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_release_operator)
                    reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
                    login_time = reserved_order["logged_in_time"]
                    ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
                    is_active_operator = ActiveOperators.objects.filter(operator_id_id=operator["operator_id"])
                    if len(is_active_operator) == 0:
                        ActiveOperators.objects.create(operator_id_id=operator["operator_id"], logged_in_time=login_time, shift_id=operator["operator__shift"])
                Order.objects.filter(id=order_id).update(operator=operator_list)
                operator = Order.objects.filter(id=order_id).values("operator_id", "id").first()
                operator_id = Operator.objects.filter(id=operator["operator_id"]).values("user__username", "id", "shift")
                operator_username = operator_id[0]["user__username"]
                order_reserve_operator = "Operator" + " " + "<b>" + " " + operator_username + " " + "</b>" + " " + "is reserved"
                action = AuditAction.INSERT
                log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_reserve_operator)
                is_operator_login = OperatorLogs.objects.filter(operator_id_id=operator_id[0]["id"], logged_in_time__isnull=False).values("logged_in_time").first()
                operator_login_time = None
                if is_operator_login:
                    operator_login_time = is_operator_login["logged_in_time"]
                active_operator = ActiveOperators.objects.filter(operator_id_id=operator_id[0]["id"], reserved_order_id_id=None)
                if active_operator:
                    ActiveOperators.objects.filter(operator_id_id=operator_id[0]["id"], reserved_order_id_id=None).update(
                        shift_id=operator_id[0]["shift"], logged_in_time=operator_login_time, reserved_order_id_id=operator["id"]
                    )
                else:
                    ActiveOperators.objects.create(
                        operator_id_id=operator_id[0]["id"], shift_id=operator_id[0]["shift"], reserved_order_id_id=operator["id"], logged_in_time=operator_login_time
                    )
            response = {"code": 1, "msg": "Orders reserve successfully."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_to_next_details(request, order_id):
    try:
        order = (
            Order.objects.filter(id=order_id)
            .values(
                "id",
                "service__id",
                "company__id",
                "order_status",
                "operator",
                "layer",
                "operator__user__username",
                "order_previous_status",
                "order_next_status",
            )
            .first()
        )
        order_flow_mapping = OrderFlowMapping.objects.filter(company_id=order["company__id"], service_id=order["service__id"]).values("process_ids").first()
        ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
        processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "sequence", "name").order_by("sequence")
        next_status = ""
        if order["order_previous_status"] == order["order_next_status"] and order["order_status"] == "FQC":
            next_status = order["order_next_status"]
        else:
            cu_sequence = [process["sequence"] if order["order_status"] == process["code"] else None for process in processes]
            cu_sequence = [sequence for sequence in cu_sequence if sequence]
            for process in processes:
                if cu_sequence and cu_sequence[0] < process["sequence"]:
                    next_status = process["code"]
                    break
        process_ = []
        for process in processes:
            if process["code"] != order["order_status"]:
                process_.append(
                    {
                        "name": process["name"],
                        "id": process["code"],
                    }
                )
        auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on", "descr").last()
        process_start_time = auditlog["action_on"].replace(tzinfo=None)
        current_time = datetime.datetime.now()
        diff = current_time - process_start_time
        second = diff.days * 86400 + diff.seconds
        minutes = second // 60
        second %= 60
        prep_time_ = Decimal(str(minutes) + "." + str(second).zfill(2))
        prep_time_decimal = diff.days * 86400 + diff.seconds
        prep_time_ = int(prep_time_)
        layer = order["layer"] if order["layer"] != "" and order["layer"] is not None else ""
        efficiency = (
            Efficiency.objects
            .filter(
                company_id=order["company__id"],
                service_id=order["service__id"],
                process__code=order["order_status"],
                is_deleted=False
            ).values("layer", "multi_layer").first()
        )
        layer_point = ""
        layer_ = ""
        layer_ = layer[0:2]
        if efficiency is None:
            layer_ = ""
            layer_point = 0
        else:
            if layer != "":
                if int(layer_) <= 2:
                    layer_ = "1/2 Layers"
                    layer_point = efficiency["layer"] if efficiency["layer"] is not None else 0
                else:
                    layer_ = "Multi Layers"
                    layer_point = efficiency["multi_layer"] if efficiency["multi_layer"] is not None else 0
            else:
                layer_ = ""
                layer_point = 0
        remark_list = ["schematic", "footprint", "placement", "routing", "gerber_release"]
        if order["order_status"] in remark_list :
            code_ = "Design_Remarks"
        else:
            code_ = order["order_status"] + "_remarks"
        remark_type_send_to_next = CommentType.objects.filter(code=code_, is_active=True).values("name", "id").first()
        panel_file_type_ = FileType.objects.filter(is_active=True, code="PANEL").values("name", "id").first()
        response = {
            "code": 1,
            "prep_time_": prep_time_,
            "layer_point": layer_point,
            "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "",
            "order_status_code": order["order_status"],
            "process_": process_,
            "next_status_code": next_status,
            "next_status_name": dict(order_status)[next_status] if next_status in dict(order_status) else "",
            "operator": order["operator__user__username"],
            "process_start_time": datetime.datetime.strptime(str(process_start_time).strip(), "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M"),
            "prep_time_decimal": prep_time_decimal,
            "remark_type_send_to_next": remark_type_send_to_next,
            "panel_file_type_": panel_file_type_,
        }
        return render(request, "pws/send_to_next_details.html", response)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_to_next(request):
    try:
        with transaction.atomic():
            c_ip = base_views.get_client_ip(request)
            next_status = request.POST.get("next_status")
            order_id = request.POST.get("order_id")
            file_type_send_next = request.POST.get("file_type_send_next")
            file_send_next = request.FILES.get("file_send_next")
            remarks_type = request.POST.get("remarks_type")
            remarks = request.POST.get("remarks")
            efficeiency_check = request.POST.get("efficeiency_check")
            attachment = request.FILES.get("attachment")
            prep_time_ = request.POST.get("prep_time_")
            order = (
                Order.objects.filter(id=order_id)
                .values(
                    "id",
                    "service__id",
                    "company__id",
                    "order_status",
                    "operator",
                    "order_number",
                    "panel_no",
                    "operator_id",
                    "operator__shift",
                    "customer_order_nr",
                    "operator__user_id",
                    "operator_id__user_id__username"
                ).first()
            )
            operator = order["operator_id"]
            if not operator:
                return HttpResponse(
                    AppResponse.msg(0, "Operator is release by another operator.<br><br>Please reload the page to check latest status."), content_type="json"
                )
            auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on").last()
            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=order["company__id"], service_id=order["service__id"]).values("process_ids").first()
            ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
            processes = (
                OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids)
                .values("code", "sequence", "name").order_by("sequence")
            )
            all_processes_sequence_list = [x["sequence"] for x in processes]
            cu_sequence = [process["sequence"] if next_status == process["code"] else None for process in processes]
            cu_sequence = [sequence for sequence in cu_sequence if sequence]
            next_ = None
            ord_previous = None
            for process in processes:
                if cu_sequence and cu_sequence[0] < process["sequence"]:
                    next_ = process["code"]
                    break
            orde_prev_list = []
            for proecess_sequence in all_processes_sequence_list:
                orde_prev_list.append(proecess_sequence)
                if cu_sequence and cu_sequence[0] == proecess_sequence:
                    break
            if len(orde_prev_list) != 0:
                if len(orde_prev_list) == 1:
                    ord_prev = 0
                else:
                    ord_prev = orde_prev_list[-2]
                if ord_prev != 0 and ord_prev in all_processes_sequence_list:
                    ord_prev_ = OrderProcess.objects.filter(sequence=ord_prev).values("code").first()
                    ord_previous = ord_prev_["code"]
                else:
                    ord_previous = None
            reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
            login_time = reserved_order["logged_in_time"]
            ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
            is_active_operator = ActiveOperators.objects.filter(operator_id_id=order["operator_id"])
            if len(is_active_operator) == 0:
                ActiveOperators.objects.create(operator_id_id=order["operator_id"], logged_in_time=login_time, shift_id=order["operator__shift"])
            order_status_upl_panel = order["order_status"]
            panel_no = order["panel_no"]
            if order_status_upl_panel == "upload_panel" and panel_no:
                orders = Order.objects.filter(panel_no=panel_no, order_status="upload_panel").values("id")
                orders_list = [x["id"] for x in orders]
            if file_type_send_next is not None and file_send_next is not None:
                upload_file_name = str(file_send_next)
                upload_file_data = file_send_next.read()
                u_id = request.user.id
                file_type_id = FileType.objects.filter(id=file_type_send_next).values("code").first()
                if order_status_upl_panel == "upload_panel" and panel_no:
                    for orderlist_id in orders_list:
                        order_ = Order.objects.filter(id=orderlist_id).values("order_number", "customer_order_nr").first()
                        Order_Attachment.objects.filter(object_id=orderlist_id, file_type__code=file_type_id["code"]).update(deleted=True)
                        upload_and_save_impersonate(
                            upload_file_data, "pws", "order_attachment", orderlist_id, u_id, c_ip, file_type_id["code"], upload_file_name, order_["customer_order_nr"], ""
                        )
                else:
                    Order_Attachment.objects.filter(object_id=order_id, file_type__code=file_type_id["code"]).update(deleted=True)
                    upload_and_save_impersonate(
                        upload_file_data, "pws", "order_attachment", order_id, u_id, c_ip, file_type_id["code"], upload_file_name, order["customer_order_nr"], ""
                    )
            if remarks != "":
                if order_status_upl_panel == "upload_panel" and panel_no:
                    for orderlist_id in orders_list:
                        order_ = Order.objects.filter(id=orderlist_id).values("order_number", "customer_order_nr", "operator__user_id").first()
                        auditlog = Auditlog.objects.filter(object_id=orderlist_id, descr__endswith=" is reserved").values("action_on").last()
                        prep_by = order_["operator__user_id"]
                        prep_on = auditlog["action_on"]
                        remark = base_views.create_remark("pws", "order", orderlist_id, remarks, "", request.user.id, "remarks", remarks_type, "", "", prep_by, prep_on)
                        if attachment is not None:
                            attachment_name = str(attachment)
                            attachment_data = attachment.read()
                            upload_and_save_impersonate(
                                attachment_data, "base", "Remark_Attachment", remark.id, request.user.id, c_ip, "REMARK", attachment_name, order_["customer_order_nr"], ""
                            )
                else:
                    prep_by = order["operator__user_id"]
                    prep_on = auditlog["action_on"]
                    remark = base_views.create_remark("pws", "order", order_id, remarks, "", request.user.id, "remarks", remarks_type, "", "", prep_by, prep_on)
                    if attachment is not None:
                        attachment_name = str(attachment)
                        attachment_data = attachment.read()
                        upload_and_save_impersonate(
                            attachment_data, "base", "Remark_Attachment", remark.id, request.user.id, c_ip, "REMARK", attachment_name, order["customer_order_nr"], ""
                        )
            manage_auto_allocation = ManageAutoAllocation.objects.values("id", "stop_start_time", "stop_end_time")
            stop_auto_allocation = False
            if manage_auto_allocation:
                time_now = datetime.datetime.now()
                current_time = time_now.strftime("%H:%M:%S")
                for data in manage_auto_allocation:
                    begin_time = str(data["stop_start_time"])
                    end_time = str(data["stop_end_time"])
                    if begin_time < end_time:
                        stop_auto_ = current_time >= begin_time and current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
                    else:
                        stop_auto_ = current_time >= begin_time or current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
            panel_preparation_status = ["panel", "upload_panel"]
            if next_status != "order_finish":
                user_efficiency_log(request, order_id, prep_time_, next_status, efficeiency_check, "")
                Order.objects.filter(id=order_id).update(
                    order_status=next_status, order_next_status=next_, order_previous_status=ord_previous, in_time=datetime.datetime.now(), operator=None
                )
                action = AuditAction.UPDATE
                order_next_status = (
                    "Order sent to " + " " + "<b>" + " " + dict(order_status)[next_status] + " " + "</b>" + " "
                    + "from" + " " + "<b>" + " " + dict(order_status)[order["order_status"]] + " " + "</b>"
                )
                log_views.insert_("pws", "order", [order_id], action, request.user.id, c_ip, order_next_status, order["operator"], prep_time_)
                if stop_auto_allocation is False and next_status not in panel_preparation_status:
                    skill_matrix_data_auto_assign(request, order["company__id"], next_status)
                response = {"code": 1, "msg": "Order sent to the next stage successfully.", "status": next_status}
            if next_status == "order_finish":
                order_status_up_panel = order["order_status"]
                panel_no = order["panel_no"]
                if order_status_up_panel == "upload_panel" and panel_no:
                    for orderlist_id in orders_list:
                        if orderlist_id != int(order_id):
                            remove_active_operator = Order.objects.filter(id=orderlist_id).values("id", "operator_id", "operator__shift").first()
                            reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=orderlist_id).values("logged_in_time").first()
                            login_time = reserved_order["logged_in_time"]
                            ActiveOperators.objects.filter(reserved_order_id_id=orderlist_id).delete()
                            is_active_operator = ActiveOperators.objects.filter(operator_id_id=remove_active_operator["operator_id"])
                            if len(is_active_operator) == 0:
                                ActiveOperators.objects.create(
                                    operator_id_id=remove_active_operator["operator_id"],
                                    logged_in_time=login_time,
                                    shift_id=remove_active_operator["operator__shift"]
                                )
                        user_efficiency_log(request, orderlist_id, prep_time_, "finished", efficeiency_check, "")
                        order_finish_mail(request, orderlist_id, "upload_panel", prep_time_)
                else:
                    user_efficiency_log(request, order_id, prep_time_, "finished", efficeiency_check, "")
                    order_finish_mail(request, order_id, order["order_status"], prep_time_)
                response = {"code": 1, "msg": "Order has been finished.", "status": "upload_panel"}
            if stop_auto_allocation is False and order["order_status"] not in panel_preparation_status:
                skill_matrix_data_auto_assign(request, order["company__id"], order["order_status"])
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order_finish_mail(request, order_id, order_status_f, prep_time_):
    try:
        with transaction.atomic():
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id").first()
            request_user_id = request_user_id["id"]
            c_ip = base_views.get_client_ip(request)
            order = Order.objects.filter(id=order_id).values("id", "service__id", "company__id", "order_status", "operator", "company", "user_id").first()
            Order.objects.filter(id=order_id).update(
                order_status="finished",
                operator=None,
                order_previous_status=order_status_f,
                order_next_status=None,
                in_time=datetime.datetime.now(),
                finished_on=datetime.datetime.now()
            )
            order_detail = Order.objects.filter(id=order_id).values("company__name", "customer_order_nr", "order_number", "service__name", "pcb_name", "layer").first()
            layer = Layer.objects.filter(code=order_detail["layer"]).values("code", "name").first()
            if layer:
                layers = layer["name"]
            else:
                layers = ""
            user_cc_mail = CompanyUser.objects.filter(id=order["user_id"]).values("user__email").first()
            cc_mail = user_cc_mail["user__email"] if user_cc_mail else ""
            email_id = CompanyParameter.objects.filter(company=order["company"]).values("ord_comp_mail", "mail_from").first()
            mail_from = email_id["mail_from"] if email_id["mail_from"] else None
            email_id = email_id["ord_comp_mail"]
            if email_id:
                email_id = [email_ids for email_ids in email_id.split(",")]
                subject = "Order Processed - " + order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
                head = order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
                title = "Your order processed"
                message = render_to_string(
                    "pws/mail_order.html",
                    {
                        "mail_type": "finish_order",
                        "head": head,
                        "title": title,
                        "layers": layers,
                        "order_detail": order_detail,
                    },
                )
                send_mail(True, "public", [*email_id], subject, message, "", [cc_mail], mail_from)
            order_finished = (
                "Order has been " + " " + "<b>" + " " + "Finished" + " " + "</b>" + " " + "from" + " " + "<b>" + " " + dict(order_status)[order["order_status"]] + " " + "</b>"
            )
            action = AuditAction.UPDATE
            log_views.insert_("pws", "order", [order_id], action, request_user_id, c_ip, order_finished, order["operator"], prep_time_)
            log_views.insert("pws", "Order", [order_id], action, request_user_id, c_ip, "Order has been finished")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def skill_matrix_data_auto_assign(request, company_id, status):
    try:
        with transaction.atomic():
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id").first()
            request_user_id = request_user_id["id"]
            query = Q()
            excluded_order_status = ["cancel", "finished"]
            query_skill = Q()
            query_skill.add(Q(logged_in_time__isnull=False), query_skill.connector)
            query_skill.add(~Q(reserved_order_id__order_status__in=excluded_order_status), query_skill.connector)
            query_skill.add(~Q(reserved_order_id__order_status=status), query_skill.connector)
            delivery_date = "id"
            sort_col = "id"
            order_by = OrderAllocationFlow.objects.filter(company_id=company_id)
            if order_by:
                order_by = OrderAllocationFlow.objects.filter(company_id=company_id).values("id", "allocation")
                order_by_name = order_by[0]["allocation"]
                if order_by_name == "pre_due_date":
                    sort_col = "preparation_due_date"
                if order_by_name == "delivery_and_order_date":
                    sort_col = "act_delivery_date"
                    delivery_date = "order_date"
                if order_by_name == "systemin_time":
                    sort_col = "in_time"
                if order_by_name == "delivery_date":
                    sort_col = "act_delivery_date"
                if order_by_name == "order_date":
                    sort_col = "order_date"
                if order_by_name == "layers":
                    sort_col = "-layer_column"
                if order_by_name == "delivery_and_layers":
                    sort_col = "act_delivery_date"
                    delivery_date = "layer_column"
            query.add(Q(company_id=company_id), query.connector)
            query.add(Q(order_status=status), query.connector)
            query.add(Q(operator__user__username=None), query.connector)
            orders = (
                Order.objects.filter(query).values("id", "order_number", "order_status", "operator__user__username")
                .annotate(
                    layer_column=Case(
                        When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                        When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                        When(layer="", then=None),
                        default=None,
                        output_field=IntegerField(),
                    ),
                )
                .order_by(sort_col, delivery_date)
            )
            total_order_list = [i["id"] for i in orders]
            skill_oper_activ = ActiveOperators.objects.filter(query_skill).values("operator_id__user_id", "reserved_order_id__order_status")
            skill_ope_id = [i["operator_id__user_id"] for i in skill_oper_activ]
            skill_matrix = SkillMatrix.objects.filter(company_id=company_id, process__code=status).values("operator_ids").first()
            if len(total_order_list) != 0:
                if skill_matrix:
                    if skill_matrix["operator_ids"] is not None:
                        skill_matrix_oper = []
                        if "," not in skill_matrix["operator_ids"]:
                            operator_ids = Operator.objects.filter(user_id=skill_matrix["operator_ids"]).values("user_id", "user__username").first()
                            skill_matrix_oper.append(operator_ids["user_id"])
                        else:
                            skill_matrix_ope = skill_matrix["operator_ids"].split(",")
                            operator_ids = Operator.objects.filter(user_id__in=skill_matrix_ope).values("user_id", "user__username")
                            for id in operator_ids:
                                skill_matrix_oper.append(id["user_id"])
                        listss_ = []
                        for id in skill_ope_id:
                            if id in skill_matrix_oper:
                                listss_.append(id)
                        listss_1 = []
                        for id in listss_:
                            if id not in listss_1:
                                listss_1.append(id)
                        listss = []
                        for id in listss_1:
                            skill_o = ActiveOperators.objects.filter(Q(reserved_order_id__order_status=status), operator_id__user_id=id).values("operator_id__user_id").count()
                            if skill_o == 1:
                                listss.append(id)
                            if skill_o == 0:
                                listss.append(id)
                                listss.append(id)
                        if len(listss) != 0:
                            total_login = len(listss)
                            for x in range(total_login):
                                if x == len(total_order_list):
                                    break
                                order_id = total_order_list[x]
                                if order_id:
                                    operator_id = listss[x]
                                    ids = Operator.objects.filter(user_id=operator_id).values("id", "shift", "user__username").first()
                                    Order.objects.filter(id=order_id).update(operator=ids["id"])
                                    is_operator_login = OperatorLogs.objects.filter(operator_id_id=ids["id"], logged_in_time__isnull=False).values("logged_in_time").first()
                                    operator_login_time = None
                                    if is_operator_login:
                                        operator_login_time = is_operator_login["logged_in_time"]
                                    active_operator = ActiveOperators.objects.filter(operator_id_id=ids["id"], reserved_order_id_id=None)
                                    if active_operator:
                                        ActiveOperators.objects.filter(operator_id_id=ids["id"], reserved_order_id_id=None).update(
                                            shift_id=ids["shift"], logged_in_time=operator_login_time, reserved_order_id_id=order_id
                                        )
                                    else:
                                        ActiveOperators.objects.create(
                                            operator_id_id=ids["id"], shift_id=ids["shift"], reserved_order_id_id=order_id, logged_in_time=operator_login_time
                                        )
                                    c_ip = base_views.get_client_ip(request)
                                    action = AuditAction.UPDATE
                                    order_reserve_operator = "Operator" + " " + "<b>" + " " + ids["user__username"] + " " + "</b>" + " " + "is reserved"
                                    log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_reserve_operator)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def skill_data_auto_assign_to_login(request, operator_id):
    try:
        with transaction.atomic():
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id").first()
            request_user_id = request_user_id["id"]
            manage_auto_allocation = ManageAutoAllocation.objects.values("id", "stop_start_time", "stop_end_time")
            stop_auto_allocation = False
            if manage_auto_allocation:
                time_now = datetime.datetime.now()
                current_time = time_now.strftime("%H:%M:%S")
                for data in manage_auto_allocation:
                    begin_time = str(data["stop_start_time"])
                    end_time = str(data["stop_end_time"])
                    if begin_time < end_time:
                        stop_auto_ = current_time >= begin_time and current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
                    else:
                        stop_auto_ = current_time >= begin_time or current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
            if operator_id and stop_auto_allocation is False:
                operators = Operator.objects.filter(id=operator_id[0]["id"], is_active=True, is_deleted=False).values("user__username", "company_ids").first()
                customer_list = []
                if operators["company_ids"] != "":
                    if "," not in operators["company_ids"]:
                        customer_list.append(operators["company_ids"])
                    else:
                        customer_list = operators["company_ids"].split(",")
                    for custo_id in customer_list:
                        company_id = custo_id
                        query = Q()
                        excluded_order_status = ["cancel", "finished"]
                        query_skill = Q()
                        query_skill.add(Q(logged_in_time__isnull=False), query_skill.connector)
                        query_skill.add(~Q(reserved_order_id__order_status__in=excluded_order_status), query_skill.connector)
                        query_skill.add(Q(reserved_order_id=None), query_skill.connector)
                        query_skill.add(Q(operator_id=operator_id[0]["id"]), query_skill.connector)
                        delivery_date = "id"
                        sort_col = "id"
                        order_by = OrderAllocationFlow.objects.filter(company_id=company_id)
                        if order_by:
                            order_by = OrderAllocationFlow.objects.filter(company_id=company_id).values("id", "allocation")
                            order_by_name = order_by[0]["allocation"]
                            if order_by_name == "pre_due_date":
                                sort_col = "preparation_due_date"
                            if order_by_name == "delivery_and_order_date":
                                sort_col = "act_delivery_date"
                                delivery_date = "order_date"
                            if order_by_name == "systemin_time":
                                sort_col = "in_time"
                            if order_by_name == "delivery_date":
                                sort_col = "act_delivery_date"
                            if order_by_name == "order_date":
                                sort_col = "order_date"
                            if order_by_name == "layers":
                                sort_col = "-layer_column"
                            if order_by_name == "delivery_and_layers":
                                sort_col = "act_delivery_date"
                                delivery_date = "layer_column"
                        panel_preparation_status = ["cancel", "exception", "finished", "panel", "upload_panel"]
                        query.add(Q(company_id=company_id), query.connector)
                        query.add(Q(operator__user__username=None), query.connector)
                        query.add(~Q(order_status=None), query.connector)
                        query.add(~Q(order_status__in=panel_preparation_status), query.connector)
                        skill_oper_activ = ActiveOperators.objects.filter(query_skill).values("operator_id__user_id", "reserved_order_id__order_status")
                        skill_ope_id = [i["operator_id__user_id"] for i in skill_oper_activ]
                        if skill_ope_id:
                            skill_matrix = SkillMatrix.objects.filter(company_id=company_id).values("process__code", "operator_ids")
                            process_list = []
                            for data in skill_matrix:
                                if data["operator_ids"] is not None:
                                    if "," not in data["operator_ids"]:
                                        operator_ids = Operator.objects.filter(user_id=data["operator_ids"]).values("user_id", "user__username").first()
                                        if skill_ope_id[0] == operator_ids["user_id"]:
                                            process_list.append(data["process__code"])
                                    else:
                                        skill_matrix_ope = data["operator_ids"].split(",")
                                        operator_ids = Operator.objects.filter(user_id__in=skill_matrix_ope).values("user_id", "user__username")
                                        for id in operator_ids:
                                            if skill_ope_id[0] == id["user_id"]:
                                                process_list.append(data["process__code"])
                            for data in process_list:
                                orders = (
                                    Order.objects.filter(query, order_status=data)
                                    .values("id", "order_number", "order_status", "operator__user__username", "company__name")
                                    .annotate(
                                        layer_column=Case(
                                            When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                                            When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                                            When(layer="", then=None),
                                            default=None,
                                            output_field=IntegerField(),
                                        ),
                                    )
                                    .order_by(sort_col, delivery_date)
                                    .first()
                                )
                                if orders:
                                    order_id = orders["id"]
                                    ids = Operator.objects.filter(id=operator_id[0]["id"]).values("id", "shift", "user__username").first()
                                    Order.objects.filter(id=order_id).update(operator=ids["id"])
                                    is_operator_login = OperatorLogs.objects.filter(operator_id_id=ids["id"], logged_in_time__isnull=False).values("logged_in_time").first()
                                    operator_login_time = None
                                    if is_operator_login:
                                        operator_login_time = is_operator_login["logged_in_time"]
                                    active_operator = ActiveOperators.objects.filter(operator_id_id=ids["id"], reserved_order_id_id=None)
                                    if active_operator:
                                        ActiveOperators.objects.filter(operator_id_id=ids["id"], reserved_order_id_id=None).update(
                                            shift_id=ids["shift"], logged_in_time=operator_login_time, reserved_order_id_id=order_id
                                        )
                                    else:
                                        ActiveOperators.objects.create(
                                            operator_id_id=ids["id"], shift_id=ids["shift"], reserved_order_id_id=order_id, logged_in_time=operator_login_time
                                        )
                                    c_ip = base_views.get_client_ip(request)
                                    action = AuditAction.UPDATE
                                    order_reserve_operator = "Operator" + " " + "<b>" + " " + ids["user__username"] + " " + "</b>" + " " + "is reserved"
                                    log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_reserve_operator)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def skill_matrix_order(request, order_id, next_status, user_id=None):
    try:
        with transaction.atomic():
            manage_auto_allocation = ManageAutoAllocation.objects.values("id", "stop_start_time", "stop_end_time")
            stop_auto_allocation = False
            if manage_auto_allocation:
                time_now = datetime.datetime.now()
                current_time = time_now.strftime("%H:%M:%S")
                for data in manage_auto_allocation:
                    begin_time = str(data["stop_start_time"])
                    end_time = str(data["stop_end_time"])
                    if begin_time < end_time:
                        stop_auto_ = current_time >= begin_time and current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
                    else:
                        stop_auto_ = current_time >= begin_time or current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
            user_id = user_id if user_id else request.user.id
            order = Order.objects.filter(id=order_id).values("id", "company__id").first()
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            excluded_order_status = ["cancel", "finished"]
            query_skill = Q()
            query_skill.add(Q(logged_in_time__isnull=False), query_skill.connector)
            query_skill.add(~Q(reserved_order_id__order_status__in=excluded_order_status), query_skill.connector)
            query_skill.add(~Q(reserved_order_id__order_status=next_status), query_skill.connector)
            skill_oper_activ = ActiveOperators.objects.filter(query_skill).values("operator_id__user_id", "reserved_order_id__order_status")
            skill_ope_id = [i["operator_id__user_id"] for i in skill_oper_activ]
            skill_matrix = SkillMatrix.objects.filter(company_id=order["company__id"], process__code=next_status).values("operator_ids").first()
            if skill_matrix and stop_auto_allocation is False:
                if skill_matrix["operator_ids"] is not None:
                    skill_matrix_oper = []
                    if "," not in skill_matrix["operator_ids"]:
                        operator_ids = Operator.objects.filter(user_id=skill_matrix["operator_ids"]).values("user_id", "user__username").first()
                        skill_matrix_oper.append(operator_ids["user_id"])
                    else:
                        skill_matrix_ope = skill_matrix["operator_ids"].split(",")
                        operator_ids = Operator.objects.filter(user_id__in=skill_matrix_ope).values("user_id", "user__username")
                        for id in operator_ids:
                            skill_matrix_oper.append(id["user_id"])
                    listss_ = []
                    for id in skill_ope_id:
                        if id in skill_matrix_oper:
                            listss_.append(id)
                    listss_1 = []
                    for id in listss_:
                        if id not in listss_1:
                            listss_1.append(id)
                    listss = []
                    for id in listss_1:
                        skill_o = ActiveOperators.objects.filter(Q(reserved_order_id__order_status=next_status), operator_id__user_id=id).values("operator_id__user_id").count()
                        if skill_o == 1:
                            listss.append(id)
                        if skill_o == 0:
                            listss.append(id)
                    if len(listss) != 0:
                        ids = Operator.objects.filter(user_id=listss[0]).values("id", "shift", "user__username").first()
                        operator_free = ids["id"]
                        Order.objects.filter(id=order_id).update(operator=operator_free)
                        order_reserve_operator = "Operator" + " " + "<b>" + " " + ids["user__username"] + " " + "</b>" + " " + "is reserved"
                        log_views.insert("pws", "order", [order_id], action, user_id, c_ip, order_reserve_operator)
                        is_operator_login = OperatorLogs.objects.filter(operator_id_id=ids["id"], logged_in_time__isnull=False).values("logged_in_time").first()
                        operator_login_time = None
                        if is_operator_login:
                            operator_login_time = is_operator_login["logged_in_time"]
                        active_operator = ActiveOperators.objects.filter(operator_id_id=ids["id"], reserved_order_id_id=None)
                        if active_operator:
                            ActiveOperators.objects.filter(operator_id_id=ids["id"], reserved_order_id_id=None).update(
                                shift_id=ids["shift"], logged_in_time=operator_login_time, reserved_order_id_id=order["id"]
                            )
                        else:
                            ActiveOperators.objects.create(operator_id_id=ids["id"], shift_id=ids["shift"], reserved_order_id_id=order["id"], logged_in_time=operator_login_time)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def back_to_previous_details(request, order_id):
    try:
        order = (
            Order.objects.filter(id=order_id)
            .values(
                "id",
                "service__id",
                "company__id",
                "order_status",
                "layer",
                "operator__user__username",
                "order_previous_status",
                "order_next_status",
            )
            .first()
        )
        order_flow_mapping = OrderFlowMapping.objects.filter(company_id=order["company__id"], service_id=order["service__id"]).values("process_ids").first()
        ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
        processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "sequence", "name").order_by("sequence")
        all_processes_sequence_list = [x["sequence"] for x in processes]
        if order["order_previous_status"] == order["order_next_status"] and order["order_status"] == "FQC":
            ord_previous = order["order_previous_status"]
        else:
            cu_sequence__f = [process["sequence"] if order["order_status"] == process["code"] else None for process in processes]
            cu_sequence__f = [sequence for sequence in cu_sequence__f if sequence]
            ord_previous = None
            orde_prev_list = []
            for process in processes:
                orde_prev_list.append(process["sequence"])
                if cu_sequence__f and cu_sequence__f[0] == process["sequence"]:
                    break
            if len(orde_prev_list) != 0:
                if len(orde_prev_list) == 1:
                    ord_stat = 0
                else:
                    ord_stat = orde_prev_list[-2]
                if ord_stat != 0 and ord_stat in all_processes_sequence_list:
                    ord_stat_ = OrderProcess.objects.filter(sequence=ord_stat).values("code").first()
                    ord_previous = ord_stat_["code"]
                else:
                    ord_previous = None
        auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on", "descr").last()
        process_start_time = auditlog["action_on"].replace(tzinfo=None)
        current_time = datetime.datetime.now()
        diff = current_time - process_start_time
        second = diff.days * 86400 + diff.seconds
        minutes = second // 60
        second %= 60
        prep_time_ = Decimal(str(minutes) + "." + str(second).zfill(2))
        prep_time_decimal = diff.days * 86400 + diff.seconds
        prep_time_ = int(prep_time_)
        layer = order["layer"] if order["layer"] != "" and order["layer"] is not None else ""
        efficiency = (
            Efficiency.objects
            .filter(
                company_id=order["company__id"],
                service_id=order["service__id"],
                process__code="back_to_previous",
                is_deleted=False
            ).values("layer", "multi_layer").first()
        )
        layer_point = ""
        layer_ = ""
        layer_ = layer[0:2]
        if efficiency is None:
            layer_ = ""
            layer_point = 0
        else:
            if layer != "":
                if int(layer_) <= 2:
                    layer_ = "1/2 Layers"
                    layer_point = efficiency["layer"] if efficiency["layer"] is not None else 0
                else:
                    layer_ = "Multi Layers"
                    layer_point = efficiency["multi_layer"] if efficiency["multi_layer"] is not None else 0
            else:
                layer_ = ""
                layer_point = 0
        remark_list = ["schematic", "footprint", "placement", "routing", "gerber_release"]
        if order["order_status"] in remark_list :
            code_ = "Design_Remarks"
        else:
            code_ = order["order_status"] + "_remarks"
        remark_type_back_to_previous = CommentType.objects.filter(code=code_, is_active=True).values("name", "id").first()
        panel_file_type_ = FileType.objects.filter(is_active=True, code="PANEL").values("name", "id").first()
        response = {
            "code": 1,
            "prep_time_": prep_time_,
            "layer_point": layer_point,
            "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "",
            "order_status_code": order["order_status"],
            "ord_previous_code": ord_previous,
            "ord_previous_name": dict(order_status)[ord_previous] if ord_previous in dict(order_status) else "",
            "operator": order["operator__user__username"],
            "process_start_time": datetime.datetime.strptime(str(process_start_time).strip(), "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M"),
            "prep_time_decimal": prep_time_decimal,
            "remark_type_back_to_previous": remark_type_back_to_previous,
            "panel_file_type_": panel_file_type_,
        }
        return render(request, "pws/back_to_previous_details.html", response)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def back_to_previous(request):
    try:
        with transaction.atomic():
            c_ip = base_views.get_client_ip(request)
            back_to_previous_code = request.POST.get("back_to_previous_code")
            order_id = request.POST.get("order_id")
            file_type_back_to_previous = request.POST.get("file_type_back_to_previous")
            file_back_to_previous = request.FILES.get("file_back_to_previous")
            remarks_type_back_to_previous = request.POST.get("remarks_type_back_to_previous")
            remarks_back_to_previous = request.POST.get("remarks_back_to_previous")
            efficeiency_check_back_to_previous = request.POST.get("efficeiency_check_back_to_previous")
            attachment_back_to_previous = request.FILES.get("attachment_back_to_previous")
            prep_time_back_to_previous = request.POST.get("prep_time_back_to_previous")
            order = (
                Order.objects.filter(id=order_id)
                .values(
                    "id",
                    "service__id",
                    "company__id",
                    "order_status",
                    "operator",
                    "order_number",
                    "order_next_status",
                    "operator_id",
                    "operator__shift",
                    "customer_order_nr",
                    "operator__user_id"
                ).first()
            )
            operator = order["operator_id"]
            if not operator:
                return HttpResponse(
                    AppResponse.msg(0, "Operator is release by another operator.<br><br>Please reload the page to check latest status."), content_type="json"
                )
            auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on").last()
            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=order["company__id"], service_id=order["service__id"]).values("process_ids").first()
            ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
            processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "sequence", "name").order_by("sequence")
            all_processes_sequence_list = [x["sequence"] for x in processes]
            next_ = None
            ord_previous = None
            if back_to_previous_code == order["order_next_status"] and order["order_status"] == "FQC":
                cu_sequence__f = [process["sequence"] if back_to_previous_code == process["code"] else None for process in processes]
                cu_sequence__f = [sequence for sequence in cu_sequence__f if sequence]
                orde_prev_list = []
                for process in processes:
                    if cu_sequence__f and cu_sequence__f[0] < process["sequence"]:
                        next_ = process["code"]
                        break
                for proecess_sequence in all_processes_sequence_list:
                    orde_prev_list.append(proecess_sequence)
                    if cu_sequence__f and cu_sequence__f[0] == proecess_sequence:
                        break
                if len(orde_prev_list) != 0:
                    if len(orde_prev_list) == 1:
                        ord_prev = 0
                    else:
                        ord_prev = orde_prev_list[-2]
                    if ord_prev != 0 and ord_prev in all_processes_sequence_list:
                        ord_prev_ = OrderProcess.objects.filter(sequence=ord_prev).values("code").first()
                        ord_previous = ord_prev_["code"]
                    else:
                        ord_previous = None
            else:
                next_ = order["order_status"]
                cu_sequence__f = [process["sequence"] if order["order_status"] == process["code"] else None for process in processes]
                cu_sequence__f = [sequence for sequence in cu_sequence__f if sequence]
                orde_prev_list = []
                for process in processes:
                    orde_prev_list.append(process["sequence"])
                    if cu_sequence__f and cu_sequence__f[0] == process["sequence"]:
                        break
                if len(orde_prev_list) != 0:
                    if len(orde_prev_list) >= 3:
                        ord_prev = orde_prev_list[-3]
                    else:
                        ord_prev = 0
                    if ord_prev != 0 and ord_prev in all_processes_sequence_list:
                        ord_prev_ = OrderProcess.objects.filter(sequence=ord_prev).values("code").first()
                        ord_previous = ord_prev_["code"]
                    else:
                        ord_previous = None
            reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
            login_time = reserved_order["logged_in_time"]
            ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
            is_active_operator = ActiveOperators.objects.filter(operator_id_id=order["operator_id"])
            if len(is_active_operator) == 0:
                ActiveOperators.objects.create(operator_id_id=order["operator_id"], logged_in_time=login_time, shift_id=order["operator__shift"])
            if file_type_back_to_previous is not None and file_back_to_previous is not None:
                upload_file_name = str(file_back_to_previous)
                upload_file_data = file_back_to_previous.read()
                u_id = request.user.id
                file_type_id = FileType.objects.filter(id=file_type_back_to_previous).values("code").first()
                Order_Attachment.objects.filter(object_id=order_id, file_type__code=file_type_id["code"]).update(deleted=True)
                upload_and_save_impersonate(
                    upload_file_data, "pws", "order_attachment", order_id, u_id, c_ip, file_type_id["code"], upload_file_name, order["customer_order_nr"], ""
                )
            if remarks_back_to_previous != "":
                prep_by = order["operator__user_id"]
                prep_on = auditlog["action_on"]
                remark = base_views.create_remark(
                    "pws", "order", order_id, remarks_back_to_previous, "", request.user.id, "remarks", remarks_type_back_to_previous, "", "", prep_by, prep_on
                )
                if attachment_back_to_previous is not None:
                    attachment_name = str(attachment_back_to_previous)
                    attachment_data = attachment_back_to_previous.read()
                    upload_and_save_impersonate(
                        attachment_data, "base", "Remark_Attachment", remark.id, request.user.id, c_ip, "REMARK", attachment_name, order["customer_order_nr"], ""
                    )
            manage_auto_allocation = ManageAutoAllocation.objects.values("id", "stop_start_time", "stop_end_time")
            stop_auto_allocation = False
            if manage_auto_allocation:
                time_now = datetime.datetime.now()
                current_time = time_now.strftime("%H:%M:%S")
                for data in manage_auto_allocation:
                    begin_time = str(data["stop_start_time"])
                    end_time = str(data["stop_end_time"])
                    if begin_time < end_time:
                        stop_auto_ = current_time >= begin_time and current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
                    else:
                        stop_auto_ = current_time >= begin_time or current_time <= end_time
                        if stop_auto_ is True:
                            stop_auto_allocation = stop_auto_
            panel_preparation_status = ["panel", "upload_panel"]
            user_efficiency_log(request, order_id, prep_time_back_to_previous, back_to_previous_code, efficeiency_check_back_to_previous, "back_to_previous")
            Order.objects.filter(id=order_id).update(
                order_status=back_to_previous_code, order_next_status=next_, order_previous_status=ord_previous, in_time=datetime.datetime.now(), operator=None
            )
            action = AuditAction.UPDATE
            order_previous_status = (
                "Order sent back to " + " " + "<b>" + " " + dict(order_status)[back_to_previous_code] + " "
                + "</b>" + " " + "from" + " " + "<b>" + " " + dict(order_status)[order["order_status"]] + " " + "</b>"
            )
            log_views.insert_("pws", "order", [order_id], action, request.user.id, c_ip, order_previous_status, order["operator"], prep_time_back_to_previous)
            if stop_auto_allocation is False and back_to_previous_code not in panel_preparation_status:
                skill_matrix_data_auto_assign(request, order["company__id"], back_to_previous_code)
            if stop_auto_allocation is False and order["order_status"] not in panel_preparation_status:
                skill_matrix_data_auto_assign(request, order["company__id"], order["order_status"])
            response = {"code": 1, "msg": "Order sent back to the previous stage successfully.", "status": back_to_previous_code}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order(request, order_id, remarks_status):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_add_new_file", "view_file_history", "can_edit_order"]
        permissions = Util.get_permission_role(user, perms)
        order_deta = OrderTechParameter.objects.filter(order__id=order_id).values().first()
        order_details = Order.objects.filter(id=order_id).values().first()
        company_name = Company.objects.filter(id=order_details["company_id"]).values().first()
        service_name = Service.objects.filter(id=order_details["service_id"]).values().first()
        files = Order_Attachment.objects.filter(object_id=order_details["id"], file_type__code="ORDERFILE", deleted=False).values("id", "name", "uid", "size").first()
        order_screen = list(OrderScreen.objects.filter(company_id=order_details["company_id"], is_deleted=False).values_list("order_screen_parameter__code", flat=True))
        tech_parameter = list(set(order_screen).intersection(set(technical_parameter)))
        customer_spec_parameter = list(set(order_screen).intersection(set(customer_specific_parameter)))
        customer_user_id = CompanyUser.objects.filter(user=request.user.id).values("id").first()
        customer_user = None
        if customer_user_id is None:
            customer_user = False
        else:
            customer_user = True
        order_screen_masters = list(
            OrderScreen.objects.filter(company_id=order_details["company_id"], is_deleted=False)
            .values("display_ids", "order_screen_parameter__code", "is_compulsory", "order_screen_parameter_id")
            .order_by("order_screen_parameter__sequence")
        )
        service_display_id = [y for x in order_screen_masters if x["display_ids"] if x["order_screen_parameter__code"] == "cmb_service" for y in x["display_ids"].split(",")]
        services = Service.objects.filter(id__in=service_display_id).values("id", "name", "code")
        sub_parameter_ids = [y for x in order_screen_masters if x["display_ids"] for y in x["display_ids"].split(",")]
        layer_display_code = [layer_code["code"] for layer_code in OrderScreenParameter.objects.filter(id__in=sub_parameter_ids).values("code").order_by("sequence")]
        response = OrderScreenParameter.objects.filter(id__in=sub_parameter_ids).values("code", "name", "parent_id", "parent_id__code")
        layers = Layer.objects.filter(code__in=layer_display_code).values("id", "name", "code")
        board_thickness_display_id = [
            y for x in order_screen_masters if x["display_ids"] if x["order_screen_parameter__code"] == "cmb_board_thickness" for y in x["display_ids"].split(",")
        ]
        board_thickness_display_code = [
            board_thickness["code"] for board_thickness in OrderScreenParameter.objects.filter(id__in=board_thickness_display_id).values("code").order_by("sequence")
        ]
        board_thickness = BoardThickness.objects.filter(code__in=board_thickness_display_code).values("id", "name", "code")
        code_dict = {}
        for order_code in order_screen:
            my_dict = {}
            for order in order_screen_masters:
                if order["order_screen_parameter__code"] == order_code:
                    for res in response:
                        if order["order_screen_parameter_id"] == res["parent_id"]:
                            my_dict[res["code"]] = res["name"]
            code_dict[order_code] = my_dict
        hide_add_file = False if order_details["order_status"] in ["cancel", "exception", "finished"] else True
        is_reserve = True if order_details["operator_id"] else False
        context = {
            "hide_add_file" : hide_add_file,
            "is_reserve": is_reserve,
            "order_deta": order_deta,
            "order_details": order_details,
            "permissions": json.dumps(permissions),
            "code_dict": code_dict,
            "order_screen_master": order_screen_masters,
            "services": services,
            "layers": layers,
            "board_thicknesses": board_thickness,
            "technical_parameter": tech_parameter,
            "remarks_status": remarks_status,
            "customer_user": customer_user,
            "company_name": company_name,
            "service_name": service_name,
            "customer_specific_parameter": customer_spec_parameter,
            "file": files["name"] if files else None,
            "size": str(files["size"]) + " KB" if files else None,
            "order_screen": order_screen,
            "remarks": BeautifulSoup(order_details["remarks"], features="html5lib").get_text(),
            "order_date": Util.get_local_time(order_details["order_date"], True),
            "delivery_date": Util.get_local_time(order_details["delivery_date"], True),
            "preparation_due_date": Util.get_local_time(order_details["preparation_due_date"], True),
        }
        return render(request, "pws/order.html", context)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def reserve_operator(request):
    try:
        with transaction.atomic():
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id").first()
            request_user_id = request_user_id["id"]
            operator_list = request.POST.get("operator")
            order_list = request.POST.get("order_id")
            order_status_ = ["exception"]
            c_ip = base_views.get_client_ip(request)
            order_list_ = []
            if "," in order_list:
                order_list = list(map(int, order_list.split(",")))
                for order_id in order_list:
                    isorder = Order.objects.filter(~Q(order_status__in=order_status_), id=order_id).values("id").first()
                    if isorder:
                        if isorder["id"] not in order_list_:
                            order_list_.append(isorder["id"])
            else:
                isorder = Order.objects.filter(~Q(order_status__in=order_status_), operator=None, id=int(order_list)).values("id").first()
                if isorder:
                    order_list_.append(isorder["id"])
            for order_id in order_list_:
                operator = Order.objects.filter(id=order_id).values("id", "operator", "operator_id", "operator__shift").first()
                if operator["operator"]:
                    operator_id = Operator.objects.filter(id=operator["operator_id"]).values("user__username").first()
                    operator_username = operator_id["user__username"]
                    order_release_operator = "Operator" + " " + "<b>" + " " + operator_username + " " + "</b>" + " " + "is released"
                    Order.objects.filter(id=order_id).update(operator=None)
                    action = AuditAction.UPDATE
                    log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_release_operator)
                    reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
                    login_time = reserved_order["logged_in_time"]
                    ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
                    is_active_operator = ActiveOperators.objects.filter(operator_id_id=operator["operator_id"])
                    if len(is_active_operator) == 0:
                        ActiveOperators.objects.create(operator_id_id=operator["operator_id"], logged_in_time=login_time, shift_id=operator["operator__shift"])
                Order.objects.filter(id=order_id).update(operator=operator_list)
                operator = Order.objects.filter(id=order_id).values("operator_id", "id").first()
                operator_id = Operator.objects.filter(id=operator["operator_id"]).values("user__username", "id", "shift")
                operator_username = operator_id[0]["user__username"]
                order_reserve_operator = "Operator" + " " + "<b>" + " " + operator_username + " " + "</b>" + " " + "is reserved"
                action = AuditAction.INSERT
                log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_reserve_operator)
                is_operator_login = OperatorLogs.objects.filter(operator_id_id=operator_id[0]["id"], logged_in_time__isnull=False).values("logged_in_time").first()
                operator_login_time = None
                if is_operator_login:
                    operator_login_time = is_operator_login["logged_in_time"]
                active_operator = ActiveOperators.objects.filter(operator_id_id=operator_id[0]["id"], reserved_order_id_id=None)
                if active_operator:
                    ActiveOperators.objects.filter(operator_id_id=operator_id[0]["id"], reserved_order_id_id=None).update(
                        shift_id=operator_id[0]["shift"], logged_in_time=operator_login_time, reserved_order_id_id=operator["id"]
                    )
                else:
                    ActiveOperators.objects.create(
                        operator_id_id=operator_id[0]["id"], shift_id=operator_id[0]["shift"], reserved_order_id_id=operator["id"], logged_in_time=operator_login_time
                    )
            response = {"code": 1, "msg": "Operator reserved successfully."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def release_operator(request, order_ids):
    try:
        with transaction.atomic():
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id").first()
            request_user_id = request_user_id["id"]
            order_list = order_ids
            order_list_ = []
            if "," in order_list:
                order_list = list(map(int, order_list.split(",")))
                for order_id in order_list:
                    isorder = Order.objects.filter(~Q(operator=None), id=order_id).values("id").first()
                    if isorder:
                        if isorder["id"] not in order_list_:
                            order_list_.append(isorder["id"])
            else:
                isorder = Order.objects.filter(~Q(operator=None), id=int(order_list)).values("id").first()
                if isorder:
                    order_list_.append(isorder["id"])
            for order_id in order_list_:
                operator = Order.objects.filter(id=order_id).values("operator_id", "operator__shift").first()
                operator_id = Operator.objects.filter(id=operator["operator_id"]).values("user__username").first()
                operator_username = operator_id["user__username"]
                order_release_operator = "Operator" + " " + "<b>" + " " + operator_username + " " + "</b>" + " " + "is released"
                Order.objects.filter(id=order_id).update(operator=None)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.UPDATE
                log_views.insert("pws", "order", [order_id], action, request_user_id, c_ip, order_release_operator)
                reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
                login_time = reserved_order["logged_in_time"]
                ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
                is_active_operator = ActiveOperators.objects.filter(operator_id_id=operator["operator_id"])
                if len(is_active_operator) == 0:
                    ActiveOperators.objects.create(operator_id_id=operator["operator_id"], logged_in_time=login_time, shift_id=operator["operator__shift"])
            response = {"code": 1, "msg": "Operator released successfully."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def workspace_search(request, status, id, type):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        query.add(Q(order_status=status), query.connector)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "layer":
            sort_col = "layer_column"
        if sort_col == "-layer":
            sort_col = "-layer_column"
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_com_ids = Operator.objects.filter(user__id=request_user_id["id"]).values("company_ids").first()
        if operator_com_ids:
            operator_role = UserGroup.objects.filter(user_id=request_user_id["id"]).values("group__name").first()
            if operator_role["group__name"] == "Engineer":
                if operator_com_ids["company_ids"]:
                    operator_com_ids = list(map(int, operator_com_ids["company_ids"].split(",")))
                    query.add(Q(company_id__in=operator_com_ids), query.connector)
                else:
                    query.add(Q(company_id=None), query.connector)
        operator_id = Operator.objects.filter(show_own_records_only=True, user__username=request.user).first()
        if operator_id:
            query.add(Q(operator=operator_id), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("operator"):
            query.add(Q(operator__user__username__icontains=request.POST["operator"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("customer"):
            query.add(Q(company__name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("order_date"):
            query.add(
                Q(
                    order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        recordsTotal = Order.objects.filter(query).count()
        orders = (
            Order.objects.prefetch_related("ordertechparameter_set")
            .filter(query)
            .values(
                "id",
                "order_status",
                "order_date",
                "preparation_due_date",
                "delivery_date",
                "order_number",
                "pcb_name",
                "service__name",
                "order_next_status",
                "order_previous_status",
                "remarks",
                "customer_order_nr",
                "layer",
                "in_time",
                "panel_no",
                "panel_qty",
            )
            .annotate(
                operator=F("operator__user__username"),
                operator_id=F("operator__user__id"),
                customer=F("company__name"),
                tool_nr=F("ordertechparameter__tool_nr"),
                board_thickness=F("ordertechparameter__board_thickness"),
                material_tg=F("ordertechparameter__material_tg"),
                bottom_solder_mask=F("ordertechparameter__bottom_solder_mask"),
                top_solder_mask=F("ordertechparameter__top_solder_mask"),
                top_legend=F("ordertechparameter__top_legend"),
                bottom_legend=F("ordertechparameter__bottom_legend"),
                surface_finish=F("ordertechparameter__surface_finish"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            )
            .order_by(sort_col)[start : (start + length)]
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        remarks_list = [order_["id"] for order_ in orders]
        remarks = Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list).values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        layers_code = [order_["layer"] for order_ in orders]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)

        order_status_code = [order["order_status"] for order in orders]
        status = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), code__in=order_status_code).values("code", "name")
        order_status_name = Util.get_dict_from_quryset("code", "name", status)
        for order in orders:
            response["data"].append(
                {
                    "id": order["id"],
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "preparation_due_date": Util.get_local_time(order["preparation_due_date"], True),
                    "delivery_date": Util.get_local_time(order["delivery_date"], True),
                    "order_number": order["order_number"],
                    "pcb_name": order["pcb_name"],
                    "operator_id": order["operator_id"],
                    "operator": order["operator"],
                    "customer": order["customer"],
                    "service": order["service__name"],
                    "remarks": "<span>" + str(remarks_disc[order["id"]]) + "</span>"
                    if order["id"] in remarks_disc
                    else "<i class=icon-plus-circle title=Add-remarks style='font-size:13px; margin-left:0px;'></i> Add remarks",
                    "order_next_status": dict(order_status)[order["order_next_status"]] if order["order_next_status"] in dict(order_status) else " ",
                    "order_previous_status": dict(order_status)[order["order_previous_status"]] if order["order_previous_status"] in dict(order_status) else " ",
                    "order_status": order["order_status"],
                    "order_status_name": order_status_name[order["order_status"]] if order["order_status"] in order_status_name else None,
                    "customer_order_nr": order["customer_order_nr"],
                    "tool_nr": order["tool_nr"],
                    "layer": layers[order["layer"]] if order["layer"] in layers else None,
                    "board_thickness": order["board_thickness"],
                    "material_tg": dict(material_tg)[order["material_tg"]] if order["material_tg"] in dict(material_tg) else " ",
                    "bottom_solder_mask": dict(bottom_solder_mask)[order["bottom_solder_mask"]] if order["bottom_solder_mask"] in dict(bottom_solder_mask) else " ",
                    "top_solder_mask": dict(top_solder_mask)[order["top_solder_mask"]] if order["top_solder_mask"] in dict(top_solder_mask) else " ",
                    "top_legend": dict(top_legend)[order["top_legend"]] if order["top_legend"] in dict(top_legend) else " ",
                    "bottom_legend": dict(bottom_legend)[order["bottom_legend"]] if order["bottom_legend"] in dict(bottom_legend) else " ",
                    "surface_finish": dict(surface_finish)[order["surface_finish"]] if order["surface_finish"] in dict(surface_finish) else " ",
                    "in_time": Util.get_local_time(order["in_time"], True),
                    "panel_no": order["panel_no"],
                    "panel_qty": order["panel_qty"],
                    "order_status_code": order["order_status"] if order["order_status"] else "",
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def generate_exception_problem_save(request):
    try:
        with transaction.atomic():
            c_ip = base_views.get_client_ip(request)
            order_id = request.POST.get("order_id")
            action = AuditAction.INSERT
            pre_define_problem = request.POST.get("pre_defined_problem")
            order_status = Order.objects.filter(id=order_id).values("order_status", "order_number", "customer_order_nr").first()
            upload_image = request.FILES.get("upload_image")
            if upload_image is not None:
                upload_image_name = str(upload_image).split(".")
                upload_image_name = upload_image_name[0] + "_img" + "." + upload_image_name[1]
                upload_image_data = upload_image.read()
                upload_and_save_impersonate(
                    upload_image_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "EXCEPTION", upload_image_name, order_status["customer_order_nr"], ""
                )

            si_file = request.FILES.get("si_file")
            if si_file is not None:
                is_si_file = True
                si_file_name = str(si_file).split(".")
                si_file_name = si_file_name[0] + "_si" + "." + si_file_name[1]
                si_file_data = si_file.read()
                Order_Attachment.objects.filter(object_id=order_id, file_type__code="SI").update(deleted=True)
                upload_and_save_impersonate(si_file_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "SI", si_file_name, order_status["customer_order_nr"], "")
            else:
                is_si_file = False

            operator = Order.objects.filter(id=order_id).values("operator__user__username", "operator_id", "operator__shift", "user_id", "operator__user__id").first()
            auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on", "descr").last()
            process_start_time = auditlog["action_on"].replace(tzinfo=None)
            current_time = datetime.datetime.now()
            diff = current_time - process_start_time
            prep_time_ = diff.days * 86400 + diff.seconds
            exception_problems = PreDefineExceptionProblem.objects.filter(id=pre_define_problem).values("code").first()
            exception_pro = exception_problems["code"]
            internal_remark = request.POST.get("internal_remark") if exception_pro == "Internal Exception" else ""
            if exception_pro == "Pre-production approval":
                user_eff_exception = "ppa_exception"
            else:
                user_eff_exception = "exception"
            user_efficiency_log(request, order_id, prep_time_, user_eff_exception, "", "")
            reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
            login_time = reserved_order["logged_in_time"] if reserved_order else None
            ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
            is_active_operator = ActiveOperators.objects.filter(operator_id_id=operator["operator_id"])
            if len(is_active_operator) == 0:
                ActiveOperators.objects.create(operator_id_id=operator["operator_id"], logged_in_time=login_time, shift_id=operator["operator__shift"])
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.INSERT
            docnumber = DocNumber.objects.filter(code="Order_exception").first()
            order_exception = OrderException.objects.create(
                exception_nr=docnumber.nextnum,
                order_id=order_id,
                pre_define_problem_id=pre_define_problem,
                created_by_id=operator["operator__user__id"],
                order_status=order_status["order_status"],
                is_si_file=is_si_file,
                internal_remark=internal_remark,
            )
            docnumber.increase()
            docnumber.save()
            Order.objects.filter(id=order_id).update(order_status="exception", in_time=datetime.datetime.now(), operator=None)
            log_views.insert("pws", "OrderException", [order_exception.id], action, request.user.id, c_ip, "Exception generated on order")
            log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, "Exception generated on order")

            order_detail = (
                OrderException.objects.filter(id=order_exception.id)
                .values(
                    "order__company__name",
                    "order__company",
                    "order__order_number",
                    "order__customer_order_nr",
                    "order__pcb_name",
                    "order__layer",
                    "order__delivery_term",
                    "order__delivery_date",
                    "pre_define_problem__code",
                    "order_status",
                )
                .first()
            )
            email_id = (
                CompanyParameter.objects.filter(company=order_detail["order__company"])
                .values(
                    "ord_exc_gen_mail",
                    "gen_mail", "mail_from",
                    "ord_exc_rem_mail",
                    "int_exc_from",
                    "int_exc_to",
                    "int_exc_cc"
                ).first()
            )
            if order_detail["pre_define_problem__code"] == "Internal Exception":
                mail_from = email_id["int_exc_from"] if email_id["int_exc_from"] else settings.INTERNAL_EXCEPTION_FROM
                email_id_ = email_id["int_exc_to"] if email_id["int_exc_to"] else settings.INTERNAL_EXCEPTION_MAIL
                cc_mail = email_id["int_exc_cc"] if email_id["int_exc_cc"] else settings.INTERNAL_EXCEPTION_CC_MAIL
                subject = "Internal Exception #" + str(order_detail["order__customer_order_nr"]) + "."
                title = "Dear Concern, <br> Please check on below details and suggest us back asap : #" + str(order_detail["order__customer_order_nr"]) + "."
            else:
                mail_from = email_id["mail_from"] if email_id["mail_from"] else None
                email_id_ = email_id["ord_exc_gen_mail"]
                email_id_ = [email_ids for email_ids in email_id_.split(",")]
                user_cc_mail = CompanyUser.objects.filter(id=operator["user_id"]).values("user__email").first()
                cc_mail = user_cc_mail["user__email"] if user_cc_mail else ""
                subject = "Exception found during CAM work for " + str(order_detail["order__company__name"]) + " #" + str(order_detail["order__customer_order_nr"]) + "."
                title = "Following are the details of Queries observed during CAM work. Please check and reply for each point."
            layer = Layer.objects.filter(code=order_detail["order__layer"]).values("code", "name").first()
            if layer:
                layers = layer["name"]
            else:
                layers = ""
            order_status_name = OrderProcess.objects.filter(code=order_detail["order_status"]).values("code", "name").first()
            delivery_terms = dict(delivery_term)[order_detail["order__delivery_term"]] if order_detail["order__delivery_term"] in dict(delivery_term) else ""
            internal_remarks = OrderException.objects.filter(id=order_exception.id).values("internal_remark").first()
            internal_remark = internal_remarks["internal_remark"] if internal_remarks else None
            head = str(order_detail["order__company__name"]) + " #" + str(order_detail["order__customer_order_nr"]) + "."
            message = render_to_string(
                "pws/mail_order.html",
                {
                    "internal_remark": internal_remark,
                    "head": head,
                    "title": title,
                    "layers": layers,
                    "order_detail": order_detail,
                    "company_gen_mail": email_id,
                    "delivery_terms": delivery_terms,
                    "order_status_name": order_status_name["name"] if order_status_name is not None else "",
                },
            )
            mail_attachment = {}
            upload_image = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="EXCEPTION").values("url", "name", "uid").last()
            if upload_image:
                full_path = os.path.join(str(settings.FILE_SERVER_PATH), upload_image["url"])
                mail_attachment[upload_image["name"]] = full_path
            if order_exception.is_si_file:
                si_file = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="SI").values("url", "name", "uid").last()
                if si_file:
                    full_path = os.path.join(str(settings.FILE_SERVER_PATH), si_file["url"])
                    mail_attachment[si_file["name"]] = full_path
            if email_id_ != ['']:
                if order_detail["pre_define_problem__code"] == "Internal Exception":
                    email_to = [email_id_]
                else:
                    email_to = [*email_id_]
                send_mail(True, "public", email_to, subject, message, mail_attachment, [cc_mail], mail_from)
            response = {
                "code": 1,
                "msg": "Exception generated on order successfully",
                "exception_id": order_exception.id,
            }
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"exceptions": "exception"}])
def incomings_view(request, type):
    try:
        user = User.objects.get(id=request.user.id)
        perms = [
            "can_add_new_file",
            "view_file_history",
            "can_put_to_customer",
            "can_view_exception_files",
            "can_modify_exception",
            "can_send_reminder",
            "can_back_to_incoming",
            "can_send_back",
            "cancel_order_exception",
            "can_export_exception",
        ]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/incomings.html", {"type": type, "permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exceptions_search(request, status, id, type):
    try:
        query = Q()
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "order__layer":
            sort_col = "layer_column"
        if sort_col == "-order__layer":
            sort_col = "-layer_column"
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_com_ids = Operator.objects.filter(user__id=request_user_id["id"]).values("company_ids").first()
        if operator_com_ids:
            operator_role = UserGroup.objects.filter(user_id=request_user_id["id"]).values("group__name").first()
            if operator_role["group__name"] == "Engineer":
                if operator_com_ids["company_ids"]:
                    operator_com_ids = list(map(int, operator_com_ids["company_ids"].split(",")))
                    query.add(Q(order__company_id__in=operator_com_ids), query.connector)
                else:
                    query.add(Q(order__company_id=None), query.connector)
        if request.POST.get("exception_nr"):
            query.add(Q(exception_nr__icontains=request.POST["exception_nr"]), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order__order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("company"):
            query.add(Q(order__company__name__icontains=request.POST["company"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(order__service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(order__customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("order_status"):
            query.add(Q(order_status__icontains=request.POST["order_status"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(order__pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(order__layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("pre_define_problem"):
            query.add(Q(pre_define_problem__code__icontains=request.POST["pre_define_problem"]), query.connector)
        if request.POST.get("order_date") is not None:
            query.add(
                Q(
                    order__order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        if request.POST.get("pws_id"):
            query.add(Q(order__order_number__icontains=request.POST["pws_id"]), query.connector)
        if request.POST.get("created_on") is not None:
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        query.add(Q(order_in_exception=False), query.connector)
        query.add(Q(exception_status=status), query.connector)
        query.add(~Q(order__order_status="cancel"), query.connector)
        recordsTotal = OrderException.objects.filter(query).count()
        order_exceptions = (
            OrderException.objects.filter(query)
            .values(
                "id",
                "exception_nr",
                "order__order_number",
                "order__customer_order_nr",
                "order__company__name",
                "created_on",
                "order__service__name",
                "created_by__username",
                "order__remarks",
                "order__layer",
                "pre_define_problem__code",
                "pre_define_problem__description",
                "order_status",
                "order__pcb_name",
                "order__order_date",
                "order__id",
                "total_reminder",
                "order__customer_order_nr",
                "order__delivery_term",
                "order__delivery_date",
                "order__user_id",
                "exception_status"
            )
            .annotate(
                layer_column=Case(
                    When(order__layer__endswith=" L", then=(Cast(Replace("order__layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(order__layer__endswith=layer_code_gtn, then=(Cast(Replace("order__layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(order__layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            )
            .order_by(sort_col)[start : (start + length)]
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        remarks_list = [order_["order__id"] for order_ in order_exceptions]
        remarks = Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list).values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        order_ids = [order_exception["order__id"] for order_exception in order_exceptions]
        include_assemblies = OrderTechParameter.objects.filter(order__in=order_ids).values("order_id", "is_include_assembly")

        layers_code = [order_["order__layer"] for order_ in order_exceptions]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)

        order_status_code = [order_["order_status"] for order_ in order_exceptions]
        status = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), code__in=order_status_code).values("code", "name")
        order_status_name = Util.get_dict_from_quryset("code", "name", status)
        is_include_assembly = {}
        for assembly in include_assemblies:
            include_assembly = assembly["is_include_assembly"]
            if assembly["order_id"] in is_include_assembly:
                include_assembly = include_assembly + ", " + is_include_assembly[assembly["order_id"]]
            is_include_assembly[assembly["order_id"]] = include_assembly

        for order_exception in order_exceptions:
            is_assembly = ""
            if is_include_assembly[order_exception["order__id"]] if order_exception["order__id"] in is_include_assembly else "":
                is_assembly = "Yes"
            else:
                is_assembly = "No"
            mail_to_customer = CompanyParameter.objects.filter(company__name=order_exception["order__company__name"]).values("ord_exc_rem_mail").first()
            response["data"].append(
                {
                    "id": order_exception["id"],
                    "exception_nr": order_exception["exception_nr"],
                    "order__order_number": order_exception["order__order_number"],
                    "order__customer_order_nr": order_exception["order__customer_order_nr"] if order_exception["order__customer_order_nr"] is not None else None,
                    "mail_to_customer": mail_to_customer["ord_exc_rem_mail"],
                    "order__company": order_exception["order__company__name"],
                    "created_on": Util.get_local_time(order_exception["created_on"], True),
                    "order__service": order_exception["order__service__name"],
                    "created_by": order_exception["created_by__username"],
                    "order__layer": layers[order_exception["order__layer"]] if order_exception["order__layer"] in layers else None,
                    "include_assembly": is_assembly,
                    "pre_define_problem": order_exception["pre_define_problem__code"],
                    "order__remarks": "<span>" + str(remarks_disc[order_exception["order__id"]]) + "</span>" if order_exception["order__id"] in remarks_disc else "",
                    "report_builder": "",
                    "order_status": order_status_name[order_exception["order_status"]] if order_exception["order_status"] in order_status_name else None,
                    "order_status_code": order_exception["order_status"],
                    "order__pcb_name": order_exception["order__pcb_name"],
                    "order__order_date": Util.get_local_time(order_exception["order__order_date"], True),
                    "order__id": order_exception["order__id"],
                    "pre_define_problem_des": order_exception["pre_define_problem__description"],
                    "total_reminder": order_exception["total_reminder"],
                    "order__delivery_term": dict(delivery_term)[order_exception["order__delivery_term"]] if order_exception["order__delivery_term"] in dict(delivery_term) else "",
                    "order__delivery_date": Util.get_local_time(order_exception["order__delivery_date"], True),
                    "exception_status": order_exception["exception_status"],
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def put_to_customer(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_put_to_customer", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_exception_id = request.POST.get("order_exception_id")
            order_id = request.POST.get("order_id")
            put_to_customer_by = request.user.id
            OrderException.objects.filter(id=order_exception_id).update(
                exception_status="put_to_customer",
                put_to_customer_date=datetime.datetime.now(),
                put_to_customer_by=put_to_customer_by
            )
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            log_views.insert("pws", "OrderException", [order_exception_id], action, request.user.id, c_ip, "Exception sent to Customer.")
            log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, "Exception sent to Customer.")
            return HttpResponse(AppResponse.msg(1, str("Exception move to put to Customer stage successfully ")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def back_to_in_coming(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_back_to_incoming", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_exception_id = request.POST.get("order_exception_id")
            order_id = request.POST.get("order_id")
            OrderException.objects.filter(id=order_exception_id).update(exception_status="in_coming")
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            log_views.insert("pws", "OrderException", [order_exception_id], action, request.user.id, c_ip, "Exception Order back to the in-coming stage.")
            log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, "Exception Order back to the in-coming stage.")
            return HttpResponse(AppResponse.msg(1, str("Order sent back to the Exception in coming stage.")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_reminder(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_send_reminder", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_exception_id = request.POST.get("order_exception_id")
            total_reminder = request.POST.get("total_reminder")
            order_id = request.POST.get("order_id")
            if total_reminder == "":
                total_reminder_count = 1
            else:
                total_reminder_count = int(total_reminder) + 1
            order_detail = (
                OrderException.objects.filter(id=order_exception_id)
                .values(
                    "order__company__name",
                    "order__company",
                    "order__order_number",
                    "order__customer_order_nr",
                    "order__pcb_name",
                    "order__layer",
                    "order__delivery_term",
                    "order__delivery_date",
                    "pre_define_problem__code",
                    "order_status",
                )
                .first()
            )

            is_si_file = OrderException.objects.filter(id=order_exception_id).values("is_si_file", "order__user_id", "internal_remark").first()
            internal_remark = is_si_file["internal_remark"] if is_si_file else None
            email_id = (
                CompanyParameter.objects.filter(company=order_detail["order__company"])
                .values("ord_exc_gen_mail", "gen_mail", "ord_exc_rem_mail", "mail_from", "int_exc_from", "int_exc_to", "int_exc_cc").first()
            )
            mail_from = email_id["mail_from"] if email_id["mail_from"] else None
            if order_detail["pre_define_problem__code"] == "Internal Exception":
                mail_from = email_id["int_exc_from"] if email_id["int_exc_from"] else settings.INTERNAL_EXCEPTION_FROM
                email_id_ = email_id["int_exc_to"] if email_id["int_exc_to"] else settings.INTERNAL_EXCEPTION_MAIL
                cc_mail = email_id["int_exc_cc"] if email_id["int_exc_cc"] else settings.INTERNAL_EXCEPTION_CC_MAIL
                subject = "Internal Exception #" + str(order_detail["order__customer_order_nr"]) + "."
                title = "Dear Concern,<br>Please check on below details and suggest us back asap : #" + str(order_detail["order__customer_order_nr"]) + "."
            else:
                email_id_ = email_id["ord_exc_rem_mail"]
                cc_mail_ = CompanyUser.objects.filter(id=is_si_file["order__user_id"]).values("user__email").first()
                cc_mail = None
                if cc_mail_:
                    cc_mail = cc_mail_["user__email"]
                subject = "Reminder: Exception found during CAM work for " + order_detail["order__company__name"] + " #" + order_detail["order__customer_order_nr"] + "."
                title = "During order processing, a problem occurred in the order. Following are order and problem details of the order."
            if email_id_ or order_detail["pre_define_problem__code"] == "Internal Exception":
                email_id_ = [email_ids for email_ids in email_id_.split(",")]
                layer = Layer.objects.filter(code=order_detail["order__layer"]).values("code", "name").first()
                if layer:
                    layers = layer["name"]
                else:
                    layers = ""
                order_status_name = OrderProcess.objects.filter(code=order_detail["order_status"]).values("code", "name").first()
                delivery_terms = dict(delivery_term)[order_detail["order__delivery_term"]] if order_detail["order__delivery_term"] in dict(delivery_term) else ""
                head = order_detail["order__company__name"] + " #" + order_detail["order__customer_order_nr"] + "."
                company_gen_mail = CompanyParameter.objects.filter(company=order_detail["order__company"]).values("gen_mail", "is_send_attachment", "is_exp_file_attachment").first()
                message = render_to_string(
                    "pws/mail_order.html",
                    {
                        "internal_remark": internal_remark,
                        "head": head,
                        "title": title,
                        "layers": layers,
                        "order_detail": order_detail,
                        "company_gen_mail": company_gen_mail,
                        "delivery_terms": delivery_terms,
                        "order_status_name": order_status_name["name"] if order_status_name is not None else "",
                    },
                )
                message_ = Order.objects.filter(id=order_id).values("mail_messages").first()
                if order_detail["pre_define_problem__code"] == "Internal Exception":
                    if message_['mail_messages']:
                        if message_['mail_messages']['exceptionId'] == int(order_exception_id):
                            if message_['mail_messages']['exceptionProb'] == "Internal Exception":
                                email_id_ = [message_['mail_messages']['toMail']]
                                cc_mail = message_['mail_messages']['ccMail']
                                subject = "Reminder :" + message_['mail_messages']['subject']
                                message = message_['mail_messages']['message']
                mail_attachment = {}
                if company_gen_mail["is_exp_file_attachment"]:
                    upload_image = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="EXCEPTION").values("url", "name", "uid").last()
                    if upload_image:
                        full_path = os.path.join(str(settings.FILE_SERVER_PATH), upload_image["url"])
                        mail_attachment[upload_image["name"]] = full_path

                if company_gen_mail["is_send_attachment"]:
                    if is_si_file["is_si_file"]:
                        si_file = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="SI").values("url", "name", "uid").last()
                        if si_file:
                            full_path = os.path.join(str(settings.FILE_SERVER_PATH), si_file["url"])
                            mail_attachment[si_file["name"]] = full_path

                send_mail(True, "public", [*email_id_], subject, message, mail_attachment, [cc_mail], mail_from)
            else:
                response = {"code": 0, "msg": "Exception mail to customer is not available."}
                return HttpResponse(AppResponse.get(response), content_type="json")
            OrderException.objects.filter(id=order_exception_id).update(total_reminder=total_reminder_count, last_reminder_date=datetime.datetime.now())
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            log_views.insert("pws", "OrderException", [order_exception_id], action, request.user.id, c_ip, "Exception reminder sent")
            log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, "Exception reminder sent")
            response = {"code": 1, "msg": "Exception reminder sent successfully"}
            return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_exception(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_exception", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_com_ids = Operator.objects.filter(user__id=request_user_id["id"]).values("company_ids").first()
        if operator_com_ids:
            operator_role = UserGroup.objects.filter(user_id=request_user_id["id"]).values("group__name").first()
            if operator_role["group__name"] == "Engineer":
                if operator_com_ids["company_ids"]:
                    operator_com_ids = list(map(int, operator_com_ids["company_ids"].split(",")))
                    query.add(Q(order__company_id__in=operator_com_ids), query.connector)
                else:
                    query.add(Q(order__company_id=None), query.connector)
        if request.POST.get("exception_nr"):
            query.add(Q(exception_nr__icontains=request.POST["exception_nr"]), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order__order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("company"):
            query.add(Q(order__company__name__icontains=request.POST["company"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(order__service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(order__customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("order_status"):
            query.add(Q(order_status__icontains=request.POST["order_status"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(order__pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(order__layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("order_date"):
            query.add(
                Q(
                    order__order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        if request.POST.get("pws_id"):
            query.add(Q(order__order_number__icontains=request.POST["pws_id"]), query.connector)
        if request.POST.get("created_on"):
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        if request.POST.get("pre_define_problem"):
            query.add(Q(pre_define_problem__code__icontains=request.POST["pre_define_problem"]), query.connector)
        query.add(Q(order_in_exception=False), query.connector)
        query.add(Q(exception_status=request.POST.get("status")), query.connector)
        query.add(~Q(order__order_status="cancel"), query.connector)
        order_exceptions = OrderException.objects.filter(query).values(
            "exception_nr",
            "order__order_number",
            "order__customer_order_nr",
            "order__company__name",
            "created_on",
            "order__service__name",
            "order__remarks",
            "created_by__username",
            "order__layer",
            "order__pcb_name",
            "order__delivery_term",
            "order__delivery_date",
            "pre_define_problem__code",
            "order__id",
            "order_status",
            "total_reminder",
        ).annotate(
            layer_column=Case(
                When(order__layer__endswith=" L", then=(Cast(Replace("order__layer", Value(" L"), Value("")), output_field=IntegerField()))),
                When(order__layer__endswith=layer_code_gtn, then=(Cast(Replace("order__layer", Value("L"), Value("")), output_field=IntegerField()))),
                When(order__layer="", then=None),
                default=None,
                output_field=IntegerField(),
            )
        ).order_by(order_by)[start : (start + length)]
        remarks_list = [order_["order__id"] for order_ in order_exceptions]
        remarks = Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list).values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        query_result = []

        order_ids = [order_exception["order__id"] for order_exception in order_exceptions]
        include_assemblies = OrderTechParameter.objects.filter(order__in=order_ids).values("order_id", "is_include_assembly")

        layer_codes = [order["order__layer"] for order in order_exceptions if order["order__layer"]]
        layer = Layer.objects.filter(code__in=layer_codes).values("name", "code")
        layers_ = Util.get_dict_from_quryset("code", "name", layer)

        order_status_code = [order_["order_status"] for order_ in order_exceptions]
        status = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), code__in=order_status_code).values("code", "name")
        order_status_name = Util.get_dict_from_quryset("code", "name", status)
        is_include_assembly = {}
        for assembly in include_assemblies:
            include_assembly = assembly["is_include_assembly"]
            if assembly["order_id"] in is_include_assembly:
                include_assembly = include_assembly + ", " + is_include_assembly[assembly["order_id"]]
            is_include_assembly[assembly["order_id"]] = include_assembly

        for exception in order_exceptions:
            is_assembly = ""
            if is_include_assembly[exception["order__id"]] if exception["order__id"] in is_include_assembly else "":
                is_assembly = "Yes"
            else:
                is_assembly = "No"
            query_result.append(
                {
                    "exception_number": exception["exception_nr"],
                    "order__order_number": exception["order__order_number"],
                    "order__customer_order_nr": exception["order__customer_order_nr"],
                    "order__company__name": exception["order__company__name"],
                    "created_on": Util.get_local_time(exception["created_on"], True),
                    "order__service__name": exception["order__service__name"],
                    "created_by__username": exception["created_by__username"],
                    "order__layer": layers_[exception["order__layer"]] if exception["order__layer"] in layers_ else None,
                    "include_assembly": is_assembly,
                    "order__pcb_name": exception["order__pcb_name"],
                    "order__delivery_term": dict(delivery_term)[exception["order__delivery_term"]] if exception["order__delivery_term"] in dict(delivery_term) else "",
                    "order__delivery_date": Util.get_local_time(exception["order__delivery_date"], True),
                    "pre_define_problem__code": exception["pre_define_problem__code"],
                    "order__remarks": BeautifulSoup(remarks_disc[exception["order__id"]], features="html5lib").get_text() if exception["order__id"] in remarks_disc else "",
                    "order_status": order_status_name[exception["order_status"]] if exception["order_status"] in order_status_name else None,
                }
            )
        headers = [
            {"title": "Exception number"},
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Customer name"},
            {"title": "Exception Date"},
            {"title": "Service"},
            {"title": "Created by"},
            {"title": "Layers"},
            {"title": "Include Assembly"},
            {"title": "PCB name"},
            {"title": "Delivery term"},
            {"title": "Delivery date"},
            {"title": "Problem statement"},
            {"title": "Remarks"},
            {"title": "Origin of problem"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "OrderException.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def modify_exception(request):
    try:
        exception_id = request.POST.get("orderExceptionId")
        order_exception = (
            OrderException.objects.filter(id=exception_id)
            .values("id", "order__id", "order__order_number", "order__customer_order_nr", "order_status", "pre_define_problem__id", "created_on", "is_si_file", "internal_remark")
            .first()
        )
        order_exception["order_status"] = dict(order_status)[order_exception["order_status"]] if order_exception["order_status"] in dict(order_status) else ""
        exception_files = uploadExceptionFile(order_exception["order__id"], order_exception["is_si_file"])
        return render(
            request,
            "pws/modify_exception.html",
            {
                "order_exception": order_exception,
                "upload_image": exception_files[0],
                "si_file": exception_files[1],
            },
        )
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def modify_exception_save(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_modify_exception", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_id = request.POST.get("order_id")
            order_exception = request.POST.get("order_exception")
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            pre_define_problem = request.POST.get("pre_defined_problem")
            order_status = Order.objects.filter(id=order_id).values("order_status", "order_number", "customer_order_nr").first()

            upload_image = request.FILES.get("upload_image")
            if upload_image is not None:
                if not Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="EXCEPTION", name=upload_image).exists():
                    if len(str(upload_image)) > 170:
                        return HttpResponse(AppResponse.msg(0, str("Exception File name is too long.")), content_type="json")
                    upload_image_name = str(upload_image).split(".")
                    upload_image_name = upload_image_name[0] + "_img" + "." + upload_image_name[1]
                    upload_image_data = upload_image.read()
                    Order_Attachment.objects.filter(object_id=order_id, file_type__code="EXCEPTION").update(deleted=True)
                    upload_and_save_impersonate(
                        upload_image_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "EXCEPTION", upload_image_name, order_status["customer_order_nr"], ""
                    )

            si_file = request.FILES.get("si_file")
            if si_file is not None:
                is_si_file = True
                if not Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="SI", name=si_file).exists():
                    if len(str(si_file)) > 170:
                        return HttpResponse(AppResponse.msg(0, str("SI File name is too long.")), content_type="json")
                    si_file_name = str(si_file).split(".")
                    si_file_name = si_file_name[0] + "_si" + "." + si_file_name[1]
                    si_file_data = si_file.read()
                    Order_Attachment.objects.filter(object_id=order_id, file_type__code="SI").update(deleted=True)
                    upload_and_save_impersonate(si_file_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "SI", si_file_name, order_status["customer_order_nr"], "")
            else:
                is_si_file = False
            exception_problems = PreDefineExceptionProblem.objects.filter(id=pre_define_problem).values("code").first()
            internal_remark = request.POST.get("internal_remark") if exception_problems["code"] == "Internal Exception" else ""
            OrderException.objects.filter(id=order_exception).update(pre_define_problem_id=pre_define_problem, is_si_file=is_si_file, internal_remark=internal_remark)
            log_views.insert("pws", "Order", [str(order_id)], action, request.user.id, c_ip, "Order exception has been updated.")
            log_views.insert("pws", "OrderException", [order_exception], action, request.user.id, c_ip, "Order exception has been updated.")
            return HttpResponse(AppResponse.msg(1, str("Order exception has been updated.")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exception_details(request):
    try:
        exception_id = request.POST.get("orderExceptionId")
        order_exception = (
            OrderException.objects.filter(id=exception_id)
            .values(
                "id", "order__id",
                "order__order_number",
                "order__customer_order_nr",
                "order__order_date",
                "order_status",
                "pre_define_problem__code",
                "is_si_file",
                "internal_remark"
            )
            .first()
        )
        order_exception["order_status"] = dict(order_status)[order_exception["order_status"]] if order_exception["order_status"] in dict(order_status) else ""
        exception_files = uploadExceptionFile(order_exception["order__id"], order_exception["is_si_file"])
        return render(
            request,
            "pws/exception_details.html",
            {
                "order_exception": order_exception,
                "upload_image": exception_files[0],
                "si_file": exception_files[1],
            },
        )
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def uploadExceptionFile(id, is_si_file):
    upload_image = Order_Attachment.objects.filter(object_id=id, deleted=False, file_type__code="EXCEPTION").values("url", "name", "uid").last()
    if is_si_file:
        si_file = Order_Attachment.objects.filter(object_id=id, deleted=False, file_type__code="SI").values("url", "name", "uid").last()
    else:
        si_file = None
    return upload_image, si_file


def order_remark_save(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_send_back", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        order_exception = request.POST.get("order_exception_id")
        order_status = request.POST.get("order_status")
        order_id = request.POST.get("order_id")
        model_remark_field = "remarks"
        remarks_back = request.POST.get("remarks_back")
        remarks_type_back = request.POST.get("remarks_type_back")
        action = AuditAction.INSERT
        c_ip = base_views.get_client_ip(request)
        send_back_by = request.user.id
        if order_id is not None:
            Order.objects.filter(id=order_id).update(order_status=order_status, in_time=datetime.datetime.now())
            Order_Attachment.objects.filter(object_id=order_id, file_type__code="EXCEPTION").update(deleted=True)
            OrderException.objects.filter(id=order_exception).update(order_in_exception=True, send_back_date=datetime.datetime.now(), send_back_by=send_back_by)
            base_views.create_remark("pws", "order", order_id, remarks_back, "", request.user.id, model_remark_field, remarks_type_back, "", "")
        log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, "Exception order sent back to process")
        log_views.insert("pws", "orderexception", [order_exception], action, request.user.id, c_ip, "Exception order sent back to process")
        return HttpResponse(AppResponse.msg(1, str("Exception order sent back to process successfully.")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_engineers_work": "engineers_work_report"}])
def engineers_work_report_view(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_generate_report", "can_export_engineers_work_report", "can_save_preptime"]
        permissions = Util.get_permission_role(user, perms)
        company_id = Company.objects.filter(is_deleted=False, is_active=True).values("id").first()
        planet_engineer = "No"
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("id", "operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    planet_engineer = "Yes"
        context = {"planet_engineer": planet_engineer, "operator_id": operator_id["id"], "company_id": company_id["id"], "permissions": json.dumps(permissions)}
        return render(request, "pws/reports/engineers_work_report.html", context)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"compare_orders": "compare_orders"}])
def compare_orders(request, type):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_import_order"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/reports/compare_orders.html", {"type": type, "permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def compare_orders_search(request, status, id, type):
    try:
        customer_order_no = request.POST.get("customer_order_nr")
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        query = Q()
        request.POST = Util.get_post_data(request)
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "layer":
            sort_col = "layer_column"
        if sort_col == "-layer":
            sort_col = "-layer_column"
        if request.POST.get("customer"):
            query.add(Q(company__name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("ecc_status"):
            query.add(Q(order_status__icontains=request.POST["ecc_status"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("pre_due_date") is not None:
            query.add(
                Q(
                    preparation_due_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("pre_due_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("pre_due_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        if request.POST.get("order_date") is not None:
            query.add(
                Q(
                    order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        query.add(Q(import_order_date__isnull=False), query.connector)
        if status == "ec_pending":
            pws_service = PWSEcPyService()
            ec_response = pws_service.get_ecc({}, "/ecpy/pws/import_pending_orders_from_ec")[0:20]
            if customer_order_no:
                ec_response = pws_service.get_ecc({"customer_order_nr": customer_order_no}, "/ecpy/pws/import_pending_orders_from_ec")
            response = {"draw": request.POST["draw"], "data": []}
            index = 1
            for order in ec_response:
                response["data"].append(
                    {
                        "id": index,
                        "order_date": Util.get_local_time(datetime.datetime.strptime(order["OrderDate"], "%d %b %Y %H:%M:%S"), True),
                        "customer": order["Customer Name"],
                        "service": order["Service"],
                        "cus_order_no": order["OrderNumber"],
                        "ecc_status": order["CurrentStatus"],
                        "layer": order["Layers"] + " Layer" if order["Layers"] is not None else "",
                        "pcb_name": order["Board Name"],
                        "pre_due_date": Util.get_local_time(datetime.datetime.strptime(order["PreDueDate"], "%d %b %Y %H:%M:%S"), True) if order["PreDueDate"] is not None else "",
                    }
                )
                index += 1
            return HttpResponse(AppResponse.get(response), content_type="json")
        elif status == "power_pending":
            url = settings.PPM_URL + "/pwsAPI/GetOrders?type=orderall"
            if customer_order_no:
                url = settings.PPM_URL + f"/pwsAPI/GetOrders?type=order&OrderNr={customer_order_no}"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            ec_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            response = {"draw": request.POST["draw"], "data": []}
            data = None
            try:
                data = ec_res.json()[0:20]
            except Exception:
                return HttpResponse(AppResponse.get(response), content_type="json")
            index = 1
            if data:
                for order in data:
                    response["data"].append(
                        {
                            "id": index,
                            "order_date": order["OrderDate"],
                            "customer": order["Customer Name"],
                            "service": order["Service"],
                            "cus_order_no": order["OrderNumber"],
                            "ecc_status": order["CurrentStatus"],
                            "layer": str(order["Layers"]) + " Layer" if order["Layers"] is not None else "",
                            "pcb_name": order["Board Name"],
                            "pre_due_date": order["PreDueDate"],
                        }
                    )
                    index += 1
            return HttpResponse(AppResponse.get(response), content_type="json")

        elif status == "power_inq_pending":
            url = settings.PPM_URL + "/pwsAPI/GetOrders?type=inqall"
            if customer_order_no:
                url = settings.PPM_URL + f"/pwsAPI/GetOrders?type=inq&OrderNr={customer_order_no}"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            ec_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            response = {"draw": request.POST["draw"], "data": []}
            data = None
            try:
                data = ec_res.json()[0:20]
            except Exception:
                return HttpResponse(AppResponse.get(response), content_type="json")
            index = 1
            for order in data:
                response["data"].append(
                    {
                        "id": index,
                        "order_date": order["OrderDate"],
                        "customer": order["Customer Name"],
                        "service": order["Service"],
                        "cus_order_no": order["OrderNumber"],
                        "ecc_status": order["CurrentStatus"],
                        "layer": str(order["Layers"]) + " Layer" if order["Layers"] is not None else "",
                        "pcb_name": order["Board Name"],
                        "pre_due_date": order["PreDueDate"],
                    }
                )
                index += 1
            return HttpResponse(AppResponse.get(response), content_type="json")

        elif status == "ec_inq_pending":
            pws_service = PWSEcPyService()
            ec_response = pws_service.get_ecc({}, "/ecpy/pws/import_inq_from_ecc")[0:20]
            if customer_order_no:
                ec_response = pws_service.get_ecc({"customer_order_nr": customer_order_no}, "/ecpy/pws/import_inq_from_ecc")
            response = {"draw": request.POST["draw"], "recordsTotal": "", "recordsFiltered": "", "data": []}
            index = 1
            for order in ec_response:
                response["data"].append(
                    {
                        "id": index,
                        "order_date": order["OrderDate"],
                        "customer": order["Customer Name"],
                        "service": order["Service"],
                        "cus_order_no": order["OrderNumber"],
                        "ecc_status": order["CurrentStatus"],
                        "layer": order["Layers"] + " Layer" if order["Layers"] is not None else "",
                        "pcb_name": order["PCBName"],
                        "pre_due_date": order["PrepDueDate"] if order["PrepDueDate"] is not None else "",
                    }
                )
                index += 1
            return HttpResponse(AppResponse.get(response), content_type="json")

        elif status == "ec_compare":
            sort_col_ = ["pws_status", "-pws_status"]
            if sort_col == "-cus_order_no":
                sort_col = "-number"
            if sort_col == "cus_order_no":
                sort_col = "number"
            order_status_ = ["ECINQ", "ECORDERS"]
            query_ = Q()
            query_.add(Q(import_from__in=order_status_), query.connector)
            ec_compare_order = (
                CompareData.objects.filter(query_).values("id", "number", "order_status", "import_from", "compared_on").order_by(sort_col if sort_col not in sort_col_ else "id")
            )
            if customer_order_no:
                query_.add(Q(number__icontains=customer_order_no), query.connector)
                ec_compare_order = (
                    CompareData.objects.filter(query_).values("id", "number", "order_status", "import_from", "compared_on").order_by(sort_col if sort_col not in sort_col_ else "id")
                )
            total_data = CompareData.objects.filter(query_).values("id")
            response = {"draw": request.POST["draw"], "recordsTotal": len(total_data), "recordsFiltered": len(total_data), "data": []}
            order_data = Order.objects.values("customer_order_nr", "order_status")
            index = 1
            for order in ec_compare_order:
                order_sta = {
                    "pws_status" : str(ord["order_status"]) for ord in order_data if str(ord["customer_order_nr"]) == str(order["number"]) and ord["order_status"] is not None
                }
                response["data"].append(
                    {
                        "id" : index,
                        "cus_order_no" : order["number"],
                        "order_status" : order["order_status"],
                        "import_from" : order["import_from"],
                        "compared_on" : Util.get_local_time(order["compared_on"], True),
                        "pws_status" : dict(order_status)[order_sta["pws_status"]] if bool(order_sta) is True and order_sta["pws_status"] in dict(order_status) else "",
                    }
                )
                index += 1
            sort_col_asc = ["pws_status"]
            sort_col_desc = ["-pws_status"]
            if sort_col in sort_col_desc:
                response["data"] = sorted(response["data"], key=lambda i: i[sort_col[1:]], reverse=True)
            if sort_col in sort_col_asc:
                response["data"] = sorted(response["data"], key=lambda i: i[sort_col])
            response["data"] = response["data"][start : (start + length)]
            return HttpResponse(AppResponse.get(response), content_type="json")

        elif status == "power_compare":
            sort_col_ = ["pws_status", "-pws_status"]
            if sort_col == "-cus_order_no":
                sort_col = "-number"
            if sort_col == "cus_order_no":
                sort_col = "number"
            order_status_ = ["POWERINQ", "POWERORD"]
            query_ = Q()
            query_.add(Q(import_from__in=order_status_), query.connector)
            power_compare_order = (
                CompareData.objects.filter(query_).values("id", "number", "order_status", "import_from", "compared_on").order_by(sort_col if sort_col not in sort_col_ else "id")
            )
            if customer_order_no:
                query_.add(Q(number__icontains=customer_order_no), query.connector)
                power_compare_order = (
                    CompareData.objects.filter(query_).values("id", "number", "order_status", "import_from", "compared_on").order_by(sort_col if sort_col not in sort_col_ else "id")
                )
            total_recordes = CompareData.objects.filter(query_).values("id")
            response = {"draw": request.POST["draw"], "recordsTotal": len(total_recordes), "recordsFiltered": len(total_recordes), "data": []}
            order_data = Order.objects.values("customer_order_nr", "order_status")
            index = 1
            for order in power_compare_order:
                order_sta = {
                    "pws_status" : str(ord["order_status"]) for ord in order_data if str(ord["customer_order_nr"]) == str(order["number"]) and ord["order_status"] is not None
                }
                response["data"].append(
                    {
                        "id" : index,
                        "cus_order_no" : order["number"],
                        "order_status" : order["order_status"],
                        "import_from" : order["import_from"],
                        "compared_on" : Util.get_local_time(order["compared_on"], True),
                        "pws_status" : dict(order_status)[order_sta["pws_status"]] if bool(order_sta) is True and order_sta["pws_status"] in dict(order_status) else "",
                    }
                )
                index += 1
            sort_col_asc = ["pws_status"]
            sort_col_desc = ["-pws_status"]
            if sort_col in sort_col_desc:
                response["data"] = sorted(response["data"], key=lambda i: i[sort_col[1:]], reverse=True)
            if sort_col in sort_col_asc:
                response["data"] = sorted(response["data"], key=lambda i: i[sort_col])
            response["data"] = response["data"][start : (start + length)]
            return HttpResponse(AppResponse.get(response), content_type="json")

        else:
            imported_orders = (
                Order.objects.filter(query)
                .values("id", "order_date", "company__name", "service__name", "customer_order_nr", "layer", "pcb_name", "preparation_due_date", "order_status", "import_order_date")
                .annotate(
                    layer_column=Case(
                        When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                        When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                        When(layer="", then=None),
                        default=None,
                        output_field=IntegerField(),
                    ),
                )
                .order_by(sort_col, "-import_order_date")[0:20]
            )
            layers = [order["layer"] for order in imported_orders if order["layer"]]
            layer_ = Layer.objects.filter(code__in=layers).values("name", "code")
            layers_ = {}
            for layer_ in layer_:
                layers_[layer_["code"]] = layer_["name"]
            response = {"draw": request.POST["draw"], "recordsTotal": "", "recordsFiltered": "", "data": []}
            index = 1
            for order in imported_orders:
                response["data"].append(
                    {
                        "id": index,
                        "order_date": Util.get_local_time(order["order_date"], True),
                        "company": order["company__name"],
                        "service": order["service__name"],
                        "customer_order_nr": order["customer_order_nr"],
                        "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "",
                        "layer": layers_[order["layer"]] if order["layer"] in layers_ else "",
                        "pcb_name": order["pcb_name"],
                        "preparation_due_date": Util.get_local_time(order["preparation_due_date"], True),
                        "import_order_date": Util.get_local_time(order["import_order_date"], True),
                    }
                )
                index += 1
            return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"nc_details": "pws_detail_master"}])
def nc_details(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["add_new_nc_detail", "edit_nc_detail", "can_export_nc_details_master"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/nc_details.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiencies_search(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)

        if request.POST.get("company"):
            query.add(Q(company__name__icontains=request.POST["company"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("process"):
            query.add(Q(process__name__icontains=request.POST["process"]), query.connector)
        if request.POST.get("layer"):
            query.add(Q(layer__icontains=request.POST["layer"]), query.connector)
        if request.POST.get("multi_layer"):
            query.add(Q(multi_layer__icontains=request.POST["multi_layer"]), query.connector)
        query.add(Q(is_deleted=False), query.connector)
        user_efficiencies = (
            Efficiency.objects.filter(query).values("id", "company__name", "service__name", "process__name", "layer", "multi_layer").order_by(sort_col)[start : (start + length)]
        )
        recordsTotal = Efficiency.objects.filter(query).count()
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for user_efficiency in user_efficiencies:
            response["data"].append(
                {
                    "id": user_efficiency["id"],
                    "company__name": user_efficiency["company__name"],
                    "service__name": user_efficiency["service__name"],
                    "process__name": user_efficiency["process__name"],
                    "layer": user_efficiency["layer"],
                    "multi_layer": user_efficiency["multi_layer"],
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_user_efficiency(request):
    try:
        with transaction.atomic():
            company = request.POST.get("company")
            service = request.POST.get("service")
            process = request.POST.get("process")
            layer = request.POST.get("layer")
            multi_layer = request.POST.get("multi_layer")
            user_efficiencies_id = request.POST.get("user_efficiencies_id")

            c_ip = base_views.get_client_ip(request)
            layer = layer if layer else 0
            multi_layer = multi_layer if multi_layer else 0
            if user_efficiencies_id:
                user = User.objects.get(id=request.user.id)
                if Util.has_perm("edit_user_efficiency", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                if not Efficiency.objects.filter(company_id=company, service_id=service, process_id=process, is_deleted=False).exclude(id=user_efficiencies_id).exists():
                    Efficiency.objects.filter(id=user_efficiencies_id).update(company_id=company, service_id=service, process_id=process, layer=layer, multi_layer=multi_layer)
                    response = {"code": 1, "msg": "User efficiency has been updated."}
                    action = AuditAction.UPDATE
                    log_views.insert(
                        "pws",
                        "Efficiency",
                        [user_efficiencies_id],
                        action,
                        request.user.id,
                        c_ip,
                        "User efficiency details update.",
                    )
                else:
                    response = {"code": 0, "msg": "User efficiency is already exists."}
            else:
                user = User.objects.get(id=request.user.id)
                if Util.has_perm("add_new_user_efficiency", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                if not Efficiency.objects.filter(company_id=company, service_id=service, process_id=process, is_deleted=False).exists():
                    user_efficiencies = Efficiency.objects.create(company_id=company, service_id=service, process_id=process, layer=layer, multi_layer=multi_layer)
                    user_efficiencies_id = user_efficiencies.id
                    response = {"code": 1, "msg": "User efficiency has been created.", "user_efficiencies_id": user_efficiencies_id}
                    action = AuditAction.INSERT
                    log_views.insert(
                        "pws",
                        "Efficiency",
                        [user_efficiencies_id],
                        action,
                        request.user.id,
                        c_ip,
                        "User efficiency has been created",
                    )
                else:
                    response = {"code": 0, "msg": "User efficiency is already exists."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiencies_delete(request):
    try:
        with transaction.atomic():
            if Util.has_perm("delete_user_efficiency", request.user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            else:
                user_efficiencies_ids_list = []
                user_efficiencies_ids = request.POST.get("ids")
                for user_efficiencies_id in user_efficiencies_ids.split(","):
                    user_efficiencies_ids_list.append(user_efficiencies_id)
                Efficiency.objects.filter(id__in=user_efficiencies_ids_list).update(is_deleted=True)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.DELETE
                log_views.insert("pws", "Efficiency", user_efficiencies_ids.split(","), action, request.user.id, c_ip, "User efficiency has been deleted")
                response = {"code": 1, "msg": "User efficiency has been deleted."}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiency(request):
    id = request.POST.get("id")
    user_efficiency = None
    if id != "0":
        user_efficiency = Efficiency.objects.filter(id=id).values("id", "company_id", "service_id", "process_id", "layer", "multi_layer", "service__name").first()
    con = {"user_efficiency": user_efficiency}
    return render(request, "pws/user_efficiency.html", con)


def import_order_view(request):
    return render(request, "pws/import_order.html")


def batch_code_view(request):
    return render(request, "pws/batch_code.html")


def nc_details_search(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)

        if request.POST.get("name"):
            query.add(Q(name__icontains=request.POST["name"]), query.connector)
        if request.POST.get("created_by"):
            query.add(Q(created_by__username__icontains=request.POST["created_by"]), query.connector)
        if request.POST.get("created_on") is not None:
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        query.add(Q(is_deleted=False), query.connector)
        recordsTotal = NcCategory.objects.filter(query).count()
        nc_details = NcCategory.objects.filter(query).values("id", "name", "parent_id__name", "created_by__username", "created_on").order_by(sort_col)[start : (start + length)]
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for nc_detail in nc_details:
            response["data"].append(
                {
                    "id": nc_detail["id"],
                    "name": nc_detail["name"],
                    "parent_id": nc_detail["parent_id__name"],
                    "created_by": nc_detail["created_by__username"],
                    "created_on": Util.get_local_time(nc_detail["created_on"], True),
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def nc_detail(request):
    try:
        id = request.POST.get("id")
        nc_detail = None
        if id != "0":
            nc_detail = NcCategory.objects.filter(id=id).values("id", "name", "parent_id_id").first()
        con = {"nc_detail": nc_detail}
        return render(request, "pws/nc_detail.html", con)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_nc_detail(request):
    try:
        with transaction.atomic():
            category_name = request.POST.get("category_name")
            nc_detail_id = request.POST.get("nc_detail_id")
            checkbox = request.POST.get("check")
            if checkbox == "check":
                main_category = request.POST.get("main_category")
            else:
                main_category = None
            c_ip = base_views.get_client_ip(request)

            if nc_detail_id:
                user = User.objects.get(id=request.user.id)
                if Util.has_perm("edit_nc_detail", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                NcCategory.objects.filter(id=nc_detail_id).update(name=category_name, parent_id_id=main_category, created_by=request.user)
                response = {"code": 1, "msg": "NC details updated."}
                action = AuditAction.UPDATE
                log_views.insert(
                    "pws",
                    "NcCategory",
                    [nc_detail_id],
                    action,
                    request.user.id,
                    c_ip,
                    "NC Details details update.",
                )
            else:
                user = User.objects.get(id=request.user.id)
                if Util.has_perm("add_new_nc_detail", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                nc_detail = NcCategory.objects.create(name=category_name, parent_id_id=main_category, created_by=request.user)
                nc_detail_id = nc_detail.id
                response = {"code": 1, "msg": "NC Details has been created.", "nc_detail": nc_detail_id}
                action = AuditAction.INSERT
                log_views.insert(
                    "pws",
                    "NcCategory",
                    [nc_detail_id],
                    action,
                    request.user.id,
                    c_ip,
                    "NC Details has been created",
                )
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def nc_details_delete(request):
    try:
        with transaction.atomic():
            if Util.has_perm("delete_nc_detail", request.user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            else:
                nc_details_id_list = []
                nc_details_ids = request.POST.get("ids")
                for nc_details_id in nc_details_ids.split(","):
                    nc_details_id_list.append(nc_details_id)
                try:
                    NcCategory.objects.filter(id__in=nc_details_id_list).update(is_deleted=True)
                    c_ip = base_views.get_client_ip(request)
                    action = AuditAction.DELETE
                    log_views.insert("pws", "NcCategory", nc_details_ids.split(","), action, request.user.id, c_ip, "NC Details has been deleted")
                    response = {"code": 1, "msg": "NC Details has been deleted"}
                except ProtectedError:
                    response = {"code": 1, "msg": "You can not delete this Category."}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_orders(request):
    try:
        query = Q()
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "layer":
            sort_col = "layer_column"
        if sort_col == "-layer":
            sort_col = "-layer_column"
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_com_ids = Operator.objects.filter(user__id=request_user_id["id"]).values("company_ids").first()
        if operator_com_ids:
            operator_role = UserGroup.objects.filter(user_id=request_user_id["id"]).values("group__name").first()
            if operator_role["group__name"] == "Engineer":
                if operator_com_ids["company_ids"]:
                    operator_com_ids = list(map(int, operator_com_ids["company_ids"].split(",")))
                    query.add(Q(company_id__in=operator_com_ids), query.connector)
                else:
                    query.add(Q(company_id=None), query.connector)
        operator_id = Operator.objects.filter(show_own_records_only=True, user__username=request.user).first()
        if operator_id:
            query.add(Q(operator=operator_id), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("company"):
            query.add(Q(company__name__icontains=request.POST["company"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("order_status"):
            if request.POST.get("order_status").lower() in "order finish":
                query.add(Q(order_status__icontains="finished"), query.connector)
            else:
                query.add(Q(order_status__icontains=request.POST["order_status"]), query.connector)
        if request.POST.get("operator"):
            query.add(Q(operator__user__username__icontains=request.POST["operator"]), query.connector)
        if request.POST.get("order_date") is not None:
            query.add(
                Q(
                    order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        recordsTotal = Order.objects.filter(query).count()
        orders = (
            Order.objects.prefetch_related("ordertechparameter_set")
            .filter(query)
            .values(
                "id",
                "order_number",
                "pcb_name",
                "order_date",
                "order_status",
                "operator__user__username",
                "layer",
                "service__name",
                "preparation_due_date",
                "delivery_date",
                "company__name",
                "company__id",
                "order_next_status",
                "order_previous_status",
                "remarks",
                "customer_order_nr",
                "user__user__username",
                "in_time",
                "finished_on",
            )
            .annotate(
                board_thickness=F("ordertechparameter__board_thickness"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            )
            .order_by(sort_col)[start : (start + length)]
        )
        remarks_list = [order_["id"] for order_ in orders]
        remarks = Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list).values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        board_thickness_id = [order["board_thickness"] for order in orders if order["board_thickness"]]
        board_thickness = BoardThickness.objects.filter(code__in=board_thickness_id).values("name", "code")
        board_thickness_ = {}
        for board_thick_ in board_thickness:
            board_thickness_[board_thick_["code"]] = board_thick_["name"]

        layers = [order["layer"] for order in orders if order["layer"]]
        layer_ = Layer.objects.filter(code__in=layers).values("name", "code")
        layers_ = {}
        for layer_ in layer_:
            layers_[layer_["code"]] = layer_["name"]

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for order in orders:
            response["data"].append(
                {
                    "id": order["id"],
                    "order_number": order["order_number"],
                    "pcb_name": order["pcb_name"],
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "operator__user__username": order["operator__user__username"],
                    "layer": layers_[order["layer"]] if order["layer"] in layers_ else "",
                    "remarks": "<span>" + str(remarks_disc[order["id"]]) + "</span>"
                    if order["id"] in remarks_disc
                    else "<i class=icon-plus-circle title=Add-remarks style='font-size:13px; margin-left:0px;'></i> Add remarks",
                    "service__name": order["service__name"],
                    "preparation_due_date": Util.get_local_time(order["preparation_due_date"], True),
                    "delivery_date": Util.get_local_time(order["delivery_date"], True),
                    "company__name": order["company__name"],
                    "customer_order_nr": order["customer_order_nr"],
                    "board_thickness": board_thickness_[order["board_thickness"]] if order["board_thickness"] in board_thickness_ else "",
                    "user__user__username": order["user__user__username"],
                    "order_next_status": dict(order_status)[order["order_next_status"]] if order["order_next_status"] in dict(order_status) else "",
                    "order_previous_status": dict(order_status)[order["order_previous_status"]] if order["order_previous_status"] in dict(order_status) else "",
                    "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "",
                    "in_time": Util.get_local_time(order["in_time"], True),
                    "finished_on": Util.get_local_time(order["finished_on"], True),
                    "order_status_code": order["order_status"] if order["order_status"] else "",
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def auto_define_assignment_flow(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_define_auto_assignment", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            company_id = request.POST.get("company_id")
            order_allocation = request.POST.get("order_allocation")
            is_exist_company = OrderAllocationFlow.objects.filter(company_id=company_id)
            if is_exist_company:
                OrderAllocationFlow.objects.filter(company_id=company_id).update(allocation=order_allocation)
                return HttpResponse(AppResponse.msg(1, "Define auto assignment flow updated"), content_type="json")
            else:
                OrderAllocationFlow.objects.create(company_id=company_id, allocation=order_allocation)
                return HttpResponse(AppResponse.msg(1, "Define auto assignment flow created"), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def show_auto_define_assignment_flow(request):
    try:
        company_id = request.POST.get("company_id")
        is_exist_company = OrderAllocationFlow.objects.filter(company_id=company_id)
        if is_exist_company:
            order_allocation = OrderAllocationFlow.objects.filter(company_id=company_id).values("allocation").first()
            allocation_code = order_allocation["allocation"]
            if allocation_code == "pre_due_date":
                allocation_name = "Preparation due date"
            if allocation_code == "delivery_date":
                allocation_name = "Delivery date"
            if allocation_code == "systemin_time":
                allocation_name = "System intime"
            if allocation_code == "order_date":
                allocation_name = "Order date"
            if allocation_code == "delivery_and_order_date":
                allocation_name = "Delivery date and Order date"
            if allocation_code == "layers":
                allocation_name = "Layers"
            if allocation_code == "delivery_and_layers":
                allocation_name = "Delivery date and layers"
            response = {"code": 1, "order_allocation": allocation_code, "allocation_name": allocation_name}
        else:
            response = {"code": 1, "order_allocation": None, "allocation_name": None}
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def auto_assignment(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_auto_assignment", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        request.POST = Util.get_post_data(request)
        company_id = request.POST.get("company_id")
        process_id = request.POST.get("process_id")
        user_id = request.user.id
        operator = Operator.objects.filter(user_id=user_id).values("id", "user_id", "shift")
        if company_id:
            query.add(Q(company_id=company_id), query.connector)
        if process_id:
            order_process = OrderProcess.objects.filter(id=process_id).values("id", "code")
            query.add(Q(order_status=order_process[0]["code"]), query.connector)
        query.add(~Q(order_status__in=["cancel", "exception", "finished"]), query.connector)
        Order.objects.filter(query).update(operator_id=operator[0]["id"])
        order_id = Order.objects.filter(query).values("id")
        is_operator_login = OperatorLogs.objects.filter(operator_id_id=operator[0]["id"], logged_in_time__isnull=False).values("logged_in_time").first()
        operator_login_time = None
        if is_operator_login:
            operator_login_time = is_operator_login["logged_in_time"]
        for reserve_id in order_id:
            active_operator = ActiveOperators.objects.filter(operator_id_id=operator[0]["id"], reserved_order_id_id=None)
            if active_operator:
                ActiveOperators.objects.filter(operator_id_id=operator[0]["id"], reserved_order_id_id=None).update(
                    shift_id=operator[0]["shift"], logged_in_time=operator_login_time, reserved_order_id_id=reserve_id["id"]
                )
            else:
                ActiveOperators.objects.create(
                    operator_id_id=operator[0]["id"], shift_id=operator[0]["shift"], reserved_order_id_id=reserve_id["id"], logged_in_time=operator_login_time
                )
        return HttpResponse(AppResponse.msg(1, "Operator reserved"), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_order_status_save(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_change_status", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            status = request.POST.get("status")
            order_id = request.POST.get("order_id")
            action = AuditAction.UPDATE
            c_ip = base_views.get_client_ip(request)
            order = Order.objects.filter(id=order_id).values("id", "service__id", "company__id", "order_status", "company").first()
            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=order["company__id"], service_id=order["service__id"]).values("process_ids").first()
            ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
            processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "sequence", "name").order_by("sequence")
            all_processes_sequence_list = [x["sequence"] for x in processes]
            cu_sequence = [process["sequence"] if status == process["code"] else None for process in processes]
            cu_sequence = [sequence for sequence in cu_sequence if sequence]
            next_ = None
            ord_previous = None
            for process in processes:
                if cu_sequence and cu_sequence[0] < process["sequence"]:
                    next_ = process["code"]
                    break
            orde_prev_list = []
            for proecess_sequence in all_processes_sequence_list:
                orde_prev_list.append(proecess_sequence)
                if cu_sequence and cu_sequence[0] == proecess_sequence:
                    break
            if len(orde_prev_list) != 0:
                if len(orde_prev_list) == 1:
                    ord_prev = 0
                else:
                    ord_prev = orde_prev_list[-2]
                if ord_prev != 0 and ord_prev in all_processes_sequence_list:
                    ord_prev_ = OrderProcess.objects.filter(sequence=ord_prev).values("code").first()
                    ord_previous = ord_prev_["code"]
                else:
                    ord_previous = None
            if order["order_status"]:
                history_status = (
                    "Order status changed " + " " + "<b>" + " " + dict(order_status)[status] + " "
                    + "</b>" + " " + "from" + " " + "<b>" + " " + dict(order_status)[order["order_status"]] + " " + "</b>"
                )
            else:
                history_status = (
                    "Order status changed " + " " + "<b>" + " " + dict(order_status)[status]
                    + " " + "</b>" + " " + "from" + " " + "<b>" + " " + "-" + " " + "</b>"
                )
            if status == "finished":
                finished_on = datetime.datetime.now()
                order_detail = Order.objects.filter(id=order_id).values("company__name", "customer_order_nr", "order_number", "service__name", "pcb_name", "layer").first()
                user_cc_mail = Order.objects.filter(id=order_id).values("user_id").first()
                layer = Layer.objects.filter(code=order_detail["layer"]).values("code", "name").first()
                if layer:
                    layers = layer["name"]
                else:
                    layers = ""
                user_cc_mail = CompanyUser.objects.filter(id=user_cc_mail["user_id"]).values("user__email").first()
                cc_mail = user_cc_mail["user__email"] if user_cc_mail else ""
                email_id = CompanyParameter.objects.filter(company=order["company"]).values("ord_comp_mail", "mail_from").first()
                mail_from = email_id["mail_from"] if email_id["mail_from"] else None
                email_id = email_id["ord_comp_mail"]
                email_id = [email_ids for email_ids in email_id.split(",")]
                subject = "Order Processed - " + order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
                head = order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
                title = "Your order processed"
                message = render_to_string(
                    "pws/mail_order.html",
                    {
                        "mail_type": "finish_order",
                        "head": head,
                        "title": title,
                        "layers": layers,
                        "order_detail": order_detail,
                    },
                )
                send_mail(True, "public", [*email_id], subject, message, "", [cc_mail], mail_from)
                log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, history_status)
                log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, "Order has been finished")
                response = {"code": 1, "msg": "Order status update."}
            else:
                finished_on = None
            if status == "finished" or status == "cancel":
                ord_previous = order["order_status"]
            operator = Order.objects.filter(id=order_id).values("id", "operator", "operator__user__username", "operator_id", "operator__shift").first()
            if operator["operator"]:
                operator__user__username = operator["operator__user__username"]
                order_release_operator = "Operator" + " " + "<b>" + " " + operator__user__username + " " + "</b>" + " " + "is released"
                Order.objects.filter(id=order_id).update(operator=None)
                action = AuditAction.UPDATE
                log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, order_release_operator)
                reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
                login_time = reserved_order["logged_in_time"]
                ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
                is_active_operator = ActiveOperators.objects.filter(operator_id_id=operator["operator_id"])
                if len(is_active_operator) == 0:
                    ActiveOperators.objects.create(operator_id_id=operator["operator_id"], logged_in_time=login_time, shift_id=operator["operator__shift"])
            Order.objects.filter(id=order_id).update(
                order_status=status, order_next_status=next_, order_previous_status=ord_previous, in_time=datetime.datetime.now(), finished_on=finished_on
            )
            if status == "cancel":
                order_detail = Order.objects.filter(id=order_id).values("company__name", "customer_order_nr", "remarks", "service__name", "pcb_name", "layer").first()
                order_company = Order.objects.filter(id=order_id).values("company", "user_id").first()
                layer = Layer.objects.filter(code=order_detail["layer"]).values("code", "name").first()
                if layer:
                    layers = layer["name"]
                else:
                    layers = ""
                user_cc_mail = CompanyUser.objects.filter(id=order_company["user_id"]).values("user__email").first()
                cc_mail = user_cc_mail["user__email"] if user_cc_mail else ""
                email_id = CompanyParameter.objects.filter(company=order_company["company"]).values("ord_rec_mail", "mail_from").first()
                mail_from = email_id["mail_from"] if email_id["mail_from"] else None
                email_id = email_id["ord_rec_mail"]
                email_id = [email_ids for email_ids in email_id.split(",")]
                subject = "Order cancelled - " + order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
                head = order_detail["company__name"] + " #" + order_detail["customer_order_nr"]
                title = "Dear customer,<br>Order " + order_detail["customer_order_nr"] + " has been cancelled."
                message = render_to_string(
                    "pws/mail_order.html",
                    {
                        "head": head,
                        "title": title,
                        "layers": layers,
                        "order_detail": order_detail,
                    },
                )
                send_mail(True, "public", [*email_id], subject, message, "", [cc_mail], mail_from)
                log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, history_status)
                log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, "Order has been Cancelled")
                response = {"code": 1, "msg": "Order status update."}
            if status != "cancel" and status != "finished":
                log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, history_status)
                response = {"code": 1, "msg": "Order status update."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def nc_report(request):
    try:
        id = request.POST.get("id")
        query = Q()
        query.add(Q(content_type_id__model="order"), query.connector)
        query.add(Q(object_id=id), query.connector)
        query.add(
            Q(descr__icontains="</b> from <b>") |
            Q(descr="Exception generated on order") |
            Q(descr__istartswith="Order has been  <b> Finished </b> from <b>"), query.connector
        )
        query.add(~Q(descr__istartswith="Order sent back"), query.connector)
        query.add(~Q(descr__istartswith="Order status changed"), query.connector)
        query.add(~Q(descr__istartswith="Order has been  <b> Cancel"), query.connector)
        auditlogs = Auditlog.objects.filter(query).values("id", "operator__user__username", "descr", "action_by__username").order_by("-action_on")
        audit_logs = []
        for log in auditlogs:
            if log["descr"] == "Exception generated on order":
                audit_logs.append({"id": log["id"], "operator__user__username": log["action_by__username"], "descr": "Exception"})
            else:
                descr = log["descr"].split("from <b> ", 1)[1]
                descr = descr.split(" </b>")[0]
                audit_logs.append({"id": log["id"], "operator__user__username": log["operator__user__username"], "descr": descr if descr else ""})
        order = None
        order = Order.objects.filter(id=id).values("id", "customer_order_nr", "order_number", "order_status", "company__name", "company_id", "operator_id", "order_date").first()
        order_date = Util.get_local_time(order["order_date"], False)
        order_process = dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else ""
        order_process_code = order["order_status"]
        order_date = datetime.datetime.strptime(str(order_date).strip(), "%d/%m/%Y").strftime("%d/%m/%Y")
        main_category = NcCategory.objects.filter(Q(is_deleted=False), ~Q(name=None), ~Q(parent_id=None)).values("id", "name", "parent_id").first()
        today_date_time = datetime.datetime.now()
        nc_create_date = datetime.datetime.strptime(str(today_date_time).strip(), "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y %H:%M")
        nc_create_by = Operator.objects.filter(user_id=request.user.id).values("id").first()
        con = {
            "sub_name": main_category["name"],
            "sub_category": main_category["id"],
            "main_category": main_category["parent_id"],
            "order": order,
            "auditlogs": audit_logs,
            "order_date": order_date,
            "order_process": order_process,
            "order_process_code": order_process_code,
            "nc_create_date": nc_create_date,
            "nc_create_by": nc_create_by["id"]
        }
        return render(request, "pws/reports/nc_report.html", con)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_nc_report(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_add_nc", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order = request.POST.get("order")
            company_id = request.POST.get("company_id")
            operator_id = request.POST.get("operator_id")
            main_category = request.POST.get("main_category")
            sub_category = request.POST.get("sub_category")
            nc_from = request.POST.get("nc_from")
            nc_type = request.POST.get("nc_type")
            nc_create_date = request.POST.get("nc_create_date")
            nc_create_by = request.POST.get("nc_create_by")
            nc_create_date = datetime.datetime.strptime(str(nc_create_date).strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:01.111111")
            check = request.POST.getlist("check")
            if check == []:
                response = {"code": 0, "msg": "Please select atleast one record."}
            auditlogs = Auditlog.objects.filter(id__in=check).values("id", "action_by__username", "action_by", "descr", "operator__user__id", "operator")

            root_cause = request.POST.get("root_cause")
            problem = request.POST.get("problem")
            solution = request.POST.get("solution")

            file = request.FILES.get("file")
            order_number = request.POST.get("order_number")
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.INSERT
            if auditlogs:
                nc_create_by = Operator.objects.filter(id=nc_create_by).values("user_id").first()
                docnumber = DocNumber.objects.filter(code="Order_nc").first()
                nc_report_list = []
                for i in range(len(auditlogs)):
                    nc_report_list.append(
                        NonConformity(
                            nc_number=docnumber.nextnum,
                            company_id=company_id,
                            nc_date=nc_create_date,
                            order_id=order,
                            root_cause=root_cause,
                            problem=problem,
                            solution=solution,
                            category_id=main_category,
                            sub_category_id=sub_category,
                            nc_type=nc_type,
                            nc_from=nc_from,
                            created_by_id=nc_create_by["user_id"]
                        )
                    )
                nc_report = NonConformity.objects.bulk_create(nc_report_list)
                nc_report_ids = nc_report
                nc_report_ids_list = []
                auditlogs_list = list(auditlogs)
                if nc_report_ids:
                    process_dict = {}
                    nc_report_details_list = []
                    processes = OrderProcess.objects.values("id", "name")
                    for process in processes:
                        process_dict[process["name"]] = process["id"]
                    for x in range(len(nc_report_ids)):
                        if auditlogs_list[x]["descr"] == "Exception generated on order":
                            descr = "Exception"
                            nc_operator_id = auditlogs_list[x]["action_by"]
                        else:
                            descr = (auditlogs_list[x]["descr"]).split("from <b> ", 1)[1]
                            descr = descr.split(" </b>")[0]
                            nc_operator_id = auditlogs_list[x]["operator__user__id"]
                        operator = Operator.objects.filter(user__id=nc_operator_id).values("id").first()
                        operator_id = operator["id"] if operator else None
                        process_id = process_dict[descr] if descr in process_dict else None
                        nc_report_ids_list.append(nc_report_ids[x].id)
                        nc_report_details_list.append(
                            NonConformityDetail(
                                non_conformity_id=nc_report_ids[x].id,
                                operator_id=operator_id,
                                process_id=process_id,
                                nc_detail_date=nc_create_date,
                                audit_log_id=auditlogs_list[x]["id"]
                            )
                        )
                    if file is not None:
                        file_name = str(file)
                        file_data = file.read()
                        upload_and_save_impersonate(file_data, "pws", "order_attachment", order, request.user.id, c_ip, "NC_FILE", file_name, order_number, docnumber.nextnum)
                NonConformityDetail.objects.bulk_create(nc_report_details_list)
                log_views.insert("pws", "nonconformity", nc_report_ids_list, action, request.user.id, c_ip, "NC report has been created")
                log_views.insert("pws", "Order", [order], action, request.user.id, c_ip, "NC report has been created")
                docnumber.increase()
                docnumber.save()
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
            request_user_username = request_user_id["username"]
            request_user_id = request_user_id["id"]
            send_msg = []
            nc_creat_operator = Operator.objects.filter(user__id=request_user_id).values("id", "operator_group").first()
            operator_group = nc_creat_operator["operator_group"] if nc_creat_operator["operator_group"] else None
            if operator_group:
                all_operators = Operator.objects.filter(operator_group=operator_group, is_deleted=False).values("user_id")
                for data in all_operators:
                    if data["user_id"] not in send_msg:
                        send_msg.append(data["user_id"])
            app_name = "PWS"
            model_name = "NonConformity"
            name = "New NC added for" " " + order_number + " " "by" " " + request_user_username + " "
            description = "New NC added for" " " + "<b>" + "" + order_number + "</b>" + " " "by" " " + "<b>" + "" + request_user_username + " " + "</b>"
            content_type = ContentType.objects.filter(app_label=app_name.lower(), model=model_name.lower()).first()
            assign_to_op = Operator.objects.filter(user_id__in=send_msg).values("id")
            assign_to = [x["id"] for x in assign_to_op]
            assign_to_ = ",".join(map(str, assign_to))
            task = Task.objects.create(name=name, content_type=content_type, description=description, created_by_id=request_user, assign_to=assign_to_)
            if task:
                message = []
                for id in assign_to:
                    if not Message.objects.filter(task_id_id=task.id, operator_id_id=id):
                        message.append(Message(task_id_id=task.id, operator_id_id=id))
                Message.objects.bulk_create(message)
            response = {"code": 1, "msg": "NC report has been created."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order_allocation(request):
    try:
        query = Q()
        order_by_name = None
        delivery_date = "id"
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        company_id = request.POST.get("company_id")
        process_id = request.POST.get("process_id")
        data_sort = request.POST.get("data_sort")
        if company_id == "":
            company_id = None
        if process_id == "":
            process_id = None
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "layer":
            sort_col = "layer_column"
        if sort_col == "-layer":
            sort_col = "-layer_column"
        if sort_col == "delivery_date":
            sort_col = "act_delivery_date"
        if sort_col == "-delivery_date":
            sort_col = "-act_delivery_date"
        order_by = OrderAllocationFlow.objects.filter(company_id=company_id)
        if order_by and data_sort is True:
            order_by = OrderAllocationFlow.objects.filter(company_id=company_id).values("id", "allocation")
            order_by_name = order_by[0]["allocation"]
            if order_by_name == "pre_due_date":
                sort_col = "preparation_due_date"
            if order_by_name == "delivery_and_order_date":
                sort_col = "act_delivery_date"
                delivery_date = "order_date"
            if order_by_name == "systemin_time":
                sort_col = "in_time"
            if order_by_name == "delivery_date":
                sort_col = "act_delivery_date"
            if order_by_name == "order_date":
                sort_col = "order_date"
            if order_by_name == "layers":
                sort_col = "-layer_column"
            if order_by_name == "delivery_and_layers":
                sort_col = "act_delivery_date"
                delivery_date = "layer_column"
        if company_id:
            query.add(Q(company_id=company_id), query.connector)
        if process_id:
            order_process = OrderProcess.objects.filter(id=process_id).values("id", "code")
            query.add(Q(order_status=order_process[0]["code"]), query.connector)
        query.add(~Q(order_status__in=["cancel", "exception", "finished", "panel", "upload_panel"]), query.connector)
        orders = (
            Order.objects.filter(query)
            .values(
                "id",
                "company__name",
                "order_number",
                "service__name",
                "layer",
                "delivery_term",
                "pcb_name",
                "delivery_term",
                "order_date",
                "operator__user__username",
                "delivery_date",
                "order_status",
                "preparation_due_date",
                "pcb_name",
                "in_time",
                "customer_order_nr",
                "act_delivery_date",
            )
            .annotate(
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            )
            .order_by(sort_col, delivery_date)[start : (start + length)]
        )
        recordsTotal = Order.objects.filter(query).count()
        layers_code = [order_["layer"] for order_ in orders]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for order in orders:
            response["data"].append(
                {
                    "id": order["id"],
                    "preparation_due_date": Util.get_local_time(order["preparation_due_date"], True),
                    "layer": layers[order["layer"]] if order["layer"] in layers else None,
                    "order_number": order["order_number"],
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "delivery_term": dict(delivery_term)[order["delivery_term"]] if order["delivery_term"] in dict(delivery_term) else "",
                    "delivery_date": Util.get_local_time(order["act_delivery_date"], True),
                    "pcb_name": order["pcb_name"],
                    "operator__user__username": order["operator__user__username"],
                    "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "",
                    "service__name": order["service__name"],
                    "company__name": order["company__name"],
                    "in_time": Util.get_local_time(order["in_time"], True),
                    "customer_order_nr": order["customer_order_nr"],
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_order_status(request):
    try:
        id = request.POST.get("id")
        order = None
        if id != "0":
            order = Order.objects.filter(id=id).values("id", "service__id", "company__id", "order_status").first()
            order_flow_mapping = OrderFlowMapping.objects.filter(company_id=order["company__id"], service_id=order["service__id"]).values("process_ids").first()
            ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
            processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "name").order_by("sequence")
            code = []
            name = []
            for process in processes:
                code.append(process["code"])
                name.append(process["name"])
            processes = dict(zip(code, name))
        con = {"order": order, "processes": processes}
        return render(request, "pws/reports/order_status.html", con)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_nc_order": "nc_reports"}])
def nc_reports(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_nc_order_report", "can_update_nc_report"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/reports/nc_reports.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_nc_reports(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "id":
            sort_col = "-id"
        company_id = request.POST.get("company_id")
        created_on = request.POST.get("created_on")
        service_id = request.POST.get("service_id")
        operator_id = request.POST.get("operator_id")

        if company_id != "":
            query.add(Q(company_id=company_id), query.connector)
        if created_on != "":
            query.add(Q(nc_date__date=created_on), query.connector)
        if service_id != "":
            query.add(Q(order__service__id=service_id), query.connector)
        if operator_id != "":
            query.add(Q(nonconformitydetail__operator_id=operator_id), query.connector)
        recordsTotal = NonConformity.objects.filter(query).count()

        nc_reports = (
            NonConformity.objects.prefetch_related("nonconformitydetail_set")
            .filter(query)
            .values("id", "nc_number", "company__name", "category__name", "sub_category__name", "created_on", "nc_type", "order__customer_order_nr", "nc_date")
            .annotate(
                process=F("nonconformitydetail__process__name"),
                order_number=F("order__order_number"),
                service_name=F("order__service__name"),
                operator=F("nonconformitydetail__operator__user__username"),
                created_by=F("created_by__username"),
            )
            .order_by(sort_col)[start : (start + length)]
        )

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for nc_report in nc_reports:
            response["data"].append(
                {
                    "id": nc_report["id"],
                    "order__customer_order_nr": nc_report["order__customer_order_nr"],
                    "nc_number": nc_report["nc_number"],
                    "company__name": nc_report["company__name"],
                    "service_name": nc_report["service_name"],
                    "operator": nc_report["operator"],
                    "category__name": nc_report["category__name"],
                    "sub_category__name": nc_report["sub_category__name"],
                    "process": nc_report["process"],
                    "nc_date": Util.get_local_time(nc_report["nc_date"], True),
                    "order_number": nc_report["order_number"],
                    "nc_type": dict(nc_type)[nc_report["nc_type"]] if nc_report["nc_type"] in dict(nc_type) else "",
                    "created_by": nc_report["created_by"],
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def nc_report_details(request):
    try:
        id = request.POST.get("id")
        nc_reports = (
            NonConformity.objects.prefetch_related("nonconformitydetail_set")
            .filter(id=id)
            .values(
                "id",
                "order_id",
                "nc_number",
                "company__name",
                "category__name",
                "sub_category__name",
                "created_on",
                "nc_type",
                "order__customer_order_nr",
                "nc_from",
                "root_cause",
                "problem",
                "solution",
                "nc_date",
            )
            .annotate(
                process=F("nonconformitydetail__process__name"),
                order_number=F("order__order_number"),
                service_name=F("order__service__name"),
                operator=F("nonconformitydetail__operator__user__username"),
                created_by=F("created_by__username"),
            )
        ).first()
        files = (
            Order_Attachment.objects.filter(object_id=nc_reports["order_id"], file_type__code="NC_FILE", source_doc=nc_reports["nc_number"])
            .values("id", "name", "uid", "size")
            .first()
        )
        response = {
            "id": nc_reports["id"],
            "customer_order_nr": nc_reports["order__customer_order_nr"],
            "nc_number": nc_reports["nc_number"],
            "company": nc_reports["company__name"],
            "service_name": nc_reports["service_name"],
            "operator": nc_reports["operator"],
            "category": nc_reports["category__name"],
            "sub_category": nc_reports["sub_category__name"],
            "process": nc_reports["process"],
            "created_on": Util.get_local_time(nc_reports["created_on"], True),
            "order_number": nc_reports["order_number"],
            "nc_type": dict(nc_type)[nc_reports["nc_type"]] if nc_reports["nc_type"] in dict(nc_type) else "",
            "nc_from": dict(order_status)[nc_reports["nc_from"]] if nc_reports["nc_from"] in dict(order_status) else "",
            "root_cause": nc_reports["root_cause"],
            "problem": nc_reports["problem"],
            "solution": nc_reports["solution"],
            "nc_date": datetime.datetime.strptime(str(nc_reports["nc_date"]).strip(), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"),
            "file": files["name"] if files else None,
            "uid": files["uid"] if files else None,
        }
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_nc_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_nc_order_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        company_id = request.POST.get("company_id")
        service_id = request.POST.get("service_id")
        operator_id = request.POST.get("operator_id")
        created_on = request.POST.get("created_on")
        display_data_list = request.POST.get("display_data_list")
        if display_data_list:
            display_data_list = list(map(int, display_data_list.split(",")))
            query.add(Q(id__in=display_data_list), query.connector)

        if company_id != "":
            query.add(Q(company_id=company_id), query.connector)
        if service_id != "":
            query.add(Q(order__service__id=service_id), query.connector)
        if operator_id != "":
            query.add(Q(nonconformitydetail__operator_id=operator_id), query.connector)
        if created_on != "":
            query.add(Q(nc_date__date=created_on), query.connector)

        nc_reports = (
            NonConformity.objects.prefetch_related("nonconformitydetail_set")
            .filter(query)
            .values("id", "nc_number", "company__name", "category__name", "sub_category__name", "created_on", "nc_type", "order__customer_order_nr", "nc_date")
            .annotate(
                process=F("nonconformitydetail__process__name"),
                order_number=F("order__order_number"),
                service_name=F("order__service__name"),
                operator=F("nonconformitydetail__operator__user__username"),
                created_by=F("created_by__username"),
            ).order_by(order_by)[start : (start + length)]
        )
        query_result = []
        for nc_report in nc_reports:
            query_result.append(
                {
                    "nc_date": Util.get_local_time(nc_report["nc_date"], True),
                    "order_number": nc_report["order_number"],
                    "nc_number": nc_report["nc_number"],
                    "customer_order_nr": nc_report["order__customer_order_nr"],
                    "company": nc_report["company__name"],
                    "service": nc_report["service_name"],
                    "engineer": nc_report["operator"],
                    "category": nc_report["category__name"],
                    "sub_category": nc_report["sub_category__name"],
                    "process": nc_report["process"],
                    "nc_type": nc_report["nc_type"],
                    "prepared_by": nc_report["created_by"],
                }
            )
        headers = [
            {"title": "NC created on"},
            {"title": "PWS ID"},
            {"title": "NC number"},
            {"title": "Order number"},
            {"title": "Customer"},
            {"title": "Service"},
            {"title": "Operator"},
            {"title": "Main category"},
            {"title": "Sub category"},
            {"title": "Process"},
            {"title": "NC type"},
            {"title": "NC Prepared by"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "nc_reports.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def import_order_from_ecc_and_ppm(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_import_order", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        order_type = request.POST.get("order_type")
        customer_orders = json.loads(request.POST.get("customer_orders"))
        if order_type == "ecc":
            import_orders = ImportOrder()
            import_order = import_orders.ecc_order(customer_orders, request)
            if import_order:
                return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
            else:
                return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")

        elif order_type == "power":
            import_orders = ImportOrder()
            import_order = import_orders.power_order(customer_orders, request)
            if import_order:
                return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
            else:
                return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")

        elif order_type == "power_inq":
            import_orders = ImportOrder()
            import_order = import_orders.power_inquery(customer_orders, request)
            if import_order:
                return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
            else:
                return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")

        elif order_type == "ec_inq_pending":
            import_orders = ImportOrder()
            import_order = import_orders.ec_inquiry(customer_orders, request)
            if import_order:
                return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
            else:
                return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")

        elif order_type == "ec_compare":
            ec_order = []
            ec_inquiry = []
            for order in customer_orders:
                if order["import_from"] == "ECORDERS":
                    ec_order.append(order["cus_order_no"])
                else:
                    ec_inquiry.append(order["cus_order_no"])
            if len(ec_order) > 0:
                import_orders = ImportOrder()
                import_order = import_orders.ecc_order(ec_order, request)
                if import_order is True:
                    return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
                else:
                    return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")
            if len(ec_inquiry) > 0:
                import_orders = ImportOrder()
                import_order = import_orders.ec_inquiry(ec_inquiry, request)
                if import_order is True:
                    return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
                else:
                    return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")
            return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")

        elif order_type == "power_compare":
            power_order = []
            power_inquiry = []
            for order in customer_orders:
                if order["import_from"] == "POWERORD":
                    power_order.append(order["cus_order_no"])
                else:
                    power_inquiry.append(order["cus_order_no"])
            if len(power_order) > 0:
                import_orders = ImportOrder()
                import_order = import_orders.power_order(power_order, request)
                if import_order:
                    return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
                else:
                    return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")
            if len(power_inquiry) > 0:
                import_orders = ImportOrder()
                import_order = import_orders.power_inquery(power_inquiry, request)
                if import_order:
                    return HttpResponse(json.dumps({"code": 1, "msg": "Record(s) imported"}), content_type="json")
                else:
                    return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")
            return HttpResponse(json.dumps({"code": 0, "msg": "Record(s) not imported"}), content_type="json")

    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def order_details_update(request):
    try:
        with transaction.atomic():
            order_id = request.POST.get("order_id")
            layer = request.POST.get("layer")
            delivery_format = request.POST.get("delivery_format")
            delivery_term = request.POST.get("delivery_term")
            pcb_name = request.POST.get("pcb_name")
            remarks = request.POST.get("remarks")
            cam_remark = request.POST.get("cam_remark")
            delivery_date = None
            act_delivery_date = None
            delivery_term_days = delivery_term.replace("DEL_", "") if delivery_term and delivery_term != "No" else None
            if delivery_term_days:
                current_date = datetime.datetime.now()
                del_term_date = datetime.datetime.now() + timedelta(int(delivery_term_days))
                delta = datetime.timedelta(days=1)
                weekends = 0
                while current_date <= del_term_date:
                    date = current_date.weekday()
                    if date > 5:
                        weekends = weekends + 1
                    current_date += delta
                delivery_date = del_term_date + timedelta(weekends)
                if delivery_date.weekday() == 6:
                    delivery_date = delivery_date + timedelta(1)
                if layer:
                    layer_ = layer[0:2]
                    list_layer = [4, 6, 8]
                    if int(layer_) not in list_layer:
                        act_delivery_date = delivery_date
                    if int(layer_) == 4:
                        act_delivery_date = delivery_date - timedelta(days=1)
                    if int(layer_) == 6:
                        act_delivery_date = delivery_date - timedelta(days=2)
                    if int(layer_) >= 8:
                        act_delivery_date = delivery_date - timedelta(days=3)
                else:
                    act_delivery_date = delivery_date
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            if order_id:
                Order.objects.filter(id=order_id).update(
                    delivery_format=delivery_format,
                    layer=layer,
                    delivery_term=delivery_term,
                    pcb_name=pcb_name,
                    remarks=remarks if remarks is not None else "",
                    delivery_date=delivery_date,
                    act_delivery_date=act_delivery_date,
                )
                exiest = OrderTechParameter.objects.filter(order=order_id).exists()
                if exiest is False:
                    OrderTechParameter.objects.create(order_id=order_id)
                order_deta = OrderTechParameter.objects.filter(order__id=order_id).values().first()
                order_tech_valuesdict = {}
                not_bool_values = [
                    "board_thickness",
                    "buildup_code",
                    "blind_buried_via_runs",
                    "edge_connector_gold_surface",
                    "tool_nr",
                    "tool_spec",
                    "logistics_spec",
                    "extra_coupon",
                    "cam_remark",
                ]
                for values in order_deta:
                    if values != "id" and values != "order_id":
                        values_name = request.POST.get(values)
                        if values_name == "on":
                            values_name = True
                        if values_name is None and values not in not_bool_values:
                            values_name = False
                        order_tech_valuesdict.update({values: values_name})
                OrderTechParameter.objects.filter(order=order_id).update(**order_tech_valuesdict)
            Remark.objects.filter(entity_id=order_id, content_type__model="order", remark_type="Cus_rema").update(remark=remarks)
            Remark.objects.filter(entity_id=order_id, content_type__model="order", remark_type="Cum_rema").update(remark=cam_remark)
            log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, "Order has been updated")
            response = {"code": 1, "msg": "Order details updated", "delivery_date": Util.get_local_time(delivery_date, True)}
            return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def add_remark(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_add_remark", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_id = request.POST.get("id")
            remarks_add = request.POST.get("remarks_add")
            remarks_type_add = request.POST.get("remarks_type_add")
            c_ip = base_views.get_client_ip(request)
            model_remark_field = "remarks"
            if order_id is not None:
                base_views.create_remark("pws", "order", order_id, remarks_add, "", request.user.id, model_remark_field, remarks_type_add, "", "")
                action = AuditAction.INSERT
                log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, "Remark has been added")
            return HttpResponse(AppResponse.msg(1, str("Remark has been added successfully.")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def utility_place_order(request, company_id, company_user_id):
    try:
        order_parameter = list(
            OrderScreen.objects.filter(company_id=company_id, is_deleted=False)
            .values(
                "order_screen_parameter_id",
                "order_screen_parameter__code",
                "order_screen_parameter__name",
                "default_value",
                "is_compulsory",
                "order_screen_parameter__parent_id",
                "display_ids",
            )
            .order_by("order_screen_parameter__sequence")
        )
        sub_par_ids = [y for x in order_parameter if x["display_ids"] for y in x["display_ids"].split(",")]
        response = list(OrderScreenParameter.objects.filter(id__in=sub_par_ids).values("code", "name", "parent_id").order_by("sequence"))
        service_sub_ids = [y for x in order_parameter if x["order_screen_parameter__code"] == "cmb_service" for y in x["display_ids"].split(",") if x["display_ids"]]
        if service_sub_ids:
            services = Service.objects.filter(id__in=service_sub_ids).values("id", "name", "code")
        else:
            applied_services = OrderFlowMapping.objects.filter(~Q(service_id=None), company_id=company_id, is_deleted=False).values("service_id")
            service_sub_ids = [x["service_id"] for x in applied_services]
            if service_sub_ids:
                services = Service.objects.filter(id__in=service_sub_ids).values("id", "name", "code")
            else:
                services = None
        return render(
            request,
            "pws/utility_place_order.html",
            {"order_parameter": order_parameter, "response": response, "company_id": company_id, "company_user_id": company_user_id, "services": services},
        )
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def chaeck_fqc_in_process(request):
    try:
        order_id = request.POST.get("orderId")
        order = Order.objects.filter(id=order_id).values("id", "service__id", "company__id").first()
        order_flow_mapping = OrderFlowMapping.objects.filter(company_id=order["company__id"], service_id=order["service__id"]).values("process_ids").first()
        ids = order_flow_mapping["process_ids"].split(",") if order_flow_mapping and order_flow_mapping["process_ids"] is not None else []
        processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=ids).values("code", "sequence", "name").order_by("sequence")
        all_processes_list = [x["code"] for x in processes]
        if "FQC" in all_processes_list:
            response = {"code": 1}
        else:
            response = {"code": 0}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_to_fqc(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_send_to_fqc", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_id = request.POST.get("orderId")
            order = Order.objects.filter(id=order_id).values("order_status", "order_next_status", "order_previous_status", "operator", "operator_id", "operator__shift").first()
            auditlog = Auditlog.objects.filter(object_id=order_id, descr__endswith=" is reserved").values("action_on", "descr").last()
            process_start_time = auditlog["action_on"].replace(tzinfo=None)
            current_time = datetime.datetime.now()
            diff = current_time - process_start_time
            prep_time_ = diff.days * 86400 + diff.seconds
            user_efficiency_log(request, order_id, prep_time_, "FQC", "", "")
            c_ip = base_views.get_client_ip(request)
            order_next_status = (
                "Order sent to" + " " + "<b>" + " " + "FQC" + " " + "</b>" + " "
                + "from" + " " + "<b>" + " " + dict(order_status)[order["order_status"]] + " " + "</b>"
            )
            if order:
                Order.objects.filter(id=order_id).update(
                    order_status="FQC", order_next_status=order["order_status"], order_previous_status=order["order_status"], operator=None, in_time=datetime.datetime.now()
                )
                action = AuditAction.UPDATE
                log_views.insert_("pws", "order", [order_id], action, request.user.id, c_ip, order_next_status, order["operator"], prep_time_)
                reserved_order = ActiveOperators.objects.filter(reserved_order_id_id=order_id).values("logged_in_time").first()
                login_time = reserved_order["logged_in_time"]
                ActiveOperators.objects.filter(reserved_order_id_id=order_id).delete()
                is_active_operator = ActiveOperators.objects.filter(operator_id_id=order["operator_id"])
                if len(is_active_operator) == 0:
                    ActiveOperators.objects.create(operator_id_id=order["operator_id"], logged_in_time=login_time, shift_id=order["operator__shift"])
            response = {"code": 1, "msg": "Send to FQC."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_utility_place_order(request, company_id, company_user_id):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_customer_place_order", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_params = request.POST.dict()
            order_number = order_params.pop("order_number")
            service_type_code = order_params.pop("service_type") if "service_type" in order_params else None
            pcb_name = order_params.pop("pcb_name") if "pcb_name" in order_params else None
            order_tech = {}
            for key, val in order_params.items():
                if key.startswith("cmb_"):
                    key = key.replace("cmb_", "")
                    order_tech[key] = val
                if key.startswith("txt_"):
                    key = key.replace("txt_", "")
                    order_tech[key] = val
                if key.startswith("chk_"):
                    if val == "on":
                        key = key.replace("chk_", "")
                        order_tech["is_" + key] = True
                    else:
                        key = key.replace("chk_", "")
                        order_tech["is_" + key] = False
                if key.startswith("is_chk_"):
                    if val == "on":
                        key = key.replace("is_chk_", "")
                        order_tech[key] = True
                    else:
                        key = key.replace("is_chk_", "")
                        order_tech[key] = False
            delivery_date = None
            act_delivery_date = None
            delivery_term = order_tech.pop("delivery_term") if "delivery_term" in order_tech else None
            delivery_term_days = delivery_term.replace("DEL_", "") if delivery_term and delivery_term != "No" else None
            layer = order_tech.pop("layer") if "layer" in order_tech else None
            if delivery_term_days:
                current_date = datetime.datetime.now()
                del_term_date = datetime.datetime.now() + timedelta(int(delivery_term_days))
                delta = datetime.timedelta(days=1)
                weekends = 0
                while current_date <= del_term_date:
                    date = current_date.weekday()
                    if date > 5:
                        weekends = weekends + 1
                    current_date += delta
                delivery_date = del_term_date + timedelta(weekends)
                if delivery_date.weekday() == 6:
                    delivery_date = delivery_date + timedelta(1)
                if layer:
                    layer_ = layer[0:2]
                    list_layer = [4, 6, 8]
                    if int(layer_) not in list_layer:
                        act_delivery_date = delivery_date
                    if int(layer_) == 4:
                        act_delivery_date = delivery_date - timedelta(days=1)
                    if int(layer_) == 6:
                        act_delivery_date = delivery_date - timedelta(days=2)
                    if int(layer_) >= 8:
                        act_delivery_date = delivery_date - timedelta(days=3)
                else:
                    act_delivery_date = delivery_date
            delivery_format = order_tech.pop("delivery_format") if "delivery_format" in order_tech else None
            remarks = order_tech.pop("remarks") if "remarks" in order_tech else ""
            order_flow = OrderFlowMapping.objects.filter(company_id=company_id, service__code=service_type_code).values("process_ids", "service_id").first()
            service_id = order_flow["service_id"] if order_flow and order_flow["service_id"] else None
            process_ids = str(order_flow["process_ids"]).split(",") if order_flow and order_flow["process_ids"] != "" else []
            processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=process_ids).values("code", "sequence").order_by("sequence")
            order_status = processes[0]["code"] if len(processes) > 0 else ""
            order_next_status = processes[1]["code"] if len(processes) > 1 else None
            company_user = CompanyUser.objects.filter(company_id=company_id, user=company_user_id).values("id").first()
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.INSERT
            cam_remark = order_tech["cam_remark"] if "cam_remark" in order_tech else None
            model_remark_field = "remarks"
            due_time = order_tech["due_time"] if "due_time" in order_tech else None
            if due_time and due_time != "":
                preparation_due_date = datetime.datetime.now() + timedelta(hours=int(due_time.replace("Due_time_", "").replace("H", ""))) if "due_time" in order_tech else None
            else:
                preparation_due_date = None
            docnumber = DocNumber.objects.filter(code="Order_place").first()
            messages = order_number + " " + "Order placed"
            order = Order(
                company_id=company_id,
                order_number=docnumber.nextnum,
                customer_order_nr=order_number,
                service_id=service_id,
                layer=layer,
                order_date=datetime.datetime.now(),
                preparation_due_date=preparation_due_date,
                user_id=company_user["id"],
                delivery_date=delivery_date,
                act_delivery_date=act_delivery_date,
                order_status=order_status,
                order_next_status=order_next_status,
                delivery_format=delivery_format,
                delivery_term=delivery_term,
                pcb_name=pcb_name,
                remarks=remarks,
                in_time=datetime.datetime.now(),
            )
            order.save()
            docnumber.increase()
            docnumber.save()
            order_tech["order_id"] = order.id
            order_tech_para = OrderTechParameter(**order_tech)
            order_tech_para.save()
            no_of_jobs = CompanyParameter.objects.filter(company_id=company_id).values("no_of_jobs").first()
            total_jobs = ""
            if no_of_jobs["no_of_jobs"] is None:
                total_jobs = 1
            else:
                total_jobs = no_of_jobs["no_of_jobs"] + 1
            CompanyParameter.objects.filter(company_id=company_id).update(no_of_jobs=total_jobs)
            file_ = request.FILES.get("order_file")
            if file_ is not None:
                file_name = str(file_)
                file_data = file_.read()
                upload_and_save_impersonate(file_data, "pws", "order_attachment", order.id, request.user.id, c_ip, "ORDERFILE", file_name, order_number, "")

            order_detail = Order.objects.filter(id=order.id).values("company__name", "customer_order_nr", "remarks", "service__name", "pcb_name", "layer").first()
            order_company = Order.objects.filter(id=order.id).values("company").first()
            layer = Layer.objects.filter(code=order_detail["layer"]).values("code", "name").first()
            if layer:
                layers = layer["name"]
            else:
                layers = ""
            user_cc_mail = CompanyUser.objects.filter(id=order.user_id).values("user__email").first()
            cc_mail = user_cc_mail["user__email"] if user_cc_mail else ""
            email_id = CompanyParameter.objects.filter(company=order_company["company"]).values("ord_rec_mail", "mail_from").first()
            mail_from = email_id["mail_from"] if email_id["mail_from"] else None
            email_id = email_id["ord_rec_mail"]
            if email_id:
                email_id = [email_ids for email_ids in email_id.split(",")]
                subject = "Order Acknowledgement - " + order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
                head = order_detail["company__name"] + " #" + order_detail["customer_order_nr"]
                title = "Dear customer,<br>Thank you for placing your order."
                message = render_to_string(
                    "pws/mail_order.html",
                    {
                        "head": head,
                        "title": title,
                        "layers": layers,
                        "order_detail": order_detail,
                    },
                )
                send_mail(True, "public", [*email_id], subject, message, "", [cc_mail], mail_from)
            log_views.insert("pws", "order", [order.id], action, company_user_id, c_ip, "Order has been created")
            if remarks != "":
                base_views.create_remark("pws", "order", order.id, remarks, "Cus_rema", request.user.id, model_remark_field, "Customer_Remarks", "", "")
            if cam_remark:
                base_views.create_remark("pws", "order", order.id, order_tech["cam_remark"], "Cum_rema", request.user.id, model_remark_field, "Customer_CAM_Remarks", "", "")
            skill_matrix_order(request, order.id, order_status, None)
            return HttpResponse(AppResponse.msg(1, messages), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_customer_input_output": "work_detail_customer"}])
def work_detail_customer(request):
    user = User.objects.get(id=request.user.id)
    perms = ["can_export_customer_input_output_detail_report"]
    permissions = Util.get_permission_role(user, perms)
    return render(request, "pws/reports/work_detail_customer.html", {"permissions": json.dumps(permissions)})


def search_work_detail_customer(request):
    try:
        if "load_data" in request.POST:
            query = Q()
            query1 = Q()
            request.POST = Util.get_post_data(request)
            start = int(request.POST["start"])
            length = int(request.POST["length"])
            sort_col = Util.get_sort_column(request.POST)
            if sort_col == "layer":
                sort_col = "layer_column"
            if sort_col == "-layer":
                sort_col = "-layer_column"
            if request.POST.get("company_id") != "":
                query.add(Q(company_id=request.POST["company_id"]), query.connector)
            if request.POST.get("operator_id") != "":
                query.add(Q(operator_id=request.POST["operator_id"]), query.connector)
            if request.POST.get("start_date__date") and request.POST.get("end_date__date"):
                query.add(
                    Q(
                        order__order_date__range=[
                            datetime.datetime.strptime(str(request.POST["start_date__date"]) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(request.POST["end_date__date"]) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query.connector,
                )
            query.add(Q(order__order_status="finished"), query.connector)
            if request.POST.get("operator_id") != "":
                query1.add(Q(order__operator=request.POST["operator_id"]), query1.connector)
            if request.POST.get("start_date__date") and request.POST.get("end_date__date"):
                query1.add(
                    Q(
                        order__order_date__range=[
                            datetime.datetime.strptime(str(request.POST["start_date__date"]) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(request.POST["end_date__date"]) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query1.connector,
                )
            if request.POST.get("company_id") != "":
                query1.add(Q(order__company=request.POST["company_id"]), query1.connector)
            query1.add(Q(order__order_status="finished"), query1.connector)

            recordTotal = (
                UserEfficiencyLog.objects.filter(query)
                .values("order__order_number")
                .annotate(
                    order_date=F("order__order_date"),
                    customer_order_nr=F("order__customer_order_nr"),
                    company__name=F("company__name"),
                    service__name=F("order__service__name"),
                    layer=F("order_layer"),
                    finished_on=F("order__finished_on"),
                    operator=Count("operator__user__username", distinct=True),
                    prep_time=Sum("prep_time"),
                )
                .count()
            )

            user_efficiency_logs = (
                UserEfficiencyLog.objects.filter(query)
                .values(
                    "order__order_number",
                    "order__customer_order_nr"
                )
                .annotate(
                    order_date=F("order__order_date"),
                    company__name=F("company__name"),
                    service__name=F("order__service__name"),
                    layer=F("order_layer"),
                    finished_on=F("order__finished_on"),
                    operator=Count("operator__user__username", distinct=True),
                    prep_time=Sum("prep_time"),
                    move_to_panel=Count("order__order_number", filter=Q(order_to_status="panel"), distinct=True),
                    layer_column=Case(
                        When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                        When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                        When(layer="", then=None),
                        default=None,
                        output_field=IntegerField(),
                    ),
                )
                .order_by(sort_col)[start : (start + length)]
            )

            layers = [user_efficiency_log["layer"] for user_efficiency_log in user_efficiency_logs if user_efficiency_log["layer"]]
            layer = Layer.objects.filter(code__in=layers).values("name", "code")
            layers_ = {}
            for layer_ in layer:
                layers_[layer_["code"]] = layer_["name"]

            ppa_exception = (
                OrderException.objects.filter(query1)
                .values(
                    "order__order_number",
                    "order__customer_order_nr"
                )
                .annotate(
                    pre_define_problem_count=Count("order__order_number", filter=Q(pre_define_problem__code="Pre-production approval"), distinct=True),
                )
            )
            move_to_ppa = {}
            for ppa_exception_count in ppa_exception:
                move_to_ppa[ppa_exception_count["order__order_number"], ppa_exception_count["order__customer_order_nr"]] = ppa_exception_count["pre_define_problem_count"]

            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordTotal,
                "recordsFiltered": recordTotal,
                "data": [],
            }
            index = 1
            for user_efficiency_log in user_efficiency_logs:
                time_taken = None
                if user_efficiency_log["prep_time"] is not None:
                    pre = int(user_efficiency_log["prep_time"])
                    hour = pre // 3600
                    pre %= 3600
                    minutes = pre // 60
                    pre %= 60
                    preparation_time = str(hour) + ":" + str(minutes).zfill(2)
                    time_taken = int(user_efficiency_log["prep_time"])
                response["data"].append(
                    {
                        "id": index,
                        "order_date": Util.get_local_time(user_efficiency_log["order_date"], True),
                        "company__name": user_efficiency_log["company__name"],
                        "order__order_number": user_efficiency_log["order__order_number"],
                        "order__customer_order_nr": user_efficiency_log["order__customer_order_nr"],
                        "service__name": user_efficiency_log["service__name"],
                        "operator": user_efficiency_log["operator"],
                        "prep_time": preparation_time if time_taken is not None else "",
                        "finished_on": Util.get_local_time(user_efficiency_log["finished_on"], True),
                        "layer": layers_[user_efficiency_log["layer"]] if user_efficiency_log["layer"] in layers_ else "",
                        "si_completed": (user_efficiency_log["move_to_panel"] if user_efficiency_log["move_to_panel"] else 0)
                        + (
                            move_to_ppa[user_efficiency_log["order__order_number"], user_efficiency_log["order__customer_order_nr"]]
                            if (user_efficiency_log["order__order_number"], user_efficiency_log["order__customer_order_nr"]) in move_to_ppa else 0
                        ),
                        "sort_col": sort_col,
                        "recordsTotal": recordTotal,
                    }
                )
                index += 1
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_work_detail_customer(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_customer_input_output_detail_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        query1 = Q()
        company_id = request.POST.get("company_id")
        operator_id = request.POST.get("operator_id")
        start_date__date = request.POST.get("start_date__date")
        end_date__date = request.POST.get("end_date__date")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")

        if company_id != "":
            query.add(Q(company_id=company_id), query.connector)
        if operator_id != "":
            query.add(Q(operator__id=operator_id), query.connector)
        if start_date__date != "" and end_date__date != "":
            query.add(
                Q(
                    order__order_date__range=[
                        datetime.datetime.strptime(str(start_date__date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(end_date__date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        if request.POST.get("operator_id") != "":
            query1.add(Q(order__operator=request.POST["operator_id"]), query1.connector)
        if request.POST.get("start_date__date") and request.POST.get("end_date__date"):
            query1.add(
                Q(
                    order__order_date__range=[
                        datetime.datetime.strptime(str(request.POST["start_date__date"]) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST["end_date__date"]) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query1.connector,
            )
        if request.POST.get("company_id") != "":
            query1.add(Q(order__company=request.POST["company_id"]), query1.connector)
        query1.add(Q(order__order_status="finished"), query1.connector)

        user_efficiency_logs = (
            UserEfficiencyLog.objects.filter(query, order__order_status="finished")
            .values(
                "order__order_number",
                "order__customer_order_nr"
            )
            .annotate(
                order_date=F("order__order_date"),
                company__name=F("company__name"),
                service__name=F("order__service__name"),
                layer=F("order_layer"),
                finished_on=F("order__finished_on"),
                operator=Count("operator", distinct=True),
                prep_time=Sum("prep_time"),
                move_to_panel=Count("order__order_number", filter=Q(order_to_status="panel"), distinct=True),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )

        layers = [user_efficiency_log["layer"] for user_efficiency_log in user_efficiency_logs if user_efficiency_log["layer"]]
        layer = Layer.objects.filter(code__in=layers).values("name", "code")
        layers_ = {}
        for layer_ in layer:
            layers_[layer_["code"]] = layer_["name"]

        ppa_exception = (
            OrderException.objects.filter(query1)
            .values(
                "order__order_number",
                "order__customer_order_nr"
            )
            .annotate(
                pre_define_problem_count=Count("order__order_number", filter=Q(pre_define_problem__code="Pre-production approval"), distinct=True),
            )
        )
        move_to_ppa = {}
        for ppa_exception_count in ppa_exception:
            move_to_ppa[ppa_exception_count["order__order_number"], ppa_exception_count["order__customer_order_nr"]] = ppa_exception_count["pre_define_problem_count"]

        query_result = []
        for user_efficiency_log in user_efficiency_logs:
            time_taken = None
            if user_efficiency_log["prep_time"] is not None:
                pre = int(user_efficiency_log["prep_time"])
                hour = pre // 3600
                pre %= 3600
                minutes = pre // 60
                pre %= 60
                preparation_time = str(hour) + ":" + str(minutes).zfill(2)
                time_taken = int(user_efficiency_log["prep_time"])
            query_result.append(
                {
                    "order_date": Util.get_local_time(user_efficiency_log["order_date"], True),
                    "company": user_efficiency_log["company__name"],
                    "order_number": user_efficiency_log["order__order_number"],
                    "order__customer_order_nr": user_efficiency_log["order__customer_order_nr"],
                    "service_name": user_efficiency_log["service__name"],
                    "layer": layers_[user_efficiency_log["layer"]] if user_efficiency_log["layer"] in layers_ else "",
                    "finished_on": Util.get_local_time(user_efficiency_log["finished_on"], True),
                    "total_operator": user_efficiency_log["operator"],
                    "prep_time": preparation_time if time_taken is not None else "",
                    "si_completed": (user_efficiency_log["move_to_panel"] if user_efficiency_log["move_to_panel"] else 0)
                    + (
                        move_to_ppa[user_efficiency_log["order__order_number"], user_efficiency_log["order__customer_order_nr"]]
                        if (user_efficiency_log["order__order_number"], user_efficiency_log["order__customer_order_nr"]) in move_to_ppa else 0
                    ),
                }
            )
        headers = [
            {"title": "Order date"},
            {"title": "Company"},
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Service"},
            {"title": "Layer"},
            {"title": "Completion date"},
            {"title": "No of engineers worked"},
            {"title": "Total time worked on it"},
            {"title": "SI completed"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "customer_input/output_detail_report.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_customer_summary": "summary_report_customer"}])
def summary_report_customer(request):
    user = User.objects.get(id=request.user.id)
    perms = ["can_export_customer_input_output_summary_report"]
    permissions = Util.get_permission_role(user, perms)
    return render(request, "pws/reports/summary_report_customer.html", {"permissions": json.dumps(permissions)})


def search_summary_report_customer(request):
    try:
        if "load_data" in request.POST:
            request.POST = Util.get_post_data(request)
            query = Q()
            query1 = Q()
            query2 = Q()
            start = int(request.POST["start"])
            length = int(request.POST["length"])
            sort_col = Util.get_sort_column(request.POST)

            if request.POST.get("start_date__date") and request.POST.get("end_date__date"):
                query.add(
                    Q(
                        action_on__date__range=[
                            datetime.datetime.strptime(str(request.POST["start_date__date"]), "%d/%m/%Y").strftime("%Y-%m-%d"),
                            datetime.datetime.strptime(str(request.POST["end_date__date"]), "%d/%m/%Y").strftime("%Y-%m-%d"),
                        ]
                    ),
                    query.connector,
                )
                query2.add(
                    Q(
                        created_on__date__range=[
                            datetime.datetime.strptime(str(request.POST["start_date__date"]), "%d/%m/%Y").strftime("%Y-%m-%d"),
                            datetime.datetime.strptime(str(request.POST["end_date__date"]), "%d/%m/%Y").strftime("%Y-%m-%d"),
                        ]
                    ),
                    query2.connector,
                )
            if request.POST.get("company_id") != "":
                query1.add(Q(company=request.POST["company_id"]), query1.connector)

            exception_descr = ["Exception replied", "Order has been updated from exception"]
            order_ids = []
            orders = Order.objects.filter(query1).values("id")
            for order in orders:
                order_ids.append(order["id"])
            recordsTotal = (
                Auditlog.objects.filter(
                    query,
                    (
                        Q(descr="Exception replied")
                        | Q(descr="Order has been updated from exception")
                        | Q(descr="Order has been created")
                        | Q(descr="Order has been finished")
                        | Q(descr="Exception generated on order")
                        | Q(descr="NC report has been created")
                        | Q(descr__endswith="is reserved")
                        | Q(descr__startswith="Order sent to")
                        | Q(descr__startswith="Order sent back to  <b>")
                        | Q(descr__startswith="Order has been  <b> Finished")
                    ),
                    Q(content_type__model="order"),
                    Q(object_id__in=order_ids)
                )
                .values(
                    "action_on__date",
                )
                .annotate(
                    company=Subquery(Order.objects.filter(id=OuterRef("object_id")).values("company__name").distinct()),
                    received=Count("id", filter=Q(descr="Order has been created")),
                    completed=Count("id", filter=Q(descr="Order has been finished")),
                    exception=Count("id", filter=Q(descr="Exception generated on order")),
                    exception_reply=Count("id", filter=Q(descr__in=exception_descr)),
                    operator=Count("descr", filter=Q(descr__endswith="is reserved"), distinct=True),
                    nc_report=Count("id", filter=Q(descr="NC report has been created")),
                    move_to_panel=Count("object_id", filter=Q(descr__startswith="Order sent to  <b> Panel") | Q(descr__startswith="Order sent back to  <b> Panel"), distinct=True)
                )
            ).count()

            audit_logs = (
                Auditlog.objects.filter(
                    query,
                    (
                        Q(descr="Exception replied")
                        | Q(descr="Order has been updated from exception")
                        | Q(descr="Order has been created")
                        | Q(descr="Order has been finished")
                        | Q(descr="Exception generated on order")
                        | Q(descr="NC report has been created")
                        | Q(descr__endswith="is reserved")
                        | Q(descr__startswith="Order sent to")
                        | Q(descr__startswith="Order sent back to  <b>")
                        | Q(descr__startswith="Order has been  <b> Finished")
                    ),
                    Q(content_type__model="order"),
                    Q(object_id__in=order_ids)
                )
                .values(
                    "action_on__date",
                )
                .annotate(
                    company=Subquery(Order.objects.filter(id=OuterRef("object_id")).values("company__name").distinct()),
                    received=Count("id", filter=Q(descr="Order has been created")),
                    completed=Count("id", filter=Q(descr="Order has been finished")),
                    exception=Count("id", filter=Q(descr="Exception generated on order")),
                    exception_reply=Count("id", filter=Q(descr__in=exception_descr)),
                    operator=Count("descr", filter=Q(descr__endswith="is reserved"), distinct=True),
                    nc_report=Count("id", filter=Q(descr="NC report has been created")),
                    total_time=Sum("prep_time"),
                    move_to_panel=Count("object_id", filter=Q(descr__startswith="Order sent to  <b> Panel") | Q(descr__startswith="Order sent back to  <b> Panel"), distinct=True)
                )
                .order_by(sort_col)[start : (start + length)]
            )

            audit_ = Auditlog.objects.filter(query, content_type__model="order", object_id__in=order_ids).values("object_id")
            order_ids = [order["object_id"] for order in audit_ if order["object_id"]]

            total_work_efficiencies = (
                UserEfficiencyLog.objects.filter(query2, order__in=order_ids)
                .values("created_on__date", "company__name")
                .annotate(
                    total_work_efficiency=Sum("total_work_efficiency"),
                    move_to_ppa=Count("order__order_number", filter=Q(order_to_status="ppa_exception"), distinct=True),
                )
            )
            total_work_efficiencies_ = {}
            for total_work_efficiency_ in total_work_efficiencies:
                total_work_efficiencies_[total_work_efficiency_["created_on__date"], total_work_efficiency_["company__name"]] = total_work_efficiency_["total_work_efficiency"]

            ppa_exception = (
                OrderException.objects.filter(query2)
                .values(
                    "created_on__date",
                    "order__company__name"
                )
                .annotate(
                    pre_define_problem_count=Count("order_id", filter=Q(pre_define_problem__code="Pre-production approval"), distinct=True),
                )
            )
            move_to_ppa = {}
            for ppa_exception_count in ppa_exception:
                move_to_ppa[ppa_exception_count["created_on__date"], ppa_exception_count["order__company__name"]] = ppa_exception_count["pre_define_problem_count"]

            remark_type_ids = CommentType.objects.filter(
                Q(code="Design_Remarks")
                | Q(code="analysis_remarks")
                | Q(code="incoming_remarks")
                | Q(code="BOM_incoming_remarks")
                | Q(code="SI_remarks")
                | Q(code="SICC_remarks")
                | Q(code="BOM_CC_remarks")
                | Q(code="FQC_remarks")
                | Q(code="panel_remarks")
                | Q(code="upload_panel_remarks")
            ).values("id")
            remark_type_id = [remark_type_id_["id"] for remark_type_id_ in remark_type_ids if remark_type_id_["id"]]
            remark = (
                Remark.objects.filter(query2, comment_type__in=remark_type_id, entity_id__in=order_ids)
                .values("created_on__date")
                .annotate(company=Subquery(Order.objects.filter(id=OuterRef("entity_id")).values("company__name").distinct()), remark_count=Count("id"))
            )
            total_remark_ = {}
            for remarks in remark:
                total_remark_[remarks["created_on__date"], remarks["company"]] = remarks["remark_count"]

            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }
            index = 1
            for audit_log in audit_logs:
                time_taken = None
                if audit_log["total_time"] is not None:
                    pre = int(audit_log["total_time"])
                    hour = pre // 3600
                    pre %= 3600
                    minutes = pre // 60
                    pre %= 60
                    preparation_time = str(hour) + ":" + str(minutes).zfill(2)
                    time_taken = int(audit_log["total_time"])
                response["data"].append(
                    {
                        "id": index,
                        "action_on__date": datetime.datetime.strptime(str(audit_log["action_on__date"]).strip(), "%Y-%m-%d").strftime("%d-%m-%Y"),
                        "company": audit_log["company"],
                        "received": audit_log["received"],
                        "completed": audit_log["completed"],
                        "exception": audit_log["exception"],
                        "exception_reply": audit_log["exception_reply"],
                        "operator": audit_log["operator"],
                        "total_points": Util.decimal_to_str(
                            request,
                            total_work_efficiencies_[audit_log["action_on__date"], audit_log["company"]]
                            if (audit_log["action_on__date"], audit_log["company"]) in total_work_efficiencies_
                            else 0.0,
                        ),
                        "total_time": preparation_time if time_taken is not None else "0:00 ",
                        "remark_count": total_remark_[audit_log["action_on__date"], audit_log["company"]]
                        if (audit_log["action_on__date"], audit_log["company"]) in total_remark_
                        else 0,
                        "nc_report": audit_log["nc_report"] if audit_log["nc_report"] else "0",
                        "si_completed": (audit_log["move_to_panel"] if audit_log["move_to_panel"] else 0)
                        + (
                            move_to_ppa[audit_log["action_on__date"], audit_log["company"]]
                            if (audit_log["action_on__date"], audit_log["company"]) in move_to_ppa
                            else 0
                        ),
                        "sort_col": sort_col,
                        "recordsTotal": recordsTotal,
                    }
                )
                index += 1
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_summary_report_customer(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_customer_input_output_summary_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        query1 = Q()
        query2 = Q()

        company_id = request.POST.get("company_id")
        start_date__date = request.POST.get("start_date__date")
        end_date__date = request.POST.get("end_date__date")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if start_date__date != "" and end_date__date != "":
            query.add(
                Q(
                    action_on__date__range=[
                        datetime.datetime.strptime(str(start_date__date), "%d/%m/%Y").strftime("%Y-%m-%d"),
                        datetime.datetime.strptime(str(end_date__date), "%d/%m/%Y").strftime("%Y-%m-%d"),
                    ]
                ),
                query.connector,
            )
            query2.add(
                Q(
                    created_on__date__range=[
                        datetime.datetime.strptime(str(start_date__date), "%d/%m/%Y").strftime("%Y-%m-%d"),
                        datetime.datetime.strptime(str(end_date__date), "%d/%m/%Y").strftime("%Y-%m-%d"),
                    ]
                ),
                query2.connector,
            )
        if company_id != "":
            query1.add(Q(company=company_id), query1.connector)

        exception_descr = ["Exception replied", "Order has been updated from exception"]
        order_ids = []
        orders = Order.objects.filter(query1).values("id")
        for order in orders:
            order_ids.append(order["id"])

        audit_logs = (
            Auditlog.objects.filter(
                query,
                (
                    Q(descr="Exception replied")
                    | Q(descr="Order has been updated from exception")
                    | Q(descr="Order has been created")
                    | Q(descr="Order has been finished")
                    | Q(descr="Exception generated on order")
                    | Q(descr="NC report has been created")
                    | Q(descr__endswith="is reserved")
                    | Q(descr__startswith="Order sent to")
                    | Q(descr__startswith="Order sent back to  <b>")
                    | Q(descr__startswith="Order has been  <b> Finished")
                ),
                Q(content_type__model="order"),
                Q(object_id__in=order_ids)
            )
            .values(
                "action_on__date",
            )
            .annotate(
                company=Subquery(Order.objects.filter(id=OuterRef("object_id")).values("company__name").distinct()),
                received=Count("id", filter=Q(descr="Order has been created")),
                completed=Count("id", filter=Q(descr="Order has been finished")),
                exception=Count("id", filter=Q(descr="Exception generated on order")),
                exception_reply=Count("id", filter=Q(descr__in=exception_descr)),
                operator=Count("descr", filter=Q(descr__endswith="is reserved"), distinct=True),
                nc_report=Count("id", filter=Q(descr="NC report has been created")),
                total_time=Sum("prep_time"),
                move_to_panel=Count("object_id", filter=Q(descr__startswith="Order sent to  <b> Panel") | Q(descr__startswith="Order sent back to  <b> Panel"), distinct=True)
            )
            .order_by(order_by)[start : (start + length)]
        )

        audit_ = Auditlog.objects.filter(query, content_type__model="order", object_id__in=order_ids).values("object_id")
        order_ids = [order["object_id"] for order in audit_ if order["object_id"]]

        total_work_efficiencies = (
            UserEfficiencyLog.objects.filter(query2, order__in=order_ids)
            .values("created_on__date", "company__name")
            .annotate(
                total_work_efficiency=Sum("total_work_efficiency"),
                move_to_ppa=Count("order__order_number", filter=Q(order_to_status="ppa_exception"), distinct=True),
            )
        )
        total_work_efficiencies_ = {}
        for total_work_efficiency_ in total_work_efficiencies:
            total_work_efficiencies_[total_work_efficiency_["created_on__date"], total_work_efficiency_["company__name"]] = total_work_efficiency_["total_work_efficiency"]

        ppa_exception = (
            OrderException.objects.filter(query2)
            .values(
                "created_on__date",
                "order__company__name"
            )
            .annotate(
                pre_define_problem_count=Count("order_id", filter=Q(pre_define_problem__code="Pre-production approval"), distinct=True),
            )
        )
        move_to_ppa = {}
        for ppa_exception_count in ppa_exception:
            move_to_ppa[ppa_exception_count["created_on__date"], ppa_exception_count["order__company__name"]] = ppa_exception_count["pre_define_problem_count"]

        remark_type_ids = CommentType.objects.filter(
            Q(code="Design_Remarks")
            | Q(code="analysis_remarks")
            | Q(code="incoming_remarks")
            | Q(code="BOM_incoming_remarks")
            | Q(code="SI_remarks")
            | Q(code="SICC_remarks")
            | Q(code="BOM_CC_remarks")
            | Q(code="FQC_remarks")
            | Q(code="panel_remarks")
            | Q(code="upload_panel_remarks")
        ).values("id")
        remark_type_id = [remark_type_id_["id"] for remark_type_id_ in remark_type_ids if remark_type_id_["id"]]
        remark = (
            Remark.objects.filter(query2, comment_type__in=remark_type_id, entity_id__in=order_ids)
            .values("created_on__date")
            .annotate(company=Subquery(Order.objects.filter(id=OuterRef("entity_id")).values("company__name").distinct()), remark_count=Count("id"))
        )
        total_remark_ = {}
        for remarks in remark:
            total_remark_[remarks["created_on__date"], remarks["company"]] = remarks["remark_count"]

        query_result = []
        for audit_log in audit_logs:
            time_taken = None
            if audit_log["total_time"] is not None:
                pre = int(audit_log["total_time"])
                hour = pre // 3600
                pre %= 3600
                minutes = pre // 60
                pre %= 60
                preparation_time = str(hour) + ":" + str(minutes).zfill(2)
                time_taken = int(audit_log["total_time"])
            query_result.append(
                {
                    "action_on__date": datetime.datetime.strptime(str(audit_log["action_on__date"]).strip(), "%Y-%m-%d").strftime("%d-%m-%Y"),
                    "company": audit_log["company"],
                    "received": audit_log["received"],
                    "completed": audit_log["completed"],
                    "exception": audit_log["exception"],
                    "exception_reply": audit_log["exception_reply"],
                    "operator": audit_log["operator"],
                    "total_points": Util.decimal_to_str(
                        request,
                        total_work_efficiencies_[audit_log["action_on__date"], audit_log["company"]]
                        if (audit_log["action_on__date"], audit_log["company"]) in total_work_efficiencies_
                        else 0.0,
                    ),
                    "total_time": preparation_time if time_taken is not None else "0:00",
                    "remark_count": total_remark_[audit_log["action_on__date"], audit_log["company"]]
                    if (audit_log["action_on__date"], audit_log["company"]) in total_remark_
                    else 0,
                    "nc_report": audit_log["nc_report"] if audit_log["nc_report"] else "0",
                    "si_completed": (audit_log["move_to_panel"] if audit_log["move_to_panel"] else 0)
                    + (
                        move_to_ppa[audit_log["action_on__date"], audit_log["company"]]
                        if (audit_log["action_on__date"], audit_log["company"]) in move_to_ppa
                        else 0
                    ),
                }
            )
        headers = [
            {"title": "Order date"},
            {"title": "Company"},
            {"title": "Received"},
            {"title": "Completed"},
            {"title": "Exception"},
            {"title": "Exception reply"},
            {"title": "No. of Engineers worked"},
            {"title": "Total points"},
            {"title": "Total time worked on it"},
            {"title": "Prep remark count"},
            {"title": "NC count"},
            {"title": "SI completed"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "customer_input/output_summary_report.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_engineers_work_report(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if request.POST.get("select_id"):
            if request.POST["group_id"] != "":
                query.add(Q(operator_id__operator_group=request.POST["group_id"]), query.connector)
            if request.POST["shift_id"] != "":
                query.add(Q(operator_id__shift=request.POST["shift_id"]), query.connector)
            if request.POST["select_id"] == "1":
                if request.POST["company_id"] != "":
                    query.add(Q(company_id=request.POST["company_id"]), query.connector)
            else:
                if request.POST["operator_id"] != "":
                    query.add(Q(operator_id=request.POST["operator_id"]), query.connector)
            if request.POST.get("date") != "":
                query.add(Q(created_on__date=request.POST["date"]), query.connector)
            request_user = request.user.id
            request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
            operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
            if operator_id:
                if operator_id["operator_type"]:
                    if operator_id["operator_type"] == "PLANET_ENG":
                        query.add(Q(operator__user__id=request_user_id["id"]), query.connector)
            if request.POST["select_id"] == "1":
                user_efficiency_logs = UserEfficiencyLog.objects.filter(query).values("operator__user__username").order_by(sort_col)
            else:
                user_efficiency_logs = UserEfficiencyLog.objects.filter(query).values("company__name").order_by(sort_col)
            data = user_efficiency_logs.annotate(
                total=Coalesce(Sum("total_work_efficiency"), 0),
                work_efficiency=Coalesce((Sum("total_work_efficiency") / 450) * 100, 0),
                schematic=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="schematic")), 0),
                footprint=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="footprint")), 0),
                placement=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="placement")), 0),
                routing=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="routing")), 0),
                gerber_release=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="gerber_release")), 0),
                analysis=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="analysis")), 0),
                incoming=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="incoming")), 0),
                BOM_incoming=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="BOM_incoming")), 0),
                SI=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="SI")), 0),
                SICC=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="SICC")), 0),
                BOM_CC=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="BOM_CC")), 0),
                FQC=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="FQC")), 0),
                panel=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="panel")), 0),
                upload_panel=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="upload_panel")), 0),
                exception=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="exception")), 0),
            )[start : (start + length)]
            recordsTotal = (user_efficiency_logs).distinct().count()
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }
            index = 1
            for user_efficiency_log in data:
                if request.POST["select_id"] == "1":
                    response["data"].append(
                        {
                            "id": index,
                            "operator__user__username": user_efficiency_log["operator__user__username"] if user_efficiency_log["operator__user__username"] else "",
                            "schematic": Util.decimal_to_str(request, user_efficiency_log["schematic"]),
                            "footprint": Util.decimal_to_str(request, user_efficiency_log["footprint"]),
                            "placement": Util.decimal_to_str(request, user_efficiency_log["placement"]),
                            "routing": Util.decimal_to_str(request, user_efficiency_log["routing"]),
                            "gerber_release": Util.decimal_to_str(request, user_efficiency_log["gerber_release"]),
                            "analysis": Util.decimal_to_str(request, user_efficiency_log["analysis"]),
                            "incoming": Util.decimal_to_str(request, user_efficiency_log["incoming"]),
                            "BOM_incoming": Util.decimal_to_str(request, user_efficiency_log["BOM_incoming"]),
                            "SI": Util.decimal_to_str(request, user_efficiency_log["SI"]),
                            "SICC": Util.decimal_to_str(request, user_efficiency_log["SICC"]),
                            "BOM_CC": Util.decimal_to_str(request, user_efficiency_log["BOM_CC"]),
                            "FQC": Util.decimal_to_str(request, user_efficiency_log["FQC"]),
                            "panel": Util.decimal_to_str(request, user_efficiency_log["panel"]),
                            "upload_panel": Util.decimal_to_str(request, user_efficiency_log["upload_panel"]),
                            "exception": Util.decimal_to_str(request, user_efficiency_log["exception"]),
                            "total": Util.decimal_to_str(request, user_efficiency_log["total"]),
                            "work_efficiency": Util.decimal_to_str(request, user_efficiency_log["work_efficiency"]),
                            "sort_col": sort_col,
                            "recordsTotal": recordsTotal,
                        }
                    )
                else:
                    response["data"].append(
                        {
                            "id": index,
                            "company__name": user_efficiency_log["company__name"] if user_efficiency_log["company__name"] else "",
                            "schematic": Util.decimal_to_str(request, user_efficiency_log["schematic"]),
                            "footprint": Util.decimal_to_str(request, user_efficiency_log["footprint"]),
                            "placement": Util.decimal_to_str(request, user_efficiency_log["placement"]),
                            "routing": Util.decimal_to_str(request, user_efficiency_log["routing"]),
                            "gerber_release": Util.decimal_to_str(request, user_efficiency_log["gerber_release"]),
                            "analysis": Util.decimal_to_str(request, user_efficiency_log["analysis"]),
                            "incoming": Util.decimal_to_str(request, user_efficiency_log["incoming"]),
                            "BOM_incoming": Util.decimal_to_str(request, user_efficiency_log["BOM_incoming"]),
                            "SI": Util.decimal_to_str(request, user_efficiency_log["SI"]),
                            "SICC": Util.decimal_to_str(request, user_efficiency_log["SICC"]),
                            "BOM_CC": Util.decimal_to_str(request, user_efficiency_log["BOM_CC"]),
                            "FQC": Util.decimal_to_str(request, user_efficiency_log["FQC"]),
                            "panel": Util.decimal_to_str(request, user_efficiency_log["panel"]),
                            "upload_panel": Util.decimal_to_str(request, user_efficiency_log["upload_panel"]),
                            "exception": Util.decimal_to_str(request, user_efficiency_log["exception"]),
                            "total": Util.decimal_to_str(request, user_efficiency_log["total"]),
                            "work_efficiency": Util.decimal_to_str(request, user_efficiency_log["work_efficiency"]),
                            "sort_col": sort_col,
                            "recordsTotal": recordsTotal,
                        }
                    )
                index += 1
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_engineers_work_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_engineers_work_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        select_id = request.POST.get("select_id")
        group_id = request.POST.get("group_id")
        shift_id = request.POST.get("shift_id")
        operator_id = request.POST.get("operator_id")
        company_id = request.POST.get("company_id")
        date = request.POST.get("date")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if group_id != "":
            query.add(Q(operator_id__operator_group=group_id), query.connector)
        if shift_id != "":
            query.add(Q(operator_id__shift=shift_id), query.connector)
        if select_id == "1":
            if company_id != "":
                query.add(Q(company_id=company_id), query.connector)
        else:
            if operator_id != "":
                query.add(Q(operator_id=operator_id), query.connector)
        if date != "":
            query.add(Q(created_on__date=date), query.connector)
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    query.add(Q(operator__user__id=request_user_id["id"]), query.connector)
        if select_id == "1":
            user_efficiency_logs = UserEfficiencyLog.objects.filter(query).values("operator__user__username").order_by(order_by)[start : (start + length)]
        else:
            user_efficiency_logs = UserEfficiencyLog.objects.filter(query).values("company__name").order_by(order_by)[start : (start + length)]

        data = user_efficiency_logs.annotate(
            total=Coalesce(Sum("total_work_efficiency"), 0),
            work_efficiency=Coalesce((Sum("total_work_efficiency") / 450) * 100, 0),
            schematic=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="schematic")), 0),
            footprint=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="footprint")), 0),
            placement=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="placement")), 0),
            routing=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="routing")), 0),
            gerber_release=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="gerber_release")), 0),
            analysis=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="analysis")), 0),
            incoming=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="incoming")), 0),
            BOM_incoming=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="BOM_incoming")), 0),
            SI=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="SI")), 0),
            SICC=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="SICC")), 0),
            BOM_CC=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="BOM_CC")), 0),
            FQC=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="FQC")), 0),
            panel=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="panel")), 0),
            upload_panel=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="upload_panel")), 0),
            exception=Coalesce(Sum("total_work_efficiency", filter=Q(order_from_status="exception")), 0),
        )
        query_result = []
        if select_id == "1":
            for user_efficiency_log in data:
                query_result.append(
                    {
                        "operator": user_efficiency_log["operator__user__username"] if user_efficiency_log["operator__user__username"] else "",
                        "schematic": Util.decimal_to_str(request, user_efficiency_log["schematic"]),
                        "footprint": Util.decimal_to_str(request, user_efficiency_log["footprint"]),
                        "placement": Util.decimal_to_str(request, user_efficiency_log["placement"]),
                        "routing": Util.decimal_to_str(request, user_efficiency_log["routing"]),
                        "gerber_release": Util.decimal_to_str(request, user_efficiency_log["gerber_release"]),
                        "analysis": Util.decimal_to_str(request, user_efficiency_log["analysis"]),
                        "incoming": Util.decimal_to_str(request, user_efficiency_log["incoming"]),
                        "BOM_incoming": Util.decimal_to_str(request, user_efficiency_log["BOM_incoming"]),
                        "SI": Util.decimal_to_str(request, user_efficiency_log["SI"]),
                        "SICC": Util.decimal_to_str(request, user_efficiency_log["SICC"]),
                        "BOM_CC": Util.decimal_to_str(request, user_efficiency_log["BOM_CC"]),
                        "FQC": Util.decimal_to_str(request, user_efficiency_log["FQC"]),
                        "panel": Util.decimal_to_str(request, user_efficiency_log["panel"]),
                        "upload_panel": Util.decimal_to_str(request, user_efficiency_log["upload_panel"]),
                        "exception": Util.decimal_to_str(request, user_efficiency_log["exception"]),
                        "total": Util.decimal_to_str(request, user_efficiency_log["total"]),
                        "work_efficiency": Util.decimal_to_str(request, user_efficiency_log["work_efficiency"]),
                    }
                )
            headers = [
                {"title": "Username"},
                {"title": "Schematic"},
                {"title": "Footprint"},
                {"title": "Placement"},
                {"title": "Routing"},
                {"title": "Gerber_release"},
                {"title": "Analysis"},
                {"title": "Incoming"},
                {"title": "BOM_incoming"},
                {"title": "SI"},
                {"title": "SICC"},
                {"title": "BOM_CC"},
                {"title": "FQC"},
                {"title": "Panel"},
                {"title": "Upload_panel"},
                {"title": "Exception"},
                {"title": "Total"},
                {"title": "Work efficiency"},
            ]
            return Util.export_to_xls(headers, query_result[:5000], "engineers_work_report.xls")
        else:
            for user_efficiency_log in data:
                query_result.append(
                    {
                        "company": user_efficiency_log["company__name"] if user_efficiency_log["company__name"] else "",
                        "schematic": Util.decimal_to_str(request, user_efficiency_log["schematic"]),
                        "footprint": Util.decimal_to_str(request, user_efficiency_log["footprint"]),
                        "placement": Util.decimal_to_str(request, user_efficiency_log["placement"]),
                        "routing": Util.decimal_to_str(request, user_efficiency_log["routing"]),
                        "gerber_release": Util.decimal_to_str(request, user_efficiency_log["gerber_release"]),
                        "analysis": Util.decimal_to_str(request, user_efficiency_log["analysis"]),
                        "incoming": Util.decimal_to_str(request, user_efficiency_log["incoming"]),
                        "BOM_incoming": Util.decimal_to_str(request, user_efficiency_log["BOM_incoming"]),
                        "SI": Util.decimal_to_str(request, user_efficiency_log["SI"]),
                        "SICC": Util.decimal_to_str(request, user_efficiency_log["SICC"]),
                        "BOM_CC": Util.decimal_to_str(request, user_efficiency_log["BOM_CC"]),
                        "FQC": Util.decimal_to_str(request, user_efficiency_log["FQC"]),
                        "panel": Util.decimal_to_str(request, user_efficiency_log["panel"]),
                        "upload_panel": Util.decimal_to_str(request, user_efficiency_log["upload_panel"]),
                        "exception": Util.decimal_to_str(request, user_efficiency_log["exception"]),
                        "total": Util.decimal_to_str(request, user_efficiency_log["total"]),
                        "work_efficiency": Util.decimal_to_str(request, user_efficiency_log["work_efficiency"]),
                    }
                )
            headers = [
                {"title": "Company"},
                {"title": "Schematic"},
                {"title": "Footprint"},
                {"title": "Placement"},
                {"title": "Routing"},
                {"title": "Gerber_release"},
                {"title": "Analysis"},
                {"title": "Incoming"},
                {"title": "BOM_incoming"},
                {"title": "SI"},
                {"title": "SICC"},
                {"title": "BOM_CC"},
                {"title": "FQC"},
                {"title": "Panel"},
                {"title": "Upload_panel"},
                {"title": "Exception"},
                {"title": "Total"},
                {"title": "Work efficiency"},
            ]
            return Util.export_to_xls(headers, query_result[:5000], "engineers_work_report.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def engineers_work_report_process_count(request):
    try:
        query = Q()
        response = []
        company_id = request.POST.get("company_id")
        service_id = request.POST.get("service_id")
        if company_id and service_id:
            query.add(Q(company_id=company_id), query.connector)
            query.add(Q(service_id=service_id), query.connector)
            efficiency = Efficiency.objects.filter(query, is_deleted=False).values("process_id__code", "layer", "multi_layer")
            process_id = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"])).values("code")
            process_code = [x["process_id__code"] for x in efficiency]
            effici_list = []
            if efficiency:
                for data in efficiency:
                    effici_list.append({data["process_id__code"]: data["layer"], data["process_id__code"] + "_ML": data["multi_layer"]})
            for data in process_id:
                if data["code"] not in process_code:
                    effici_list.append({data["code"]: 0, data["code"] + "_ML": 0})
            effici_dict = {}
            for data in effici_list:
                effici_dict.update(data)
            response = [effici_dict]
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def admin_dashboard(request):
    return render(request, "pws/dashboard.html")


@check_view_permission([{"report_logged_in_user": "logged_in_user"}])
def logged_in_user(request):
    user = User.objects.get(id=request.user.id)
    perms = ["can_export_logged_in_users"]
    permissions = Util.get_permission_role(user, perms)
    return render(request, "pws/logged_in_user.html", {"permissions": json.dumps(permissions)})


def logged_in_user_data(request):
    try:
        query = Q()
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        query.add(Q(logged_in_time__isnull=False), query.connector)
        if request.POST.get("first_name"):
            query.add(Q(operator_id__user__first_name__icontains=request.POST["first_name"]), query.connector)
        if request.POST.get("last_name"):
            query.add(Q(operator_id__user__last_name__icontains=request.POST["last_name"]), query.connector)
        if request.POST.get("user_name"):
            query.add(Q(operator_id__user__username__icontains=request.POST["user_name"]), query.connector)
        if request.POST.get("reserved_order_id__company__name"):
            query.add(Q(reserved_order_id__company__name__icontains=request.POST["reserved_order_id__company__name"]), query.connector)
        if request.POST.get("reserved_order_id__order_number"):
            query.add(Q(reserved_order_id__order_number__icontains=request.POST["reserved_order_id__order_number"]), query.connector)
        if request.POST.get("reserved_order_id__customer_order_nr"):
            query.add(Q(reserved_order_id__customer_order_nr__icontains=request.POST["reserved_order_id__customer_order_nr"]), query.connector)

        active_operator = (
            ActiveOperators.objects.filter(query)
            .values(
                "id",
                "operator_id__id",
                "operator_id__user__first_name",
                "operator_id__user__last_name",
                "logged_in_time",
                "operator_id__user__username",
                "reserved_order_id__order_number",
                "reserved_order_id__customer_order_nr",
                "reserved_order_id__company__name",
                "reserved_order_id__service__name",
                "reserved_order_id__order_status",
                "reserved_order_id__id",
            )
            .order_by(sort_col, "-logged_in_time")[start : (start + length)]
        )
        recordsTotal = ActiveOperators.objects.filter(query).values("id")
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": len(recordsTotal),
            "recordsFiltered": len(recordsTotal),
            "data": [],
        }
        index = 1

        order_ids = [order["reserved_order_id__id"] for order in active_operator if order["reserved_order_id__id"]]
        reserved_on = Auditlog.objects.filter(object_id__in=order_ids, descr__endswith=" is reserved").values("object_id", "descr", "action_on").order_by("id")
        orders_reserved = Util.get_dict_from_quryset("object_id", "action_on", reserved_on)

        for order in active_operator:
            response["data"].append(
                {
                    "id": order["id"],
                    "login_id": order["id"],
                    "operator_id__user__first_name": order["operator_id__user__first_name"],
                    "operator_id__user__last_name": order["operator_id__user__last_name"],
                    "operator_id__user__username": order["operator_id__user__username"],
                    "reserved_order_id__order_number": order["reserved_order_id__order_number"],
                    "reserved_order_id__customer_order_nr": order["reserved_order_id__customer_order_nr"],
                    "reserved_order_id__company__name": order["reserved_order_id__company__name"],
                    "reserved_order_id__service__name": order["reserved_order_id__service__name"],
                    "reserved_order_id__order_status": dict(order_status)[order["reserved_order_id__order_status"]]
                    if order["reserved_order_id__order_status"] in dict(order_status) else None,
                    "logged_in_time": order["logged_in_time"].strftime("%d/%m/%y %H:%M:%S") if order["logged_in_time"] is not None else "",
                    "reserved_on": (orders_reserved[order["reserved_order_id__id"]]).strftime("%d/%m/%y %H:%M:%S") if order["reserved_order_id__id"] in orders_reserved else "",
                    "sort_col": sort_col,
                    "recordsTotal": len(recordsTotal),
                }
            )
            index += 1
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def place_continue(request):
    customer_user = request.POST.get("customer_user")
    response = {"id": customer_user}
    return HttpResponse(AppResponse.get(response), content_type="json")


def save_engineers_work_report(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_save_preptime", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            company_id = request.POST.get("company_id")
            service_id = request.POST.get("service_id")
            process_id = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"])).values("id", "code")
            for process_id_ in process_id:
                layer = request.POST.get(process_id_["code"]) if request.POST.get(process_id_["code"]) else 0
                multi_layer = request.POST.get(process_id_["code"] + "_ML") if request.POST.get(process_id_["code"] + "_ML") else 0
                if Efficiency.objects.filter(company_id=company_id, service_id=service_id, process_id=process_id_["id"], is_deleted=False).exists():
                    Efficiency.objects.filter(company_id=company_id, service_id=service_id, process_id=process_id_["id"]).update(layer=layer, multi_layer=multi_layer)
                else:
                    Efficiency.objects.create(company_id=company_id, service_id=service_id, process_id=process_id_["id"], layer=layer, multi_layer=multi_layer)
                response = {"code": 1, "msg": "Efficiency saved."}
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.INSERT
            log_views.insert(
                "pws",
                "Efficiency",
                [company_id],
                action,
                request.user.id,
                c_ip,
                "Engineers work report preptime has been created",
            )
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_exception_mail(request):
    try:
        if request.method == "POST":
            order_id = request.POST["order_id"]
            subject = request.POST["subject"]
            email_id = request.POST["toUser"]
            cc_mails = request.POST["ccUser"]
            message = str(BeautifulSoup(request.POST["msg"], features="html5lib"))
            is_si_file = OrderException.objects.filter(order=order_id).values("id", "exception_nr", "is_si_file", "pre_define_problem__code").last()
            save_message = dict()
            save_message["exceptionId"] = is_si_file["id"]
            save_message["exceptionProb"] = is_si_file["pre_define_problem__code"]
            save_message["toMail"] = email_id
            save_message["ccMail"] = cc_mails
            save_message["subject"] = subject
            save_message["message"] = message
            Order.objects.filter(id=order_id).update(mail_messages=save_message)
            email_id = [email_ids for email_ids in email_id.split(",")]
            order_detail = OrderException.objects.filter(order=order_id).values("order__company", "pre_define_problem__code").last()
            company_gen_mail = (
                CompanyParameter.objects.filter(company=order_detail["order__company"])
                .values("is_send_attachment", "is_exp_file_attachment", "mail_from", "int_exc_from").first()
            )
            mail_from = company_gen_mail["mail_from"] if company_gen_mail["mail_from"] else None
            if order_detail["pre_define_problem__code"] == "Internal Exception":
                mail_from = company_gen_mail["int_exc_from"] if company_gen_mail["int_exc_from"] else settings.INTERNAL_EXCEPTION_FROM
            mail_attachment = {}
            if company_gen_mail["is_exp_file_attachment"]:
                upload_image = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="EXCEPTION").values("url", "name", "uid").last()
                if upload_image:
                    full_path = os.path.join(str(settings.FILE_SERVER_PATH), upload_image["url"])
                    mail_attachment[upload_image["name"]] = full_path

            if company_gen_mail["is_send_attachment"]:
                if is_si_file["is_si_file"]:
                    si_file = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="SI").values("url", "name", "uid").last()
                    if si_file:
                        full_path = os.path.join(str(settings.FILE_SERVER_PATH), si_file["url"])
                        mail_attachment[si_file["name"]] = full_path
            send_mail(True, "public", [*email_id], subject, message, mail_attachment, [cc_mails], mail_from)
            return HttpResponse(AppResponse.msg(1, "Email has been sent."), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, "Something went wrong."), content_type="json")


def exports_logged_in_operator(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_logged_in_users", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        query.add(Q(logged_in_time__isnull=False), query.connector)
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        if request.POST.get("first_name"):
            query.add(Q(operator_id__user__first_name__icontains=request.POST["first_name"]), query.connector)
        if request.POST.get("last_name"):
            query.add(Q(operator_id__user__last_name__icontains=request.POST["last_name"]), query.connector)
        if request.POST.get("user_name"):
            query.add(Q(operator_id__user__username__icontains=request.POST["user_name"]), query.connector)
        if request.POST.get("reserved_order_id__company__name"):
            query.add(Q(reserved_order_id__company__name__icontains=request.POST["reserved_order_id__company__name"]), query.connector)
        if request.POST.get("reserved_order_id__order_number"):
            query.add(Q(reserved_order_id__order_number__icontains=request.POST["reserved_order_id__order_number"]), query.connector)
        if request.POST.get("reserved_order_id__customer_order_nr"):
            query.add(Q(reserved_order_id__customer_order_nr__icontains=request.POST["reserved_order_id__customer_order_nr"]), query.connector)

        active_operator = (
            ActiveOperators.objects.filter(query)
            .values(
                "id",
                "operator_id__id",
                "operator_id__user__first_name",
                "operator_id__user__last_name",
                "logged_in_time",
                "operator_id__user__username",
                "reserved_order_id__order_number",
                "reserved_order_id__customer_order_nr",
                "reserved_order_id__company__name",
                "reserved_order_id__service__name",
                "reserved_order_id__order_status",
                "reserved_order_id__id",
            )
            .order_by(order_by, "-logged_in_time")[start : (start + length)]
        )

        order_ids = [order["reserved_order_id__id"] for order in active_operator if order["reserved_order_id__id"]]
        reserved_on = Auditlog.objects.filter(object_id__in=order_ids, descr__endswith=" is reserved").values("object_id", "descr", "action_on").order_by("id")
        orders_reserved = Util.get_dict_from_quryset("object_id", "action_on", reserved_on)

        query_result = []
        for operator in active_operator:
            query_result.append(
                {
                    "first_name": operator["operator_id__user__first_name"],
                    "last_name": operator["operator_id__user__last_name"],
                    "operator_name": operator["operator_id__user__username"],
                    "login_time": operator["logged_in_time"].strftime("%Y-%m-%d %H:%M") if operator["logged_in_time"] is not None else "",
                    "pws_id": operator["reserved_order_id__order_number"],
                    "order_number": operator["reserved_order_id__customer_order_nr"],
                    "customer_name": operator["reserved_order_id__company__name"],
                    "service_name": operator["reserved_order_id__service__name"],
                    "process": dict(order_status)[operator["reserved_order_id__order_status"]] if operator["reserved_order_id__order_status"] in dict(order_status) else None,
                    "reserved_on": (orders_reserved[operator["reserved_order_id__id"]]).strftime("%d/%m/%y %H:%M:%S") if operator["reserved_order_id__id"] in orders_reserved else "",
                }
            )
        headers = [
            {"title": "First name"},
            {"title": "Last name"},
            {"title": "Operator name"},
            {"title": "Login time"},
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Customer"},
            {"title": "Service"},
            {"title": "Process"},
            {"title": "Reserved on"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "LoginOperator.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, "Something went wrong."), content_type="json")


def mail_screen_file(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_put_to_customer", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        order_id = request.POST.get("order_id")
        exception_id = request.POST.get("order_exception_id")
        order_number = request.POST.get("order_number")
        company_name = request.POST.get("company_name")

        order_detail = (
            OrderException.objects.filter(id=exception_id)
            .values(
                "order__company__name",
                "order__company",
                "order__order_number",
                "order__customer_order_nr",
                "order__pcb_name",
                "order__layer",
                "order__delivery_term",
                "order__delivery_date",
                "pre_define_problem__code",
                "order_status",
            )
            .first()
        )
        is_si_file = OrderException.objects.filter(id=exception_id).values("is_si_file", "order__user_id", "internal_remark").first()
        internal_remark = is_si_file["internal_remark"] if is_si_file else None
        company_gen_mail = (
            CompanyParameter.objects.filter(company=order_detail["order__company"])
            .values("gen_mail", "is_send_attachment", "is_exp_file_attachment", "ord_exc_rem_mail", "int_exc_to", "int_exc_cc").first()
        )
        if company_gen_mail["is_exp_file_attachment"]:
            upload_image = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="EXCEPTION").values("url", "name", "uid").last()
        else:
            upload_image = ""

        if company_gen_mail["is_send_attachment"]:
            if is_si_file["is_si_file"]:
                si_file = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="SI").values("url", "name", "uid").last()
            else:
                si_file = ""
        else:
            si_file = ""

        order_status_name = OrderProcess.objects.filter(code=order_detail["order_status"]).values("code", "name").first()
        layer = Layer.objects.filter(code=order_detail["order__layer"]).values("code", "name").first()
        if layer:
            layers = layer["name"]
        else:
            layers = ""
        delivery_terms = dict(delivery_term)[order_detail["order__delivery_term"]] if order_detail["order__delivery_term"] in dict(delivery_term) else ""
        if order_detail["pre_define_problem__code"] == "Internal Exception":
            # email_id_ = company_gen_mail["int_exc_to"] if company_gen_mail["int_exc_to"] else settings.INTERNAL_EXCEPTION_MAIL
            # cc_mail_ = company_gen_mail["int_exc_cc"] if company_gen_mail["int_exc_cc"] else settings.INTERNAL_EXCEPTION_CC_MAIL
            cc_mail = CompanyUser.objects.filter(id=is_si_file["order__user_id"]).values("user__email").first()
            cc_mail_ = None
            if cc_mail:
                cc_mail_ = cc_mail["user__email"]
            email_id_ = company_gen_mail["ord_exc_rem_mail"]
            subject = "Internal Exception #" + str(order_detail["order__customer_order_nr"]) + "."
            title = "Dear Concern,<br>Please check on below details and suggest us back asap : #" + str(order_detail["order__customer_order_nr"]) + "."
        else:
            cc_mail = CompanyUser.objects.filter(id=is_si_file["order__user_id"]).values("user__email").first()
            cc_mail_ = None
            if cc_mail:
                cc_mail_ = cc_mail["user__email"]
            email_id_ = company_gen_mail["ord_exc_rem_mail"]
            subject = "Exception found during CAM work for " + company_name + " #" + order_number + "."
            title = "Following are the details of Queries observed during CAM work. Please check and reply for each point."
        head = company_name + " #" + order_number + "."
        message = render_to_string(
            "pws/mail_order.html",
            {
                "internal_remark": internal_remark,
                "head": head,
                "title": title,
                "layers": layers,
                "order_detail": order_detail,
                "company_gen_mail": company_gen_mail,
                "delivery_terms": delivery_terms,
                "order_status_name": order_status_name["name"] if order_status_name is not None else "",
            },
        )
        response = {
            "code": 1,
            "msg": "Order cancel.",
            "upload_image": upload_image,
            "si_file": si_file,
            "subject": subject,
            "message": message,
            "pre_define_problem__code": order_detail["pre_define_problem__code"],
            "mail_to_customer": email_id_,
            "mail_to_cc": cc_mail_,
        }
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def skill_matrixs(request):
    return render(request, "pws/skill_matrixs.html")


def skill_matrix(request, company_id):
    try:
        customer_name = Company.objects.filter(id=company_id).values("name").first()
        exiest = SkillMatrix.objects.filter(company=company_id).exists()
        if exiest is False:
            process_id = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"])).values("id")
            skill_matrix = []
            for process_id_ in process_id:
                skill_matrix.append(SkillMatrix(company_id=company_id, process_id=process_id_["id"]))
            SkillMatrix.objects.bulk_create(skill_matrix)
        skillmatrix = SkillMatrix.objects.filter(company_id=company_id).values("company__name", "process__code", "operator_ids", "company")
        skillmatrixlist = []
        skillmatrixdict = {}
        skill_m_list = []
        is_operators = []
        for i in skillmatrix:
            skill_m_dict = {}
            if i["operator_ids"] is not None:
                is_operators.append(i["operator_ids"])
                skillmatrix_operator = []
                skillmatrix_operator.append(list(map(int, i["operator_ids"].split(","))))
                oper_ = list(itertools.chain(*skillmatrix_operator))
                operators = Operator.objects.filter(user_id__in=oper_, is_active=True, is_deleted=False).values("user__username")
                skill_m_dict["selectedoperator" + i["process__code"]] = oper_
                skill_m_dict[i["process__code"]] = [i["user__username"] for i in operators]
                skill_m_list.append(skill_m_dict)
            else:
                skill_m_dict[i["process__code"]] = i["operator_ids"]
                skill_m_list.append(skill_m_dict)
            skillmatrixdict[i["company__name"]] = skill_m_list
        skillmatrixlist.append(skillmatrixdict)
        excluded_order_status = ["cancel", "finished"]
        query_skill = Q()
        query_skill.add(~Q(reserved_order_id__order_status__in=excluded_order_status), query_skill.connector)
        login_operator = ActiveOperators.objects.filter(query_skill, logged_in_time__isnull=False).values("operator_id__user__username")
        logging_operator = []
        for operators in login_operator:
            logging_operator.append(operators["operator_id__user__username"])
        operatorslist = Operator.objects.filter(is_active=True, is_deleted=False).values("user_id", "company_ids")
        skill_operator = {}
        for operator in operatorslist:
            if operator["company_ids"]:
                skill_operator[operator["user_id"]] = list(map(int, operator["company_ids"].split(",")))
        comp_oper_dic = {}
        for company in skillmatrix:
            for key, value in skill_operator.items():
                for company_id in value:
                    if company_id == company["company"]:
                        if company_id in comp_oper_dic:
                            comp_oper_dic[company_id].append(key)
                        else:
                            comp_oper_dic[company_id] = [key]
        operator = {}
        for com_key, com_value in comp_oper_dic.items():
            customer_id_ = Company.objects.filter(id=com_key).values("name").first()
            operat = Operator.objects.filter(user_id__in=com_value).order_by("user__username").values("user_id", "user__username")
            operator[customer_id_["name"]] = operat
        context = {
            "operatorlist": operator,
            "logging_operator": logging_operator,
            "skillmatrix": skillmatrixlist,
            "customer_name": customer_name["name"],
            "is_operators": is_operators,
        }
        return render(request, "pws/skill_matrix.html", context)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_skill_matrix(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)

        if request.POST.get("customer"):
            query.add(Q(name__icontains=request.POST["customer"]), query.connector)
        query.add(Q(is_deleted=False), query.connector)
        recordsTotal = Company.objects.filter(query).count()
        companies = Company.objects.filter(query).values("name", "id").order_by(sort_col)[start : (start + length)]
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for company in companies:
            response["data"].append(
                {
                    "id": company["id"],
                    "name": company["name"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_skill_matrix_company(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("add_skill_matrix_order_allocation", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            customer_name = request.POST.get("customer_id_")
            customer_id_ = Company.objects.filter(name=customer_name).values("id").first()
            listoperator = request.POST.get("listoperator") if request.POST.get("listoperator") != "" else None
            process_name = request.POST.get("process_name")
            SkillMatrix.objects.filter(company_id=customer_id_["id"], process__code=process_name).update(operator_ids=listoperator)
            response = {}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_skill_matrix_company(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("add_skill_matrix_order_allocation", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            company_name = request.POST.get("company_id")
            company_id = Company.objects.filter(name=company_name).values("id").first()
            SkillMatrix.objects.filter(company_id=company_id["id"]).update(operator_ids=None)
            response = {"code": 1, "msg": "Skill matrix data has been deleted."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def remove_skill_matrix_oper(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("add_skill_matrix_order_allocation", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            company_name = request.POST.get("customer_id")
            company_id = Company.objects.filter(name=company_name).values("id").first()
            operator_name = request.POST.get("operator")
            operator_id = Operator.objects.filter(user__username=operator_name).values("user_id").first()
            process = request.POST.get("process")
            skill = SkillMatrix.objects.filter(company_id=company_id["id"], process__code=process).values("operator_ids").first()
            listoperator = []
            for id in skill["operator_ids"].split(","):
                if int(id) != operator_id["user_id"]:
                    listoperator.append(id)
            operator_ids_ = ",".join(listoperator)
            operator_ids = operator_ids_ if operator_ids_ != "" else None
            SkillMatrix.objects.filter(company_id=company_id["id"], process__code=process).update(operator_ids=operator_ids)
            response = {"code": 1, "msg": "Operator has been remove successfully."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def import_orders_and_inquiries(request):
    try:
        pws_service = PWSEcPyService()
        import_orders = ImportOrder()
        order_type = request.GET.get("type")

        if order_type == "ECORD":
            response = pws_service.get_ecc([{"order_type": "ECORD"}], "/ecpy/pws/orders_and_inquiries_export")
            customer_orders = [order_nr["Number"] for order_nr in response]
            import_orders.ecc_order(customer_orders, request)
            return HttpResponse(AppResponse.get({"code": 1, "msg": "All Record(s) imported"}), content_type="json")

        if order_type == "ECINQ":
            response = pws_service.get_ecc([{"order_type": "ECINQ"}], "/ecpy/pws/orders_and_inquiries_export")
            customer_orders = [order_nr["Number"] for order_nr in response]
            import_orders.ec_inquiry(customer_orders, request)
            return HttpResponse(AppResponse.get({"code": 1, "msg": "All Record(s) imported"}), content_type="json")

        if order_type == "POWERORD":
            url = settings.PPM_URL + "/pwsAPI/GetOrders?type=orderall"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            ec_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            data = None
            try:
                data = ec_res.json()
                customer_orders = [order["OrderNumber"] for order in data]
                import_orders.power_order(customer_orders, request)
                return HttpResponse(AppResponse.get({"code": 1, "msg": "All Record(s) imported"}), content_type="json")
            except Exception:
                return HttpResponse(AppResponse.get({"code": 0, "msg": "Something went wrong"}), content_type="json")

        if order_type == "POWERINQ":
            url = settings.PPM_URL + "/pwsAPI/GetOrders?type=inqall"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            ec_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            response = {"data": []}
            data = None
            try:
                data = ec_res.json()
                customer_orders = [order["OrderNumber"] for order in data]
                import_orders.power_inquery(customer_orders, request)
                return HttpResponse(AppResponse.get({"code": 1, "msg": "All Record(s) imported"}), content_type="json")
            except Exception:
                return HttpResponse(AppResponse.get({"code": 0, "msg": "something went wrong."}), content_type="json")
        return HttpResponse(json.dumps({"code": 1, "msg": "orders_imported"}), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def remove_manage_auto_allocation_data(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("manage_auto_order_allocation", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        manage_auto_all_id = request.POST.get("manage_auto_all_id")
        ManageAutoAllocation.objects.filter(id=manage_auto_all_id).delete()
        manage_auto_allocation = ManageAutoAllocation.objects.values("id", "stop_start_time", "stop_end_time")
        manage_auto_allocation_ = []
        for data in manage_auto_allocation:
            manage_auto_allocation_.append({
                "id" : data["id"],
                "stop_start_time" : str(data["stop_start_time"].strftime("%I:%M %p")),
                "stop_end_time" : str(data["stop_end_time"].strftime("%I:%M %p"))
            })
        response = {"code": 1, "msg": "Stop auto allocation has been deleted.", "manage_auto_allocation" : manage_auto_allocation_}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def add_manage_auto_allocation_data(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("manage_auto_order_allocation", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            stop_start_time = request.POST.get("stop_start_time")
            stop_end_time = request.POST.get("stop_end_time")
            ManageAutoAllocation.objects.create(stop_start_time=stop_start_time, stop_end_time=stop_end_time)
            manage_auto_allocation = ManageAutoAllocation.objects.values("id", "stop_start_time", "stop_end_time")
            manage_auto_allocation_ = []
            for data in manage_auto_allocation:
                manage_auto_allocation_.append({
                    "id" : data["id"],
                    "stop_start_time" : str(data["stop_start_time"].strftime("%I:%M %p")),
                    "stop_end_time" : str(data["stop_end_time"].strftime("%I:%M %p"))
                })
            response = {"code": 1, "msg": "Stop auto allocation has been created.", "manage_auto_allocation" : manage_auto_allocation_}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_orders_in_flow": "orders_in_flow"}])
def orders_in_flow(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_order_in_flow"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/reports/orders_in_flow.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_orders_in_flow(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        recordsTotal = Order.objects.filter(query).values("company__name").distinct().count()

        orders = (
            Order.objects.filter(query)
            .values(
                "company__name", "company__id"
            )
            .annotate(
                schematic=Count("id", filter=Q(order_status="schematic")),
                footprint=Count("id", filter=Q(order_status="footprint")),
                placement=Count("id", filter=Q(order_status="placement")),
                routing=Count("id", filter=Q(order_status="routing")),
                gerber_release=Count("id", filter=Q(order_status="gerber_release")),
                analysis=Count("id", filter=Q(order_status="analysis")),
                incoming=Count("id", filter=Q(order_status="incoming")),
                BOM_incoming=Count("id", filter=Q(order_status="BOM_incoming")),
                SI=Count("id", filter=Q(order_status="SI")),
                SICC=Count("id", filter=Q(order_status="SICC")),
                BOM_CC=Count("id", filter=Q(order_status="BOM_CC")),
                FQC=Count("id", filter=Q(order_status="FQC")),
                panel=Count("id", filter=Q(order_status="panel")),
                upload_panel=Count("id", filter=Q(order_status="upload_panel")),
                exception=Count("id", filter=Q(order_status="exception")),
            )
            .order_by(sort_col)[start : (start + length)]
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for order in orders:
            response["data"].append(
                {
                    "company__name": order["company__name"],
                    "company__id": order["company__id"],
                    "schematic": order["schematic"],
                    "footprint": order["footprint"],
                    "placement": order["placement"],
                    "routing": order["routing"],
                    "gerber_release": order["gerber_release"],
                    "analysis": order["analysis"],
                    "incoming": order["incoming"],
                    "BOM_incoming": order["BOM_incoming"],
                    "SI": order["SI"],
                    "SICC": order["SICC"],
                    "BOM_CC": order["BOM_CC"],
                    "FQC": order["FQC"],
                    "panel": order["panel"],
                    "upload_panel": order["upload_panel"],
                    "exception": order["exception"],
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_orders_in_flow(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_order_in_flow", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        orders = (
            Order.objects.filter(query)
            .values(
                "company__name"
            )
            .annotate(
                schematic=Count("id", filter=Q(order_status="schematic")),
                footprint=Count("id", filter=Q(order_status="footprint")),
                placement=Count("id", filter=Q(order_status="placement")),
                routing=Count("id", filter=Q(order_status="routing")),
                gerber_release=Count("id", filter=Q(order_status="gerber_release")),
                analysis=Count("id", filter=Q(order_status="analysis")),
                incoming=Count("id", filter=Q(order_status="incoming")),
                BOM_incoming=Count("id", filter=Q(order_status="BOM_incoming")),
                SI=Count("id", filter=Q(order_status="SI")),
                SICC=Count("id", filter=Q(order_status="SICC")),
                BOM_CC=Count("id", filter=Q(order_status="BOM_CC")),
                FQC=Count("id", filter=Q(order_status="FQC")),
                panel=Count("id", filter=Q(order_status="panel")),
                upload_panel=Count("id", filter=Q(order_status="upload_panel")),
                exception=Count("id", filter=Q(order_status="exception")),
            ).order_by(order_by)[start : (start + length)]
        )
        query_result = []
        for order in orders:
            query_result.append(
                {
                    "company__name": order["company__name"],
                    "schematic": order["schematic"],
                    "footprint": order["footprint"],
                    "placement": order["placement"],
                    "routing": order["routing"],
                    "gerber_release": order["gerber_release"],
                    "analysis": order["analysis"],
                    "incoming": order["incoming"],
                    "BOM_incoming": order["BOM_incoming"],
                    "SI": order["SI"],
                    "SICC": order["SICC"],
                    "BOM_CC": order["BOM_CC"],
                    "FQC": order["FQC"],
                    "panel": order["panel"],
                    "upload_panel": order["upload_panel"],
                    "exception": order["exception"],

                }
            )
        headers = [
            {"title": "Customer"},
            {"title": "Schematic"},
            {"title": "Footprint"},
            {"title": "Placement"},
            {"title": "Routing"},
            {"title": "Gerber Release"},
            {"title": "Analysis"},
            {"title": "Incoming"},
            {"title": "BOM incoming"},
            {"title": "SI"},
            {"title": "SICC"},
            {"title": "BOM CC"},
            {"title": "FQC"},
            {"title": "Panel"},
            {"title": "Upload Panel"},
            {"title": "Exception"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "orders_in_flow.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_orders(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_orders", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_com_ids = Operator.objects.filter(user__id=request_user_id["id"]).values("company_ids").first()
        if operator_com_ids:
            operator_role = UserGroup.objects.filter(user_id=request_user_id["id"]).values("group__name").first()
            if operator_role["group__name"] == "Engineer":
                if operator_com_ids["company_ids"]:
                    operator_com_ids = list(map(int, operator_com_ids["company_ids"].split(",")))
                    query.add(Q(company_id__in=operator_com_ids), query.connector)
                else:
                    query.add(Q(company_id=None), query.connector)
        operator_id = Operator.objects.filter(show_own_records_only=True, user__username=request.user).first()
        if operator_id:
            query.add(Q(operator=operator_id), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("pws_id"):
            query.add(Q(order_number__icontains=request.POST["pws_id"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("company"):
            query.add(Q(company__name__icontains=request.POST["company"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("order_status"):
            if request.POST.get("order_status").lower() in "order finish":
                query.add(Q(order_status__icontains="finished"), query.connector)
            else:
                query.add(Q(order_status__icontains=request.POST["order_status"]), query.connector)
        if request.POST.get("operator"):
            query.add(Q(operator__user__username__icontains=request.POST["operator"]), query.connector)
        if request.POST.get("order_date"):
            query.add(
                Q(
                    order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        orders = (
            Order.objects.prefetch_related("ordertechparameter_set")
            .filter(query)
            .values(
                "id",
                "order_number",
                "pcb_name",
                "order_date",
                "order_status",
                "operator__user__username",
                "layer",
                "service__name",
                "preparation_due_date",
                "delivery_date",
                "company__name",
                "company__id",
                "order_next_status",
                "order_previous_status",
                "remarks",
                "customer_order_nr",
                "user__user__username",
                "in_time",
                "finished_on",
            )
            .annotate(
                board_thickness=F("ordertechparameter__board_thickness"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )
        remarks_list = [order_["id"] for order_ in orders]
        remarks = Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list).values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        board_thickness_id = [order["board_thickness"] for order in orders if order["board_thickness"]]
        board_thickness = BoardThickness.objects.filter(code__in=board_thickness_id).values("name", "code")
        board_thickness_ = {}
        for board_thick_ in board_thickness:
            board_thickness_[board_thick_["code"]] = board_thick_["name"]

        layers = [order["layer"] for order in orders if order["layer"]]
        layer_ = Layer.objects.filter(code__in=layers).values("name", "code")
        layers_ = {}
        for layer_ in layer_:
            layers_[layer_["code"]] = layer_["name"]

        query_result = []
        for order in orders:
            query_result.append(
                {
                    "order_number": order["order_number"],
                    "customer_order_nr": order["customer_order_nr"],
                    "pcb_name": order["pcb_name"],
                    "layer": layers_[order["layer"]] if order["layer"] in layers_ else "",
                    "service__name": order["service__name"],
                    "board_thickness": board_thickness_[order["board_thickness"]] if order["board_thickness"] in board_thickness_ else "",
                    "user__user__username": order["user__user__username"],
                    "company__name": order["company__name"],
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "preparation_due_date": Util.get_local_time(order["preparation_due_date"], True),
                    "delivery_date": Util.get_local_time(order["delivery_date"], True),
                    "operator__user__username": order["operator__user__username"],
                    "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "",
                    "in_time": Util.get_local_time(order["in_time"], True),
                    "remarks": BeautifulSoup(remarks_disc[order["id"]], features="html5lib").get_text() if order["id"] in remarks_disc else "",
                    "finished_on": Util.get_local_time(order["finished_on"], True),
                    "order_next_status": dict(order_status)[order["order_next_status"]] if order["order_next_status"] in dict(order_status) else "",
                    "order_previous_status": dict(order_status)[order["order_previous_status"]] if order["order_previous_status"] in dict(order_status) else "",
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "order number"},
            {"title": "PCB name"},
            {"title": "Layer"},
            {"title": "Service"},
            {"title": "Board thickness"},
            {"title": "Username"},
            {"title": "Customer"},
            {"title": "Order date"},
            {"title": "preparation due date"},
            {"title": "Delivery date"},
            {"title": "Engineer"},
            {"title": "Process"},
            {"title": "In time"},
            {"title": "Remark"},
            {"title": "Order finish date"},
            {"title": "Next status"},
            {"title": "Previous status"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "order.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_nc_details(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_nc_details_master", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        if request.POST.get("name"):
            query.add(Q(name__icontains=request.POST["name"]), query.connector)
        if request.POST.get("created_by"):
            query.add(Q(created_by__username__icontains=request.POST["created_by"]), query.connector)
        if request.POST.get("created_on"):
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("created_on").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )

        query.add(Q(is_deleted=False), query.connector)
        nc_details = NcCategory.objects.filter(query).values("id", "name", "parent_id__name", "created_by__username", "created_on").order_by(order_by)[start : (start + length)]
        query_result = []
        for nc_detail in nc_details:
            query_result.append(
                {
                    "name": nc_detail["name"],
                    "parent_id": nc_detail["parent_id__name"],
                    "created_by": nc_detail["created_by__username"],
                    "created_on": Util.get_local_time(nc_detail["created_on"], True),
                }
            )
        headers = [
            {"title": "Category name"},
            {"title": "Related category"},
            {"title": "Created by"},
            {"title": "Created on"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "NC_details_master.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_user_efficiencies(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_user_efficiency", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        if request.POST.get("company"):
            query.add(Q(company__name__icontains=request.POST["company"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("process"):
            query.add(Q(process__name__icontains=request.POST["process"]), query.connector)
        if request.POST.get("layer"):
            query.add(Q(layer__icontains=request.POST["layer"]), query.connector)
        if request.POST.get("multi_layer"):
            query.add(Q(multi_layer__icontains=request.POST["multi_layer"]), query.connector)

        query.add(Q(is_deleted=False), query.connector)
        user_efficiencies = (
            Efficiency.objects.filter(query)
            .values("id", "company__name", "service__name", "process__name", "layer", "multi_layer")
            .order_by(order_by)[start : (start + length)]
        )
        query_result = []
        for user_efficiency in user_efficiencies:
            query_result.append(
                {
                    "company__name": user_efficiency["company__name"],
                    "service__name": user_efficiency["service__name"],
                    "process__name": user_efficiency["process__name"],
                    "layer": user_efficiency["layer"],
                    "multi_layer": user_efficiency["multi_layer"],
                }
            )
        headers = [
            {"title": "Customer"},
            {"title": "Service"},
            {"title": "Process"},
            {"title": "1/2 Layer"},
            {"title": "Multi layer"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "user_efficiency.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_order_allocations(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_order_allocation", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        company_id = request.POST.get("company_id")
        process_id = request.POST.get("process_id")
        if company_id != "":
            query.add(Q(company=company_id), query.connector)
        if process_id != "":
            process = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id=process_id).values("code").first()
            query.add(Q(order_status=process["code"]), query.connector)
        query.add(~Q(order_status__in=["cancel", "exception", "finished", "panel", "upload_panel"]), query.connector)
        orders = (
            Order.objects.filter(query)
            .values(
                "id",
                "company__name",
                "company",
                "service",
                "order_number",
                "service__name",
                "layer",
                "delivery_term",
                "pcb_name",
                "delivery_term",
                "order_date",
                "operator__user__username",
                "delivery_date",
                "order_status",
                "preparation_due_date",
                "pcb_name",
                "in_time",
                "customer_order_nr",
                "act_delivery_date",
            )
            .annotate(
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )
        layers_code = [order_["layer"] for order_ in orders]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)
        query_result = []
        for order in orders:
            query_result.append(
                {
                    "order_number": order["order_number"],
                    "customer_order_nr": order["customer_order_nr"],
                    "preparation_due_date": Util.get_local_time(order["preparation_due_date"], True),
                    "layer": layers[order["layer"]] if order["layer"] in layers else None,
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "delivery_term": dict(delivery_term)[order["delivery_term"]] if order["delivery_term"] in dict(delivery_term) else "",
                    "delivery_date": Util.get_local_time(order["act_delivery_date"], True),
                    "pcb_name": order["pcb_name"],
                    "in_time": Util.get_local_time(order["in_time"], True),
                    "company__name": order["company__name"],
                    "operator__user__username": order["operator__user__username"],
                    "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "",
                    "service__name": order["service__name"],
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Preparation due date"},
            {"title": "Layers"},
            {"title": "Order date"},
            {"title": "Delivery term"},
            {"title": "Delivery date"},
            {"title": "Pcb name"},
            {"title": "system intime"},
            {"title": "Customer"},
            {"title": "Operator name"},
            {"title": "Order status"},
            {"title": "Service name"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "order_allocations.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_job_processing(request):
    try:
        query = Q()
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_com_ids = Operator.objects.filter(user__id=request_user_id["id"]).values("company_ids").first()
        if operator_com_ids:
            operator_role = UserGroup.objects.filter(user_id=request_user_id["id"]).values("group__name").first()
            if operator_role["group__name"] == "Engineer":
                if operator_com_ids["company_ids"]:
                    operator_com_ids = list(map(int, operator_com_ids["company_ids"].split(",")))
                    query.add(Q(company_id__in=operator_com_ids), query.connector)
                else:
                    query.add(Q(company_id=None), query.connector)
        operator_id = Operator.objects.filter(show_own_records_only=True, user__username=request.user).first()
        if operator_id:
            query.add(Q(operator=operator_id), query.connector)
        if request.POST.get("status"):
            query.add(Q(order_status=request.POST.get("status")), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("operator"):
            query.add(Q(operator__user__username__icontains=request.POST["operator"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("customer"):
            query.add(Q(company__name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("order_date"):
            query.add(
                Q(
                    order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        orders = (
            Order.objects.prefetch_related("ordertechparameter_set")
            .filter(query)
            .values(
                "id",
                "order_status",
                "order_date",
                "preparation_due_date",
                "delivery_date",
                "order_number",
                "pcb_name",
                "service__name",
                "order_next_status",
                "order_previous_status",
                "remarks",
                "customer_order_nr",
                "layer",
                "in_time",
                "panel_no",
                "panel_qty"
            )
            .annotate(
                operator=F("operator__user__username"),
                operator_id=F("operator__user__id"),
                customer=F("company__name"),
                tool_nr=F("ordertechparameter__tool_nr"),
                board_thickness=F("ordertechparameter__board_thickness"),
                material_tg=F("ordertechparameter__material_tg"),
                bottom_solder_mask=F("ordertechparameter__bottom_solder_mask"),
                top_solder_mask=F("ordertechparameter__top_solder_mask"),
                top_legend=F("ordertechparameter__top_legend"),
                bottom_legend=F("ordertechparameter__bottom_legend"),
                surface_finish=F("ordertechparameter__surface_finish"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )
        remarks_list = [order_["id"] for order_ in orders]
        remarks = Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list).values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        layers_code = [order_["layer"] for order_ in orders]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)
        query_result = []
        for order in orders:
            query_result.append(
                {
                    "order_number": order["order_number"],
                    "customer_order_nr": order["customer_order_nr"],
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "in_time": Util.get_local_time(order["in_time"], True),
                    "preparation_due_date": Util.get_local_time(order["preparation_due_date"], True),
                    "delivery_date": Util.get_local_time(order["delivery_date"], True),
                    "pcb_name": order["pcb_name"],
                    "tool_nr": order["tool_nr"],
                    "layer": layers[order["layer"]] if order["layer"] in layers else None,
                    "customer": order["customer"],
                    "service": order["service__name"],
                    "operator": order["operator"],
                    "remarks": BeautifulSoup(remarks_disc[order["id"]], features="html5lib").get_text() if order["id"] in remarks_disc else "",
                    "order_next_status": dict(order_status)[order["order_next_status"]] if order["order_next_status"] in dict(order_status) else " ",
                    "order_previous_status": dict(order_status)[order["order_previous_status"]] if order["order_previous_status"] in dict(order_status) else " ",
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Order date"},
            {"title": "In time"},
            {"title": "Preparation due date"},
            {"title": "Delivery date"},
            {"title": "PCB name"},
            {"title": "Tool nr."},
            {"title": "PCB type"},
            {"title": "Customer"},
            {"title": "Service"},
            {"title": "Engineer"},
            {"title": "Remarks"},
            {"title": "Next stage"},
            {"title": "Previous stage"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "job_processing.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_job_processing_(request):
    try:
        query = Q()
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_com_ids = Operator.objects.filter(user__id=request_user_id["id"]).values("company_ids").first()
        if operator_com_ids:
            operator_role = UserGroup.objects.filter(user_id=request_user_id["id"]).values("group__name").first()
            if operator_role["group__name"] == "Engineer":
                if operator_com_ids["company_ids"]:
                    operator_com_ids = list(map(int, operator_com_ids["company_ids"].split(",")))
                    query.add(Q(company_id__in=operator_com_ids), query.connector)
                else:
                    query.add(Q(company_id=None), query.connector)
        operator_id = Operator.objects.filter(show_own_records_only=True, user__username=request.user).first()
        if operator_id:
            query.add(Q(operator=operator_id), query.connector)
        if request.POST.get("status"):
            query.add(Q(order_status=request.POST.get("status")), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("operator"):
            query.add(Q(operator__user__username__icontains=request.POST["operator"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("customer"):
            query.add(Q(company__name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        if request.POST.get("order_date"):
            query.add(
                Q(
                    order_date__range=[
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("order_date").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        orders = (
            Order.objects.prefetch_related("ordertechparameter_set")
            .filter(query)
            .values(
                "id",
                "order_status",
                "order_date",
                "preparation_due_date",
                "delivery_date",
                "order_number",
                "pcb_name",
                "service__name",
                "order_next_status",
                "order_previous_status",
                "remarks",
                "customer_order_nr",
                "layer",
                "in_time",
                "panel_no",
                "panel_qty"
            )
            .annotate(
                operator=F("operator__user__username"),
                operator_id=F("operator__user__id"),
                customer=F("company__name"),
                tool_nr=F("ordertechparameter__tool_nr"),
                board_thickness=F("ordertechparameter__board_thickness"),
                material_tg=F("ordertechparameter__material_tg"),
                bottom_solder_mask=F("ordertechparameter__bottom_solder_mask"),
                top_solder_mask=F("ordertechparameter__top_solder_mask"),
                top_legend=F("ordertechparameter__top_legend"),
                bottom_legend=F("ordertechparameter__bottom_legend"),
                surface_finish=F("ordertechparameter__surface_finish"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__endswith=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )
        remarks_list = [order_["id"] for order_ in orders]
        remarks = Remark.objects.filter(content_type_id__model="order", entity_id__in=remarks_list).values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]
        layers_code = [order_["layer"] for order_ in orders]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)
        if request.POST.get("status") == "panel":
            query_result = []
            for order in orders:
                query_result.append(
                    {
                        "order_number": order["order_number"],
                        "customer_order_nr": order["customer_order_nr"],
                        "order_date": Util.get_local_time(order["order_date"], True),
                        "in_time": Util.get_local_time(order["in_time"], True),
                        "pcb_name": order["pcb_name"],
                        "tool_nr": order["tool_nr"],
                        "layer": layers[order["layer"]] if order["layer"] in layers else None,
                        "customer": order["customer"],
                        "remarks": BeautifulSoup(remarks_disc[order["id"]], features="html5lib").get_text() if order["id"] in remarks_disc else "",
                        "board_thickness": order["board_thickness"],
                        "material_tg": dict(material_tg)[order["material_tg"]] if order["material_tg"] in dict(material_tg) else " ",
                        "service": order["service__name"],
                        "operator": order["operator"],
                        "bottom_solder_mask": dict(bottom_solder_mask)[order["bottom_solder_mask"]] if order["bottom_solder_mask"] in dict(bottom_solder_mask) else " ",
                        "top_solder_mask": dict(top_solder_mask)[order["top_solder_mask"]] if order["top_solder_mask"] in dict(top_solder_mask) else " ",
                        "top_legend": dict(top_legend)[order["top_legend"]] if order["top_legend"] in dict(top_legend) else " ",
                        "bottom_legend": dict(bottom_legend)[order["bottom_legend"]] if order["bottom_legend"] in dict(bottom_legend) else " ",
                        "surface_finish": dict(surface_finish)[order["surface_finish"]] if order["surface_finish"] in dict(surface_finish) else " ",
                        "order_next_status": dict(order_status)[order["order_next_status"]] if order["order_next_status"] in dict(order_status) else " ",
                        "order_previous_status": dict(order_status)[order["order_previous_status"]] if order["order_previous_status"] in dict(order_status) else " ",
                    }
                )
            headers = [
                {"title": "PWS ID"},
                {"title": "Order number"},
                {"title": "Order date"},
                {"title": "In time"},
                {"title": "PCB name"},
                {"title": "Tool nr."},
                {"title": "PCB type"},
                {"title": "Customer"},
                {"title": "Remarks"},
                {"title": "Board thickness"},
                {"title": "Material tg"},
                {"title": "Service"},
                {"title": "Engineer"},
                {"title": "Soldermask bottom"},
                {"title": "Soldermask top"},
                {"title": "Legend top"},
                {"title": "Legend bottom"},
                {"title": "Surface finish"},
                {"title": "Next stage"},
                {"title": "Previous stage"},
            ]
            return Util.export_to_xls(headers, query_result[:5000], "job_processing.xls")
        else:
            query_result = []
            for order in orders:
                query_result.append(
                    {
                        "order_number": order["order_number"],
                        "customer_order_nr": order["customer_order_nr"],
                        "order_date": Util.get_local_time(order["order_date"], True),
                        "in_time": Util.get_local_time(order["in_time"], True),
                        "pcb_name": order["pcb_name"],
                        "tool_nr": order["tool_nr"],
                        "panel_no": order["panel_no"],
                        "panel_qty": order["panel_qty"],
                        "layer": layers[order["layer"]] if order["layer"] in layers else None,
                        "customer": order["customer"],
                        "remarks": BeautifulSoup(remarks_disc[order["id"]], features="html5lib").get_text() if order["id"] in remarks_disc else "",
                        "board_thickness": order["board_thickness"],
                        "material_tg": dict(material_tg)[order["material_tg"]] if order["material_tg"] in dict(material_tg) else " ",
                        "service": order["service__name"],
                        "operator": order["operator"],
                        "bottom_solder_mask": dict(bottom_solder_mask)[order["bottom_solder_mask"]] if order["bottom_solder_mask"] in dict(bottom_solder_mask) else " ",
                        "top_solder_mask": dict(top_solder_mask)[order["top_solder_mask"]] if order["top_solder_mask"] in dict(top_solder_mask) else " ",
                        "top_legend": dict(top_legend)[order["top_legend"]] if order["top_legend"] in dict(top_legend) else " ",
                        "bottom_legend": dict(bottom_legend)[order["bottom_legend"]] if order["bottom_legend"] in dict(bottom_legend) else " ",
                        "surface_finish": dict(surface_finish)[order["surface_finish"]] if order["surface_finish"] in dict(surface_finish) else " ",
                        "order_next_status": dict(order_status)[order["order_next_status"]] if order["order_next_status"] in dict(order_status) else " ",
                        "order_previous_status": dict(order_status)[order["order_previous_status"]] if order["order_previous_status"] in dict(order_status) else " ",
                    }
                )
            headers = [
                {"title": "PWS ID"},
                {"title": "Order number"},
                {"title": "Order date"},
                {"title": "In time"},
                {"title": "PCB name"},
                {"title": "Tool nr."},
                {"title": "Panel number"},
                {"title": "Panel quantity"},
                {"title": "PCB type"},
                {"title": "Customer"},
                {"title": "Remarks"},
                {"title": "Board thickness"},
                {"title": "Material tg"},
                {"title": "Service"},
                {"title": "Engineer"},
                {"title": "Soldermask bottom"},
                {"title": "Soldermask top"},
                {"title": "Legend top"},
                {"title": "Legend bottom"},
                {"title": "Surface finish"},
                {"title": "Next stage"},
                {"title": "Previous stage"},
            ]
            return Util.export_to_xls(headers, query_result[:5000], "job_processing.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exception_order_cancel(request, order_id):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            exception_id = request.POST.get("exception_id")
            if Util.has_perm("cancel_order_exception", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order = Order.objects.filter(id=order_id).values("order_status").first()
            Order.objects.filter(id=order_id).update(order_status="cancel", in_time=datetime.datetime.now(), order_next_status=None, order_previous_status="exception")
            Order_Attachment.objects.filter(object_id=order_id, file_type__code="EXCEPTION").update(deleted=True)
            OrderException.objects.filter(id=exception_id).update(order_in_exception=True)
            history_status = (
                "Order has been " + " " + "<b>" + " " + "Cancel" + " " + "</b>"
                + " " + "from" + " " + "<b>" + " " + dict(order_status)[order["order_status"]] + " " + "</b>"
            )
            c_ip = base_views.get_client_ip(request)
            action = AuditAction.UPDATE
            log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, history_status)
            log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, "Order has been Cancelled")
            order_detail = Order.objects.filter(id=order_id).values("company__name", "customer_order_nr", "remarks", "service__name", "pcb_name", "layer").first()
            order_company = Order.objects.filter(id=order_id).values("company", "user_id").first()
            layer = Layer.objects.filter(code=order_detail["layer"]).values("code", "name").first()
            if layer:
                layers = layer["name"]
            else:
                layers = ""
            user_cc_mail = CompanyUser.objects.filter(id=order_company["user_id"]).values("user__email").first()
            cc_mail = user_cc_mail["user__email"] if user_cc_mail else ""
            email_id = CompanyParameter.objects.filter(company=order_company["company"]).values("ord_rec_mail", "mail_from").first()
            mail_from = email_id["mail_from"] if email_id["mail_from"] else None
            email_id = email_id["ord_rec_mail"]
            if email_id:
                email_id = [email_ids for email_ids in email_id.split(",")]
                subject = "Order cancelled - " + order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
                head = order_detail["company__name"] + " #" + order_detail["customer_order_nr"]
                title = "Dear customer,<br>Order " + order_detail["customer_order_nr"] + " has been cancelled"
                message = render_to_string(
                    "pws/mail_order.html",
                    {
                        "head": head,
                        "title": title,
                        "layers": layers,
                        "order_detail": order_detail,
                    },
                )
                send_mail(True, "public", [*email_id], subject, message, "", [cc_mail], mail_from)
            response = {"code": 1, "msg": "Order canceled successfully."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_live_prep_tracking": "live_prep_tracking_report"}])
def live_prep_tracking_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_live_prep_tracking_report"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/reports/live_prep_tracking_report.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_live_prep_tracking_report(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "layer":
            sort_col = "layer_column"
        if sort_col == "-layer":
            sort_col = "-layer_column"
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("operator"):
            query.add(Q(operator__user__username__icontains=request.POST["operator"]), query.connector)
        if request.POST.get("customer"):
            query.add(Q(company__name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        query.add(~Q(operator=None), query.connector)
        if "load_data" in request.POST:
            recordsTotal = Order.objects.filter(query).count()
            orders = (
                Order.objects.filter(query)
                .values("id", "order_number", "customer_order_nr", "service", "service__name", "layer", "company", "order_status")
                .annotate(
                    customer=F("company__name"),
                    operator=F("operator__user__username"),
                    layer_column=Case(
                        When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                        When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                        When(layer="", then=None),
                        default=None,
                        output_field=IntegerField(),
                    ),
                )
                .order_by(sort_col)[start : (start + length)]
            )
            layers_code = [order_["layer"] for order_ in orders]
            layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
            layers = Util.get_dict_from_quryset("code", "name", layer)
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }

            order_ids = [x["id"] for x in orders]
            auditlog = Auditlog.objects.filter(object_id__in=order_ids, content_type_id__model="order", descr__endswith=" is reserved").values("action_on", "object_id")
            reserve_time = Util.get_dict_from_quryset("object_id", "action_on", auditlog)
            layer_pt = {}
            efficiencies = Efficiency.objects.filter(is_deleted=False).values("company_id", "service_id", "process__code", "layer", "multi_layer")
            for rec in orders:
                for efficiency in efficiencies:
                    layer = rec["layer"] if rec["layer"] != "" and rec["layer"] is not None else ""
                    layer_point = ""
                    layer_ = ""
                    layer_ = layer[0:2]
                    if efficiency is None:
                        layer_ = ""
                        layer_point = 0
                    else:
                        if layer != "":
                            if int(layer_) <= 2:
                                if efficiency["company_id"] == rec["company"] and efficiency["service_id"] == rec["service"] and efficiency["process__code"] == rec["order_status"]:
                                    layer_ = "1/2 Layers"
                                    layer_point = efficiency["layer"] if efficiency["layer"] is not None else 0
                                    layer_pt[rec["id"]] = layer_point
                            else:
                                if efficiency["company_id"] == rec["company"] and efficiency["service_id"] == rec["service"] and efficiency["process__code"] == rec["order_status"]:
                                    layer_ = "Multi Layers"
                                    layer_point = efficiency["multi_layer"] if efficiency["multi_layer"] is not None else 0
                                    layer_pt[rec["id"]] = layer_point
                        else:
                            layer_ = ""
                            layer_point = 0
            for data in orders:
                action_date = Util.get_local_time(reserve_time[data["id"]], True) if data["id"] in reserve_time else ""
                date = datetime.datetime.now() - reserve_time[data["id"]]
                duration_in_s = date.total_seconds()
                minutes = divmod(duration_in_s, 60)[0]
                preparation_time = str(int(minutes)) + " " + "minutes"
                if data["id"] in layer_pt:
                    if int(minutes) <= layer_pt[data["id"]]:
                        on_time = "On time"
                    else:
                        on_time = "<span style='color:orange;'>Delay</span>"
                else:
                    on_time = ""
                response["data"].append(
                    {
                        "id": data["id"],
                        "order_id": data["id"],
                        "order_number": data["order_number"],
                        "customer_order_nr": data["customer_order_nr"],
                        "customer": data["customer"],
                        "service": data["service__name"],
                        "layer": layers[data["layer"]] if data["layer"] in layers else None,
                        "operator": data["operator"],
                        "resreve_time" : action_date,
                        "ontime": on_time,
                        "prep_time": preparation_time,
                        "order_status": dict(order_status)[data["order_status"]] if data["order_status"] in dict(order_status) else "",
                        "sort_col": sort_col,
                        "recordsTotal": recordsTotal,
                    }
                )
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def export_live_prep_tracking_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_live_prep_tracking_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        elif request.POST.get("display_data_list"):
            display_data_list = list(map(int, request.POST.get("display_data_list").split(",")))
            query.add(Q(id__in=display_data_list), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("operator"):
            query.add(Q(operator__user__username__icontains=request.POST["operator"]), query.connector)
        if request.POST.get("customer"):
            query.add(Q(company__name__icontains=request.POST["customer"]), query.connector)
        if request.POST.get("service"):
            query.add(Q(service__name__icontains=request.POST["service"]), query.connector)
        query.add(~Q(operator=None), query.connector)
        orders = (
            Order.objects.filter(query)
            .values("id", "order_number", "customer_order_nr", "service", "service__name", "layer", "company", "order_status")
            .annotate(
                customer=F("company__name"),
                operator=F("operator__user__username"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )
        layers_code = [order_["layer"] for order_ in orders]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)

        order_ids = [x["id"] for x in orders]
        auditlog = Auditlog.objects.filter(object_id__in=order_ids, content_type_id__model="order", descr__endswith=" is reserved").values("action_on", "object_id")
        reserve_time = Util.get_dict_from_quryset("object_id", "action_on", auditlog)
        layer_pt = {}

        efficiencies = Efficiency.objects.values("company_id", "service_id", "process__code", "layer", "multi_layer")
        for rec in orders:
            for efficiency in efficiencies:
                layer = rec["layer"] if rec["layer"] != "" and rec["layer"] is not None else ""
                layer_point = ""
                layer_ = ""
                layer_ = layer[0:2]
                if efficiency is None:
                    layer_ = ""
                    layer_point = 0
                else:
                    if layer != "":
                        if int(layer_) <= 2:
                            if efficiency["company_id"] == rec["company"] and efficiency["service_id"] == rec["service"] and efficiency["process__code"] == rec["order_status"]:
                                layer_ = "1/2 Layers"
                                layer_point = efficiency["layer"] if efficiency["layer"] is not None else 0
                                layer_pt[rec["id"]] = layer_point
                        else:
                            if efficiency["company_id"] == rec["company"] and efficiency["service_id"] == rec["service"] and efficiency["process__code"] == rec["order_status"]:
                                layer_ = "Multi Layers"
                                layer_point = efficiency["multi_layer"] if efficiency["multi_layer"] is not None else 0
                                layer_pt[rec["id"]] = layer_point
                    else:
                        layer_ = ""
                        layer_point = 0
        query_result = []
        for data in orders:
            action_date = Util.get_local_time(reserve_time[data["id"]], True) if data["id"] in reserve_time else ""
            date = datetime.datetime.now() - reserve_time[data["id"]]
            duration_in_s = date.total_seconds()
            minutes = divmod(duration_in_s, 60)[0]
            preparation_time = str(int(minutes)) + " " + "minutes"
            if data["id"] in layer_pt:
                if int(minutes) <= layer_pt[data["id"]]:
                    on_time = "On time"
                else:
                    on_time = "Delay"
            else:
                on_time = ""
            query_result.append(
                {
                    "order_number": data["order_number"],
                    "customer_order_nr": data["customer_order_nr"],
                    "customer": data["customer"],
                    "resreve_time" : action_date,
                    "service": data["service__name"],
                    "layer": layers[data["layer"]] if data["layer"] in layers else None,
                    "prep_time": preparation_time,
                    "ontime": on_time,
                    "operator": data["operator"],
                    "order_status": dict(order_status)[data["order_status"]] if data["order_status"] in dict(order_status) else "",
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Customer"},
            {"title": "Reserved on"},
            {"title": "Service"},
            {"title": "Layers"},
            {"title": "Minutes till now"},
            {"title": "Ontime"},
            {"title": "Operator name"},
            {"title": "Order status"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "live_prep_tracking_report.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_user_efficiency": "user_efficiency_report"}])
def user_efficiency_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_user_efficiency_report", "can_edit"]
        permissions = Util.get_permission_role(user, perms)
        today = datetime.datetime.strptime(str(datetime.datetime.now()), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m")
        return render(request, "pws/reports/user_efficiency_report.html", {"today": today, "permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_user_efficiency_reports(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if "load_data" in request.POST:
            date_range = request.POST.get("today_date_")
            start_date_ = date_range.split("-")
            start_date = date_range + "-1"
            any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
            next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
            Last_date = next_month - datetime.timedelta(days=next_month.day)
            dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
            last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
            last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            start_dt_ = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
            date_range = last_date_time - start_dt_
            dates = list()
            for days in range(0, date_range.days + 1):
                dates.append((start_dt_ + datetime.timedelta(days)).strftime('%Y-%m-%d'))
            dates_query = []
            for date in dates:
                dates_query.append(datetime.datetime.strptime(str(date) + " 06:00", "%Y-%m-%d %H:%M"))
            date29 = Q()
            if len(dates) > 29:
                date29.add(Q(created_on__range=[dates_query[28], dates_query[29]]), date29.connector)
            else:
                date29.add(Q(created_on__day__range=["29", "30"]), date29.connector)
            date30 = Q()
            if len(dates) > 30:
                date30.add(Q(created_on__range=[dates_query[29], dates_query[30]]), date30.connector)
            else:
                date30.add(Q(created_on__day__range=["30", "31"]), date30.connector)
            date31 = Q()
            if len(dates) > 31:
                date31.add(Q(created_on__range=[dates_query[30], dates_query[31]]), date31.connector)
            else:
                date31.add(Q(created_on__day__range=["31", "1"]), date31.connector)
            month_sundays = len([1 for i in calendar.monthcalendar(int(start_date_[0]), int(start_date_[1])) if i[6] != 0])
            month_days = calendar.monthrange(int(start_date_[0]), int(start_date_[1]))[1]
            total_days = int(month_days) - int(month_sundays)

            # for current month days count till today without sunday's
            today_ = datetime.datetime.now()
            today = datetime.date(today_.year, today_.month, today_.day)
            current_month_first_day_ = today_.replace(day=1)
            current_month_first_day = datetime.date(current_month_first_day_.year, current_month_first_day_.month, current_month_first_day_.day)
            delta = today - current_month_first_day
            date_list = []
            for i in range(delta.days + 1):
                day = current_month_first_day + datetime.timedelta(days=i)
                date_list.append(day)
            sundays = 0
            for date_ in date_list:
                if date_.weekday() == 6:
                    sundays += 1
            total_days_month_till_today = int(len(date_list)) - int(sundays)

            if "is_user_wise" in request.POST:
                if sort_col == "pi" or sort_col == "working_pi":
                    sort_col = "total_efficiency"
                if sort_col == "-pi" or sort_col == "-working_pi":
                    sort_col = "-total_efficiency"
                query_user = Q()
                query_remark = Q()
                nc_count = Q()
                query_user.add(
                    Q(
                        created_on__range=[
                            datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query_user.connector,
                )
                query_remark.add(
                    Q(
                        prep_on__range=[
                            datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query_remark.connector,
                )
                query_user.add(~Q(operator=None), query_user.connector)
                nc_count.add(
                    Q(
                        non_conformity__created_on__range=[
                            datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                        ]
                    ),
                    nc_count.connector,
                )
                request_user = request.user.id
                request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
                operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
                if operator_id:
                    if operator_id["operator_type"]:
                        if operator_id["operator_type"] == "PLANET_ENG":
                            query_user.add(Q(operator__user__id=request_user_id["id"]), query_user.connector)
                sort_col_ = [
                    "user_role", "-user_role", "rejection", "-rejection", "remarks", "-remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7",
                    "date8", "date9", "date10", "date11", "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21",
                    "date22", "date23", "date24", "date25", "date26", "date27", "date28", "date29", "date30", "date31", "-date1", "-date2", "-date3", "-date4",
                    "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11", "-date12", "-date13", "-date14", "-date15", "-date16", "-date17",
                    "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25", "-date26", "-date27", "-date28", "-date29",
                    "-date30", "-date31", "manual_days", "-manual_days"
                ]
                userefficiencylogs_ = (
                    UserEfficiencyLog.objects.filter(query_user)
                    .values(
                        "operator__user__username",
                        "operator__user__id",
                        "operator",
                        "operator__sub_group_of_operator__sub_group_name"
                    )
                ).order_by(sort_col if sort_col not in sort_col_ else "operator__user__username")
                userefficiencylogs = userefficiencylogs_.annotate(
                    target_efficiency=Max("target_efficiency"),
                    minimum_efficiency=Max("minimum_efficiency"),
                    date1=Sum("layer_point", filter=Q(created_on__range=[dates_query[0], dates_query[1]])),
                    date2=Sum("layer_point", filter=Q(created_on__range=[dates_query[1], dates_query[2]])),
                    date3=Sum("layer_point", filter=Q(created_on__range=[dates_query[2], dates_query[3]])),
                    date4=Sum("layer_point", filter=Q(created_on__range=[dates_query[3], dates_query[4]])),
                    date5=Sum("layer_point", filter=Q(created_on__range=[dates_query[4], dates_query[5]])),
                    date6=Sum("layer_point", filter=Q(created_on__range=[dates_query[5], dates_query[6]])),
                    date7=Sum("layer_point", filter=Q(created_on__range=[dates_query[6], dates_query[7]])),
                    date8=Sum("layer_point", filter=Q(created_on__range=[dates_query[7], dates_query[8]])),
                    date9=Sum("layer_point", filter=Q(created_on__range=[dates_query[8], dates_query[9]])),
                    date10=Sum("layer_point", filter=Q(created_on__range=[dates_query[9], dates_query[10]])),
                    date11=Sum("layer_point", filter=Q(created_on__range=[dates_query[10], dates_query[11]])),
                    date12=Sum("layer_point", filter=Q(created_on__range=[dates_query[11], dates_query[12]])),
                    date13=Sum("layer_point", filter=Q(created_on__range=[dates_query[12], dates_query[13]])),
                    date14=Sum("layer_point", filter=Q(created_on__range=[dates_query[13], dates_query[14]])),
                    date15=Sum("layer_point", filter=Q(created_on__range=[dates_query[14], dates_query[15]])),
                    date16=Sum("layer_point", filter=Q(created_on__range=[dates_query[15], dates_query[16]])),
                    date17=Sum("layer_point", filter=Q(created_on__range=[dates_query[16], dates_query[17]])),
                    date18=Sum("layer_point", filter=Q(created_on__range=[dates_query[17], dates_query[18]])),
                    date19=Sum("layer_point", filter=Q(created_on__range=[dates_query[18], dates_query[19]])),
                    date20=Sum("layer_point", filter=Q(created_on__range=[dates_query[19], dates_query[20]])),
                    date21=Sum("layer_point", filter=Q(created_on__range=[dates_query[20], dates_query[21]])),
                    date22=Sum("layer_point", filter=Q(created_on__range=[dates_query[21], dates_query[22]])),
                    date23=Sum("layer_point", filter=Q(created_on__range=[dates_query[22], dates_query[23]])),
                    date24=Sum("layer_point", filter=Q(created_on__range=[dates_query[23], dates_query[24]])),
                    date25=Sum("layer_point", filter=Q(created_on__range=[dates_query[24], dates_query[25]])),
                    date26=Sum("layer_point", filter=Q(created_on__range=[dates_query[25], dates_query[26]])),
                    date27=Sum("layer_point", filter=Q(created_on__range=[dates_query[26], dates_query[27]])),
                    date28=Sum("layer_point", filter=Q(created_on__range=[dates_query[27], dates_query[28]])),
                    date29=Sum("layer_point", filter=date29),
                    date30=Sum("layer_point", filter=date30),
                    date31=Sum("layer_point", filter=date31),
                    total_efficiency=Sum("layer_point"),
                )
                user_ids = [user["operator__user__id"] for user in userefficiencylogs]
                user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")
                role_data = {}
                for user_role in user_roles:
                    role_data[user_role["user_id"]] = user_role["group__name"]

                nc_count = (
                    NonConformityDetail.objects.filter(nc_count, operator__user__id__in=user_ids)
                    .values(
                        "operator__user__username",
                    )
                    .annotate(
                        total_nc_remark=Count("id", filter=Q(non_conformity__nc_type="remark")),
                        total_nc_rejection=Count("id", filter=Q(non_conformity__nc_type="rejection")),
                    )
                )
                nc_remark = {}
                for nc_count_ in nc_count:
                    nc_remark[nc_count_["operator__user__username"]] = nc_count_["total_nc_remark"]

                nc_rejection = {}
                for nc_count_ in nc_count:
                    nc_rejection[nc_count_["operator__user__username"]] = nc_count_["total_nc_rejection"]

                remarks_list = [userefficiencylogs_["operator"] for userefficiencylogs_ in userefficiencylogs]
                remarks = Remark.objects.filter(query_remark, entity_id__in=remarks_list, content_type_id__model="operator").values("entity_id", "remark").order_by("created_on")
                remarks_disc = {}
                for remark in remarks:
                    if remark["entity_id"] not in remarks_disc:
                        remarks_disc[remark["entity_id"]] = remark["remark"]
                    else:
                        remarks_disc[remark["entity_id"]] = remark["remark"]
                recordsTotal = (
                    UserEfficiencyLog.objects.filter(query_user)
                    .values(
                        "operator__user__username",
                        "operator__user__id",
                    )
                ).distinct().count()
                response = {
                    "draw": request.POST["draw"],
                    "recordsTotal": recordsTotal,
                    "recordsFiltered": recordsTotal,
                    "data": [],
                }
                for userefficiencylog in userefficiencylogs:
                    manual_days_ = []
                    for id in range(1, 32):
                        date = "date" + str(id)
                        if userefficiencylog[date] is not None:
                            manual_days_.append(1)
                    manual_days = len(manual_days_)
                    response["data"].append(
                        {
                            "operator__user__username": userefficiencylog["operator__user__username"],
                            "operator": userefficiencylog["operator"],
                            "date1": userefficiencylog["date1"] if userefficiencylog["date1"] else 0,
                            "date2": userefficiencylog["date2"] if userefficiencylog["date2"] else 0,
                            "date3": userefficiencylog["date3"] if userefficiencylog["date3"] else 0,
                            "date4": userefficiencylog["date4"] if userefficiencylog["date4"] else 0,
                            "date5": userefficiencylog["date5"] if userefficiencylog["date5"] else 0,
                            "date6": userefficiencylog["date6"] if userefficiencylog["date6"] else 0,
                            "date7": userefficiencylog["date7"] if userefficiencylog["date7"] else 0,
                            "date8": userefficiencylog["date8"] if userefficiencylog["date8"] else 0,
                            "date9": userefficiencylog["date9"] if userefficiencylog["date9"] else 0,
                            "date10": userefficiencylog["date10"] if userefficiencylog["date10"] else 0,
                            "date11": userefficiencylog["date11"] if userefficiencylog["date11"] else 0,
                            "date12": userefficiencylog["date12"] if userefficiencylog["date12"] else 0,
                            "date13": userefficiencylog["date13"] if userefficiencylog["date13"] else 0,
                            "date14": userefficiencylog["date14"] if userefficiencylog["date14"] else 0,
                            "date15": userefficiencylog["date15"] if userefficiencylog["date15"] else 0,
                            "date16": userefficiencylog["date16"] if userefficiencylog["date16"] else 0,
                            "date17": userefficiencylog["date17"] if userefficiencylog["date17"] else 0,
                            "date18": userefficiencylog["date18"] if userefficiencylog["date18"] else 0,
                            "date19": userefficiencylog["date19"] if userefficiencylog["date19"] else 0,
                            "date20": userefficiencylog["date20"] if userefficiencylog["date20"] else 0,
                            "date21": userefficiencylog["date21"] if userefficiencylog["date21"] else 0,
                            "date22": userefficiencylog["date22"] if userefficiencylog["date22"] else 0,
                            "date23": userefficiencylog["date23"] if userefficiencylog["date23"] else 0,
                            "date24": userefficiencylog["date24"] if userefficiencylog["date24"] else 0,
                            "date25": userefficiencylog["date25"] if userefficiencylog["date25"] else 0,
                            "date26": userefficiencylog["date26"] if userefficiencylog["date26"] else 0,
                            "date27": userefficiencylog["date27"] if userefficiencylog["date27"] else 0,
                            "date28": userefficiencylog["date28"] if userefficiencylog["date28"] else 0,
                            "date29": userefficiencylog["date29"] if userefficiencylog["date29"] else 0,
                            "date30": userefficiencylog["date30"] if userefficiencylog["date30"] else 0,
                            "date31": userefficiencylog["date31"] if userefficiencylog["date31"] else 0,
                            "target_efficiency": userefficiencylog["target_efficiency"] if userefficiencylog["target_efficiency"] else 0,
                            "minimum_efficiency": userefficiencylog["minimum_efficiency"] if userefficiencylog["minimum_efficiency"] else 0,
                            "total_efficiency": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today))) if
                            userefficiencylog["total_efficiency"] else 0,
                            "pi": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today))) if
                            userefficiencylog["total_efficiency"] else 0,
                            "manual_days": manual_days if manual_days else 0,
                            "user_role": role_data[userefficiencylog["operator__user__id"]] if userefficiencylog["operator__user__id"] in role_data else "",
                            "working_pi": Util.decimal_to_str(request, (int(userefficiencylog["total_efficiency"]) * 100) / (450 * int(manual_days)))
                            if userefficiencylog["total_efficiency"] else 0,
                            "remarks": nc_remark[userefficiencylog["operator__user__username"]]
                            if (userefficiencylog["operator__user__username"]) in nc_remark else 0,
                            "rejection": nc_rejection[userefficiencylog["operator__user__username"]]
                            if (userefficiencylog["operator__user__username"]) in nc_rejection else 0,
                            "additional_remarks": "<span>" + str(remarks_disc[userefficiencylog["operator"]]) + "</span>"
                            if userefficiencylog["operator"] in remarks_disc
                            else "<i class=icon-plus-circle title=Add-remarks style='font-size:13px; margin-left:0px;'></i> Add remarks",
                            "select_date": request.POST.get("today_date_"),
                            "operator__sub_group_of_operator__sub_group_name": userefficiencylog["operator__sub_group_of_operator__sub_group_name"],
                            "sort_col": sort_col,
                            "recordsTotal": recordsTotal,
                        }
                    )
                sort_col_asc = [
                    "user_role", "rejection", "remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7", "date8", "date9", "date10", "date11",
                    "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21", "date22", "date23", "date24", "date25",
                    "date26", "date27", "date28", "date29", "date30", "date31", "manual_days"
                ]
                sort_col_desc = [
                    "-user_role", "-rejection", "-remarks", "-date1", "-date2", "-date3", "-date4", "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11",
                    "-date12", "-date13", "-date14", "-date15", "-date16", "-date17", "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25",
                    "-date26", "-date27", "-date28", "-date29", "-date30", "-date31", "-manual_days"
                ]
                if sort_col in sort_col_desc:
                    response["data"] = sorted(response["data"], key=lambda i: i[sort_col[1:]], reverse=True)
                if sort_col in sort_col_asc:
                    response["data"] = sorted(response["data"], key=lambda i: i[sort_col])
                response["data"] = response["data"][start : (start + length)]
            elif "is_customer_wise" in request.POST:
                if sort_col == "pi" or sort_col == "working_pi":
                    sort_col = "total_efficiency"
                if sort_col == "-pi" or sort_col == "-working_pi":
                    sort_col = "-total_efficiency"
                query_user = Q()
                nc_count = Q()
                query_user.add(
                    Q(
                        created_on__range=[
                            datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                        ]
                    ),
                    query_user.connector,
                )
                query_user.add(~Q(operator=None), query_user.connector)
                nc_count.add(
                    Q(
                        non_conformity__created_on__range=[
                            datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                        ]
                    ),
                    nc_count.connector,
                )
                request_user = request.user.id
                request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
                operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
                if operator_id:
                    if operator_id["operator_type"]:
                        if operator_id["operator_type"] == "PLANET_ENG":
                            query_user.add(Q(operator__user__id=request_user_id["id"]), query_user.connector)
                sort_col_ = [
                    "user_role", "-user_role", "rejection", "-rejection", "remarks", "-remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7",
                    "date8", "date9", "date10", "date11", "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21",
                    "date22", "date23", "date24", "date25", "date26", "date27", "date28", "date29", "date30", "date31", "-date1", "-date2", "-date3", "-date4",
                    "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11", "-date12", "-date13", "-date14", "-date15", "-date16", "-date17",
                    "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25", "-date26", "-date27", "-date28", "-date29",
                    "-date30", "-date31", "manual_days", "-manual_days"
                ]
                userefficiencylogs_ = (
                    UserEfficiencyLog.objects.filter(query_user)
                    .values(
                        "operator__user__username",
                        "operator__user__id",
                        "company__name",
                        "operator__sub_group_of_operator__sub_group_name"
                    )
                ).order_by(sort_col if sort_col not in sort_col_ else "operator__user__username")
                userefficiencylogs = userefficiencylogs_.annotate(
                    target_efficiency=Max("target_efficiency"),
                    minimum_efficiency=Max("minimum_efficiency"),
                    date1=Sum("layer_point", filter=Q(created_on__range=[dates_query[0], dates_query[1]])),
                    date2=Sum("layer_point", filter=Q(created_on__range=[dates_query[1], dates_query[2]])),
                    date3=Sum("layer_point", filter=Q(created_on__range=[dates_query[2], dates_query[3]])),
                    date4=Sum("layer_point", filter=Q(created_on__range=[dates_query[3], dates_query[4]])),
                    date5=Sum("layer_point", filter=Q(created_on__range=[dates_query[4], dates_query[5]])),
                    date6=Sum("layer_point", filter=Q(created_on__range=[dates_query[5], dates_query[6]])),
                    date7=Sum("layer_point", filter=Q(created_on__range=[dates_query[6], dates_query[7]])),
                    date8=Sum("layer_point", filter=Q(created_on__range=[dates_query[7], dates_query[8]])),
                    date9=Sum("layer_point", filter=Q(created_on__range=[dates_query[8], dates_query[9]])),
                    date10=Sum("layer_point", filter=Q(created_on__range=[dates_query[9], dates_query[10]])),
                    date11=Sum("layer_point", filter=Q(created_on__range=[dates_query[10], dates_query[11]])),
                    date12=Sum("layer_point", filter=Q(created_on__range=[dates_query[11], dates_query[12]])),
                    date13=Sum("layer_point", filter=Q(created_on__range=[dates_query[12], dates_query[13]])),
                    date14=Sum("layer_point", filter=Q(created_on__range=[dates_query[13], dates_query[14]])),
                    date15=Sum("layer_point", filter=Q(created_on__range=[dates_query[14], dates_query[15]])),
                    date16=Sum("layer_point", filter=Q(created_on__range=[dates_query[15], dates_query[16]])),
                    date17=Sum("layer_point", filter=Q(created_on__range=[dates_query[16], dates_query[17]])),
                    date18=Sum("layer_point", filter=Q(created_on__range=[dates_query[17], dates_query[18]])),
                    date19=Sum("layer_point", filter=Q(created_on__range=[dates_query[18], dates_query[19]])),
                    date20=Sum("layer_point", filter=Q(created_on__range=[dates_query[19], dates_query[20]])),
                    date21=Sum("layer_point", filter=Q(created_on__range=[dates_query[20], dates_query[21]])),
                    date22=Sum("layer_point", filter=Q(created_on__range=[dates_query[21], dates_query[22]])),
                    date23=Sum("layer_point", filter=Q(created_on__range=[dates_query[22], dates_query[23]])),
                    date24=Sum("layer_point", filter=Q(created_on__range=[dates_query[23], dates_query[24]])),
                    date25=Sum("layer_point", filter=Q(created_on__range=[dates_query[24], dates_query[25]])),
                    date26=Sum("layer_point", filter=Q(created_on__range=[dates_query[25], dates_query[26]])),
                    date27=Sum("layer_point", filter=Q(created_on__range=[dates_query[26], dates_query[27]])),
                    date28=Sum("layer_point", filter=Q(created_on__range=[dates_query[27], dates_query[28]])),
                    date29=Sum("layer_point", filter=date29),
                    date30=Sum("layer_point", filter=date30),
                    date31=Sum("layer_point", filter=date31),
                    total_efficiency=Sum("layer_point"),
                )
                user_ids = [user["operator__user__id"] for user in userefficiencylogs]
                user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")
                role_data = {}
                for user_role in user_roles:
                    role_data[user_role["user_id"]] = user_role["group__name"]

                nc_count = (
                    NonConformityDetail.objects.filter(nc_count, operator__user__id__in=user_ids)
                    .values(
                        "operator__user__username",
                        "non_conformity__company__name",
                    )
                    .annotate(
                        total_nc_remark=Count("id", filter=Q(non_conformity__nc_type="remark")),
                        total_nc_rejection=Count("id", filter=Q(non_conformity__nc_type="rejection")),
                    )
                )
                nc_remark = {}
                for nc_count_ in nc_count:
                    nc_remark[nc_count_["operator__user__username"], nc_count_["non_conformity__company__name"]] = nc_count_["total_nc_remark"]

                nc_rejection = {}
                for nc_count_ in nc_count:
                    nc_rejection[nc_count_["operator__user__username"], nc_count_["non_conformity__company__name"]] = nc_count_["total_nc_rejection"]

                recordsTotal = (
                    UserEfficiencyLog.objects.filter(query_user)
                    .values(
                        "operator__user__username",
                        "company__name",
                        "operator__user__id",
                    )
                ).distinct().count()
                response = {
                    "draw": request.POST["draw"],
                    "recordsTotal": recordsTotal,
                    "recordsFiltered": recordsTotal,
                    "data": [],
                }
                for userefficiencylog in userefficiencylogs:
                    manual_days_ = []
                    for id in range(1, 32):
                        date = "date" + str(id)
                        if userefficiencylog[date] is not None:
                            manual_days_.append(1)
                    manual_days = len(manual_days_)
                    response["data"].append(
                        {
                            "operator__user__username": userefficiencylog["operator__user__username"],
                            "company__name": userefficiencylog["company__name"],
                            "date1": userefficiencylog["date1"] if userefficiencylog["date1"] else 0,
                            "date2": userefficiencylog["date2"] if userefficiencylog["date2"] else 0,
                            "date3": userefficiencylog["date3"] if userefficiencylog["date3"] else 0,
                            "date4": userefficiencylog["date4"] if userefficiencylog["date4"] else 0,
                            "date5": userefficiencylog["date5"] if userefficiencylog["date5"] else 0,
                            "date6": userefficiencylog["date6"] if userefficiencylog["date6"] else 0,
                            "date7": userefficiencylog["date7"] if userefficiencylog["date7"] else 0,
                            "date8": userefficiencylog["date8"] if userefficiencylog["date8"] else 0,
                            "date9": userefficiencylog["date9"] if userefficiencylog["date9"] else 0,
                            "date10": userefficiencylog["date10"] if userefficiencylog["date10"] else 0,
                            "date11": userefficiencylog["date11"] if userefficiencylog["date11"] else 0,
                            "date12": userefficiencylog["date12"] if userefficiencylog["date12"] else 0,
                            "date13": userefficiencylog["date13"] if userefficiencylog["date13"] else 0,
                            "date14": userefficiencylog["date14"] if userefficiencylog["date14"] else 0,
                            "date15": userefficiencylog["date15"] if userefficiencylog["date15"] else 0,
                            "date16": userefficiencylog["date16"] if userefficiencylog["date16"] else 0,
                            "date17": userefficiencylog["date17"] if userefficiencylog["date17"] else 0,
                            "date18": userefficiencylog["date18"] if userefficiencylog["date18"] else 0,
                            "date19": userefficiencylog["date19"] if userefficiencylog["date19"] else 0,
                            "date20": userefficiencylog["date20"] if userefficiencylog["date20"] else 0,
                            "date21": userefficiencylog["date21"] if userefficiencylog["date21"] else 0,
                            "date22": userefficiencylog["date22"] if userefficiencylog["date22"] else 0,
                            "date23": userefficiencylog["date23"] if userefficiencylog["date23"] else 0,
                            "date24": userefficiencylog["date24"] if userefficiencylog["date24"] else 0,
                            "date25": userefficiencylog["date25"] if userefficiencylog["date25"] else 0,
                            "date26": userefficiencylog["date26"] if userefficiencylog["date26"] else 0,
                            "date27": userefficiencylog["date27"] if userefficiencylog["date27"] else 0,
                            "date28": userefficiencylog["date28"] if userefficiencylog["date28"] else 0,
                            "date29": userefficiencylog["date29"] if userefficiencylog["date29"] else 0,
                            "date30": userefficiencylog["date30"] if userefficiencylog["date30"] else 0,
                            "date31": userefficiencylog["date31"] if userefficiencylog["date31"] else 0,
                            "target_efficiency": userefficiencylog["target_efficiency"] if userefficiencylog["target_efficiency"] else 0,
                            "minimum_efficiency": userefficiencylog["minimum_efficiency"] if userefficiencylog["minimum_efficiency"] else 0,
                            "total_efficiency": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today)))
                            if userefficiencylog["total_efficiency"] else 0,
                            "pi": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today))) if
                            userefficiencylog["total_efficiency"] else 0,
                            "manual_days": manual_days if manual_days else 0,
                            "user_role": role_data[userefficiencylog["operator__user__id"]] if userefficiencylog["operator__user__id"] in role_data else "",
                            "working_pi": Util.decimal_to_str(request, (int(userefficiencylog["total_efficiency"]) * 100) / (450 * int(manual_days)))
                            if userefficiencylog["total_efficiency"] else 0,
                            "remarks": nc_remark[userefficiencylog["operator__user__username"], userefficiencylog["company__name"]]
                            if (userefficiencylog["operator__user__username"], userefficiencylog["company__name"]) in nc_remark else 0,
                            "rejection": nc_rejection[userefficiencylog["operator__user__username"], userefficiencylog["company__name"]]
                            if (userefficiencylog["operator__user__username"], userefficiencylog["company__name"]) in nc_rejection else 0,
                            "operator__sub_group_of_operator__sub_group_name": userefficiencylog["operator__sub_group_of_operator__sub_group_name"],
                            "sort_col": sort_col,
                            "recordsTotal": recordsTotal,
                        }
                    )
                sort_col_asc = [
                    "user_role", "rejection", "remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7", "date8", "date9", "date10", "date11",
                    "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21", "date22", "date23", "date24", "date25",
                    "date26", "date27", "date28", "date29", "date30", "date31", "manual_days"
                ]
                sort_col_desc = [
                    "-user_role", "-rejection", "-remarks", "-date1", "-date2", "-date3", "-date4", "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11",
                    "-date12", "-date13", "-date14", "-date15", "-date16", "-date17", "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25",
                    "-date26", "-date27", "-date28", "-date29", "-date30", "-date31", "-manual_days"
                ]
                if sort_col in sort_col_desc:
                    response["data"] = sorted(response["data"], key=lambda i: i[sort_col[1:]], reverse=True)
                if sort_col in sort_col_asc:
                    response["data"] = sorted(response["data"], key=lambda i: i[sort_col])
                response["data"] = response["data"][start : (start + length)]
            else:
                shift_query = Q()
                shift_query.add(
                    Q(
                        created_on__range=[
                            datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                            datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                        ]
                    ),
                    shift_query.connector,
                )
                request_user = request.user.id
                request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
                operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
                if operator_id:
                    if operator_id["operator_type"]:
                        if operator_id["operator_type"] == "PLANET_ENG":
                            shift_query.add(Q(operator__user__id=request_user_id["id"]), shift_query.connector)
                recordsTotal = UserEfficiencyLog.objects.filter(shift_query).values("created_on__date").distinct().count()
                response = {
                    "draw": request.POST["draw"],
                    "recordsTotal": recordsTotal,
                    "recordsFiltered": recordsTotal,
                    "data": [],
                }
                sort_col_ = [
                    "first_shift",
                    "-first_shift",
                    "second_shift",
                    "-second_shift",
                    "third_shift",
                    "-third_shift",
                    "total_point",
                    "-total_point",
                    "knowledge_leaders_first",
                    "-knowledge_leaders_first",
                    "knowledge_leaders_second",
                    "-knowledge_leaders_second",
                    "knowledge_leaders_third",
                    "-knowledge_leaders_third"
                ]
                shift_wise = (
                    UserEfficiencyLog.objects.filter(shift_query)
                    .values("created_on", "layer_point", "knowledge_leaders", "operator_shift").order_by(sort_col if sort_col not in sort_col_ else "created_on")
                )
                date_ = []
                for date in dates:
                    date_.append(datetime.datetime.strptime(str(date) + " 06:00:00.00000", "%Y-%m-%d %H:%M:%S.%f"))
                shiftdata_on_datewise = {}
                for shift_wise_data in shift_wise:
                    for shift_wise_data_key, shift_wise_data_value in shift_wise_data.items():
                        if shift_wise_data_key == "created_on":
                            created_on_date = datetime.datetime.strptime(str(shift_wise_data_value), "%Y-%m-%d %H:%M:%S.%f")
                            for day in range(int(month_days) + 1):
                                day_ = int(day) + 1
                                if created_on_date >= date_[int(day)] and created_on_date <= date_[int(day_)]:
                                    if dates[int(day)] not in shiftdata_on_datewise:
                                        shiftdata_on_datewise[dates[int(day)]] = [shift_wise_data]
                                    else:
                                        shiftdata_on_datewise[dates[int(day)]].append(shift_wise_data)
                shiftwise_report_data = []
                for shiftdata_on_datewise_key, shiftdata_on_datewise_value in shiftdata_on_datewise.items():
                    first_shift_layer_point = 0
                    second_shift_layer_point = 0
                    third_shift_layer_point = 0
                    first_opr = []
                    second_opr = []
                    third_opr = []
                    for shiftdata_on_datewise_value_ in shiftdata_on_datewise_value:
                        for shiftdata_on_datewise_value_key, shiftdata_on_datewise_value_value1 in shiftdata_on_datewise_value_.items():
                            if shiftdata_on_datewise_value_value1 == "first_shift":
                                first_shift_layer_point += shiftdata_on_datewise_value_["layer_point"]
                                if shiftdata_on_datewise_value_["knowledge_leaders"]:
                                    knowledge_leadersss = shiftdata_on_datewise_value_["knowledge_leaders"].split()
                                    first_shift_operator = eval(str(knowledge_leadersss).replace("'", ""))
                                    first_opr += first_shift_operator
                            if shiftdata_on_datewise_value_value1 == "second_shift":
                                second_shift_layer_point += shiftdata_on_datewise_value_["layer_point"]
                                if shiftdata_on_datewise_value_["knowledge_leaders"]:
                                    knowledge_leadersss = shiftdata_on_datewise_value_["knowledge_leaders"].split()
                                    second_shift_operator = eval(str(knowledge_leadersss).replace("'", ""))
                                    second_opr += second_shift_operator
                            if shiftdata_on_datewise_value_value1 == "third_shift":
                                third_shift_layer_point += shiftdata_on_datewise_value_["layer_point"]
                                if shiftdata_on_datewise_value_["knowledge_leaders"]:
                                    knowledge_leadersss = shiftdata_on_datewise_value_["knowledge_leaders"].split()
                                    third_shift_operator = eval(str(knowledge_leadersss).replace("'", ""))
                                    third_opr += third_shift_operator
                    first_op = set(first_opr)
                    first_opr = list(first_op)
                    second_op = set(second_opr)
                    second_opr = list(second_op)
                    third_op = set(third_opr)
                    third_opr = list(third_op)
                    shiftwise_report_data.append({
                        "date": shiftdata_on_datewise_key,
                        "first_shift": first_shift_layer_point,
                        "first_shift_op": first_opr,
                        "second_shift": second_shift_layer_point,
                        "second_shift_op": second_opr,
                        "third_shift": third_shift_layer_point,
                        "third_shift_op": third_opr,
                        "total": first_shift_layer_point + second_shift_layer_point + third_shift_layer_point,
                    })

                operators = Operator.objects.values("id", "user__username")
                operator_name = {}
                for operator in operators:
                    operator_name[operator["id"]] = operator["user__username"]
                knowledge_leaders_first = {}
                knowledge_leaders_second = {}
                knowledge_leaders_third = {}
                for shiftwise_report_data_ in shiftwise_report_data:
                    knowledge_leaders_first[shiftwise_report_data_["date"]] = str(
                        ["<span>" + operator_name[first_shift_operator_name] + "</span><br>" for first_shift_operator_name in shiftwise_report_data_["first_shift_op"]]
                    ).replace(",", "").replace("[", "").replace("]", "").replace("'", "") if shiftwise_report_data_["first_shift_op"] != [] else "-"
                for shiftwise_report_data_ in shiftwise_report_data:
                    knowledge_leaders_second[shiftwise_report_data_["date"]] = str(
                        ["<span>" + operator_name[second_shift_operator_name] + "</span><br>" for second_shift_operator_name in shiftwise_report_data_["second_shift_op"]]
                    ).replace(",", "").replace("[", "").replace("]", "").replace("'", "") if shiftwise_report_data_["second_shift_op"] != [] else "-"
                for shiftwise_report_data_ in shiftwise_report_data:
                    knowledge_leaders_third[shiftwise_report_data_["date"]] = str(
                        ["<span>" + operator_name[third_shift_operator_name] + "</span><br>" for third_shift_operator_name in shiftwise_report_data_["third_shift_op"]]
                    ).replace(",", "").replace("[", "").replace("]", "").replace("'", "") if shiftwise_report_data_["third_shift_op"] != [] else "-"

                for data in shiftwise_report_data:
                    response["data"].append(
                        {
                            "created_on__date": datetime.datetime.strptime(str(data["date"]).strip(), "%Y-%m-%d").strftime("%d-%m-%Y"),
                            "total_point" : float(Util.decimal_to_str(request, (data["total"] / 450) * 100)) if data["total"] else 0,
                            "first_shift" : data["first_shift"] if data["first_shift"] else 0,
                            "second_shift" : data["second_shift"] if data["second_shift"] else 0,
                            "third_shift" : data["third_shift"] if data["third_shift"] else 0,
                            "knowledge_leaders_first" : knowledge_leaders_first[data["date"]] if data["date"] in knowledge_leaders_first else "-",
                            "knowledge_leaders_second" : knowledge_leaders_second[data["date"]] if data["date"] in knowledge_leaders_second else "-",
                            "knowledge_leaders_third" : knowledge_leaders_third[data["date"]] if data["date"] in knowledge_leaders_third else "-",
                            "sort_col": sort_col,
                            "recordsTotal": recordsTotal,
                        }
                    )
                sort_col_asc = [
                    "first_shift", "second_shift", "third_shift", "total_point", "knowledge_leaders_first", "knowledge_leaders_second", "knowledge_leaders_third"
                ]
                sort_col_desc = [
                    "-first_shift", "-second_shift", "-third_shift", "-total_point", "-knowledge_leaders_first", "-knowledge_leaders_second", "-knowledge_leaders_third"
                ]
                if sort_col in sort_col_desc:
                    response["data"] = sorted(response["data"], key=lambda i: i[sort_col[1:]], reverse=True)
                if sort_col in sort_col_asc:
                    response["data"] = sorted(response["data"], key=lambda i: i[sort_col])
                response["data"] = response["data"][start : (start + length)]
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiency_user_reports_export(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_user_efficiency_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = request.POST.get("order_by")
        date_range = request.POST.get("today_date_")
        start_date_ = date_range.split("-")
        start_date = date_range + "-1"
        any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        Last_date = next_month - datetime.timedelta(days=next_month.day)
        dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
        last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        start_dt_ = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
        date_range = last_date_time - start_dt_
        dates = list()
        for days in range(0, date_range.days + 1):
            dates.append((start_dt_ + datetime.timedelta(days)).strftime('%Y-%m-%d'))
        dates_query = []
        for date in dates:
            dates_query.append(datetime.datetime.strptime(str(date) + " 06:00", "%Y-%m-%d %H:%M"))
        date29 = Q()
        if len(dates) > 29:
            date29.add(Q(created_on__range=[dates_query[28], dates_query[29]]), date29.connector)
        else:
            date29.add(Q(created_on__day__range=["29", "30"]), date29.connector)
        date30 = Q()
        if len(dates) > 30:
            date30.add(Q(created_on__range=[dates_query[29], dates_query[30]]), date30.connector)
        else:
            date30.add(Q(created_on__day__range=["30", "31"]), date30.connector)
        date31 = Q()
        if len(dates) > 31:
            date31.add(Q(created_on__range=[dates_query[30], dates_query[31]]), date31.connector)
        else:
            date31.add(Q(created_on__day__range=["31", "1"]), date31.connector)
        month_sundays = len([1 for i in calendar.monthcalendar(int(start_date_[0]), int(start_date_[1])) if i[6] != 0])
        month_days = calendar.monthrange(int(start_date_[0]), int(start_date_[1]))[1]
        total_days = int(month_days) - int(month_sundays)
        if sort_col == "pi" or sort_col == "working_pi":
            sort_col = "total_efficiency"
        if sort_col == "-pi" or sort_col == "-working_pi":
            sort_col = "-total_efficiency"
        query_user = Q()
        query_remark = Q()
        nc_count = Q()
        query_remark.add(
            Q(
                prep_on__range=[
                    datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                    datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                ]
            ),
            query_remark.connector,
        )
        query_user.add(
            Q(
                created_on__range=[
                    datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                    datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                ]
            ),
            query_user.connector,
        )
        query_user.add(~Q(operator=None), query_user.connector)
        nc_count.add(
            Q(
                non_conformity__created_on__range=[
                    datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                    datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                ]
            ),
            nc_count.connector,
        )
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()

        # for current month days count till today without sunday's
        today_ = datetime.datetime.now()
        today = datetime.date(today_.year, today_.month, today_.day)
        current_month_first_day_ = today_.replace(day=1)
        current_month_first_day = datetime.date(current_month_first_day_.year, current_month_first_day_.month, current_month_first_day_.day)
        delta = today - current_month_first_day
        date_list = []
        for i in range(delta.days + 1):
            day = current_month_first_day + datetime.timedelta(days=i)
            date_list.append(day)
        sundays = 0
        for date_ in date_list:
            if date_.weekday() == 6:
                sundays += 1
        total_days_month_till_today = int(len(date_list)) - int(sundays)

        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    query_user.add(Q(operator__user__id=request_user_id["id"]), query_user.connector)
        sort_col_ = [
            "user_role", "-user_role", "rejection", "-rejection", "remarks", "-remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7",
            "date8", "date9", "date10", "date11", "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21",
            "date22", "date23", "date24", "date25", "date26", "date27", "date28", "date29", "date30", "date31", "-date1", "-date2", "-date3", "-date4",
            "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11", "-date12", "-date13", "-date14", "-date15", "-date16", "-date17",
            "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25", "-date26", "-date27", "-date28", "-date29",
            "-date30", "-date31", "manual_days", "-manual_days"
        ]
        userefficiencylogs_ = (
            UserEfficiencyLog.objects.filter(query_user)
            .values(
                "operator__user__username",
                "operator__user__id",
                "operator",
                "operator__sub_group_of_operator__sub_group_name"
            )
        ).order_by(sort_col if sort_col not in sort_col_ else "operator__user__username")
        userefficiencylogs = userefficiencylogs_.annotate(
            target_efficiency=Max("target_efficiency"),
            minimum_efficiency=Max("minimum_efficiency"),
            date1=Sum("layer_point", filter=Q(created_on__range=[dates_query[0], dates_query[1]])),
            date2=Sum("layer_point", filter=Q(created_on__range=[dates_query[1], dates_query[2]])),
            date3=Sum("layer_point", filter=Q(created_on__range=[dates_query[2], dates_query[3]])),
            date4=Sum("layer_point", filter=Q(created_on__range=[dates_query[3], dates_query[4]])),
            date5=Sum("layer_point", filter=Q(created_on__range=[dates_query[4], dates_query[5]])),
            date6=Sum("layer_point", filter=Q(created_on__range=[dates_query[5], dates_query[6]])),
            date7=Sum("layer_point", filter=Q(created_on__range=[dates_query[6], dates_query[7]])),
            date8=Sum("layer_point", filter=Q(created_on__range=[dates_query[7], dates_query[8]])),
            date9=Sum("layer_point", filter=Q(created_on__range=[dates_query[8], dates_query[9]])),
            date10=Sum("layer_point", filter=Q(created_on__range=[dates_query[9], dates_query[10]])),
            date11=Sum("layer_point", filter=Q(created_on__range=[dates_query[10], dates_query[11]])),
            date12=Sum("layer_point", filter=Q(created_on__range=[dates_query[11], dates_query[12]])),
            date13=Sum("layer_point", filter=Q(created_on__range=[dates_query[12], dates_query[13]])),
            date14=Sum("layer_point", filter=Q(created_on__range=[dates_query[13], dates_query[14]])),
            date15=Sum("layer_point", filter=Q(created_on__range=[dates_query[14], dates_query[15]])),
            date16=Sum("layer_point", filter=Q(created_on__range=[dates_query[15], dates_query[16]])),
            date17=Sum("layer_point", filter=Q(created_on__range=[dates_query[16], dates_query[17]])),
            date18=Sum("layer_point", filter=Q(created_on__range=[dates_query[17], dates_query[18]])),
            date19=Sum("layer_point", filter=Q(created_on__range=[dates_query[18], dates_query[19]])),
            date20=Sum("layer_point", filter=Q(created_on__range=[dates_query[19], dates_query[20]])),
            date21=Sum("layer_point", filter=Q(created_on__range=[dates_query[20], dates_query[21]])),
            date22=Sum("layer_point", filter=Q(created_on__range=[dates_query[21], dates_query[22]])),
            date23=Sum("layer_point", filter=Q(created_on__range=[dates_query[22], dates_query[23]])),
            date24=Sum("layer_point", filter=Q(created_on__range=[dates_query[23], dates_query[24]])),
            date25=Sum("layer_point", filter=Q(created_on__range=[dates_query[24], dates_query[25]])),
            date26=Sum("layer_point", filter=Q(created_on__range=[dates_query[25], dates_query[26]])),
            date27=Sum("layer_point", filter=Q(created_on__range=[dates_query[26], dates_query[27]])),
            date28=Sum("layer_point", filter=Q(created_on__range=[dates_query[27], dates_query[28]])),
            date29=Sum("layer_point", filter=date29),
            date30=Sum("layer_point", filter=date30),
            date31=Sum("layer_point", filter=date31),
            total_efficiency=Sum("layer_point"),
        )
        user_ids = [user["operator__user__id"] for user in userefficiencylogs]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")
        role_data = {}
        for user_role in user_roles:
            role_data[user_role["user_id"]] = user_role["group__name"]

        nc_count = (
            NonConformityDetail.objects.filter(nc_count, operator__user__id__in=user_ids)
            .values(
                "operator__user__username",
            )
            .annotate(
                total_nc_remark=Count("id", filter=Q(non_conformity__nc_type="remark")),
                total_nc_rejection=Count("id", filter=Q(non_conformity__nc_type="rejection")),
            )
        )
        nc_remark = {}
        for nc_count_ in nc_count:
            nc_remark[nc_count_["operator__user__username"]] = nc_count_["total_nc_remark"]

        nc_rejection = {}
        for nc_count_ in nc_count:
            nc_rejection[nc_count_["operator__user__username"]] = nc_count_["total_nc_rejection"]

        remarks_list = [userefficiencylogs_["operator"] for userefficiencylogs_ in userefficiencylogs]
        remarks = Remark.objects.filter(query_remark, entity_id__in=remarks_list, content_type_id__model="operator").values("entity_id", "remark").order_by("created_on")
        remarks_disc = {}
        for remark in remarks:
            if remark["entity_id"] not in remarks_disc:
                remarks_disc[remark["entity_id"]] = remark["remark"]
            else:
                remarks_disc[remark["entity_id"]] = remark["remark"]

        query_result = []
        for userefficiencylog in userefficiencylogs:
            manual_days_ = []
            for id in range(1, 32):
                date = "date" + str(id)
                if userefficiencylog[date] is not None:
                    manual_days_.append(1)
            manual_days = len(manual_days_)
            query_result.append(
                {
                    "operator__user__username": userefficiencylog["operator__user__username"],
                    "user_role": role_data[userefficiencylog["operator__user__id"]] if userefficiencylog["operator__user__id"] in role_data else "",
                    "operator__sub_group_of_operator__sub_group_name": userefficiencylog["operator__sub_group_of_operator__sub_group_name"],
                    "pi": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today))) if
                    userefficiencylog["total_efficiency"] else 0,
                    "working_pi": Util.decimal_to_str(request, (int(userefficiencylog["total_efficiency"]) * 100) / (450 * int(manual_days)))
                    if userefficiencylog["total_efficiency"] else 0,
                    "manual_days": manual_days if manual_days else 0,
                    "total_efficiency": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today)))
                    if userefficiencylog["total_efficiency"] else 0,
                    "minimum_efficiency": userefficiencylog["minimum_efficiency"] if userefficiencylog["minimum_efficiency"] else 0,
                    "target_efficiency": userefficiencylog["target_efficiency"] if userefficiencylog["target_efficiency"] else 0,
                    "additional_remarks": BeautifulSoup(remarks_disc[userefficiencylog["operator"]], features="html5lib").get_text()
                    if userefficiencylog["operator"] in remarks_disc else "",
                    "rejection": nc_rejection[userefficiencylog["operator__user__username"]]
                    if (userefficiencylog["operator__user__username"]) in nc_rejection else 0,
                    "remarks": nc_remark[userefficiencylog["operator__user__username"]]
                    if (userefficiencylog["operator__user__username"]) in nc_remark else 0,
                    "date1": userefficiencylog["date1"] if userefficiencylog["date1"] else 0,
                    "date2": userefficiencylog["date2"] if userefficiencylog["date2"] else 0,
                    "date3": userefficiencylog["date3"] if userefficiencylog["date3"] else 0,
                    "date4": userefficiencylog["date4"] if userefficiencylog["date4"] else 0,
                    "date5": userefficiencylog["date5"] if userefficiencylog["date5"] else 0,
                    "date6": userefficiencylog["date6"] if userefficiencylog["date6"] else 0,
                    "date7": userefficiencylog["date7"] if userefficiencylog["date7"] else 0,
                    "date8": userefficiencylog["date8"] if userefficiencylog["date8"] else 0,
                    "date9": userefficiencylog["date9"] if userefficiencylog["date9"] else 0,
                    "date10": userefficiencylog["date10"] if userefficiencylog["date10"] else 0,
                    "date11": userefficiencylog["date11"] if userefficiencylog["date11"] else 0,
                    "date12": userefficiencylog["date12"] if userefficiencylog["date12"] else 0,
                    "date13": userefficiencylog["date13"] if userefficiencylog["date13"] else 0,
                    "date14": userefficiencylog["date14"] if userefficiencylog["date14"] else 0,
                    "date15": userefficiencylog["date15"] if userefficiencylog["date15"] else 0,
                    "date16": userefficiencylog["date16"] if userefficiencylog["date16"] else 0,
                    "date17": userefficiencylog["date17"] if userefficiencylog["date17"] else 0,
                    "date18": userefficiencylog["date18"] if userefficiencylog["date18"] else 0,
                    "date19": userefficiencylog["date19"] if userefficiencylog["date19"] else 0,
                    "date20": userefficiencylog["date20"] if userefficiencylog["date20"] else 0,
                    "date21": userefficiencylog["date21"] if userefficiencylog["date21"] else 0,
                    "date22": userefficiencylog["date22"] if userefficiencylog["date22"] else 0,
                    "date23": userefficiencylog["date23"] if userefficiencylog["date23"] else 0,
                    "date24": userefficiencylog["date24"] if userefficiencylog["date24"] else 0,
                    "date25": userefficiencylog["date25"] if userefficiencylog["date25"] else 0,
                    "date26": userefficiencylog["date26"] if userefficiencylog["date26"] else 0,
                    "date27": userefficiencylog["date27"] if userefficiencylog["date27"] else 0,
                    "date28": userefficiencylog["date28"] if userefficiencylog["date28"] else 0,
                    "date29": userefficiencylog["date29"] if userefficiencylog["date29"] else 0,
                    "date30": userefficiencylog["date30"] if userefficiencylog["date30"] else 0,
                    "date31": userefficiencylog["date31"] if userefficiencylog["date31"] else 0,
                }
            )
        sort_col_asc = [
            "user_role", "rejection", "remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7", "date8", "date9", "date10", "date11",
            "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21", "date22", "date23", "date24", "date25",
            "date26", "date27", "date28", "date29", "date30", "date31", "manual_days"
        ]
        sort_col_desc = [
            "-user_role", "-rejection", "-remarks", "-date1", "-date2", "-date3", "-date4", "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11",
            "-date12", "-date13", "-date14", "-date15", "-date16", "-date17", "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25",
            "-date26", "-date27", "-date28", "-date29", "-date30", "-date31", "-manual_days"
        ]
        if sort_col in sort_col_desc:
            query_result = sorted(query_result, key=lambda i: i[sort_col[1:]], reverse=True)
        if sort_col in sort_col_asc:
            query_result = sorted(query_result, key=lambda i: i[sort_col])
        query_result = query_result[start : (start + length)]
        headers = [
            {"title": "Username"},
            {"title": "Userrole"},
            {"title": "Sub group"},
            {"title": "PI"},
            {"title": "Working PI"},
            {"title": "Worked days"},
            {"title": "Total efficiency"},
            {"title": "Minimum efficiency"},
            {"title": "Target efficiency"},
            {"title": "Additional remarks"},
            {"title": "Rejection"},
            {"title": "Remarks"},
            {"title": "date1"},
            {"title": "date2"},
            {"title": "date3"},
            {"title": "date4"},
            {"title": "date5"},
            {"title": "date6"},
            {"title": "date7"},
            {"title": "date8"},
            {"title": "date9"},
            {"title": "date10"},
            {"title": "date11"},
            {"title": "date12"},
            {"title": "date13"},
            {"title": "date14"},
            {"title": "date15"},
            {"title": "date16"},
            {"title": "date17"},
            {"title": "date18"},
            {"title": "date19"},
            {"title": "date20"},
            {"title": "date21"},
            {"title": "date22"},
            {"title": "date23"},
            {"title": "date24"},
            {"title": "date25"},
            {"title": "date26"},
            {"title": "date27"},
            {"title": "date28"},
            {"title": "date29"},
            {"title": "date30"},
            {"title": "date31"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "user_efficiency_user_wise_report.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiency_shift_reports_export(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_user_efficiency_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = request.POST.get("order_by")
        date_range = request.POST.get("today_date_")
        start_date_ = date_range.split("-")
        start_date = date_range + "-1"
        any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        Last_date = next_month - datetime.timedelta(days=next_month.day)
        dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
        last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        start_dt_ = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
        date_range = last_date_time - start_dt_
        dates = list()
        for days in range(0, date_range.days + 1):
            dates.append((start_dt_ + datetime.timedelta(days)).strftime('%Y-%m-%d'))
        month_days = calendar.monthrange(int(start_date_[0]), int(start_date_[1]))[1]
        shift_query = Q()
        shift_query.add(
            Q(
                created_on__range=[
                    datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                    datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                ]
            ),
            shift_query.connector,
        )
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    shift_query.add(Q(operator__user__id=request_user_id["id"]), shift_query.connector)
        sort_col_ = [
            "first_shift",
            "-first_shift",
            "second_shift",
            "-second_shift",
            "third_shift",
            "-third_shift",
            "total_point",
            "-total_point",
            "knowledge_leaders_first",
            "-knowledge_leaders_first",
            "knowledge_leaders_second",
            "-knowledge_leaders_second",
            "knowledge_leaders_third",
            "-knowledge_leaders_third"
        ]
        shift_wise = (
            UserEfficiencyLog.objects.filter(shift_query)
            .values("created_on", "layer_point", "knowledge_leaders", "operator_shift").order_by(sort_col if sort_col not in sort_col_ else "created_on")
        )
        query_result = []
        date_ = []
        for date in dates:
            date_.append(datetime.datetime.strptime(str(date) + " 06:00:00.00000", "%Y-%m-%d %H:%M:%S.%f"))
        shiftdata_on_datewise = {}
        for shift_wise_data in shift_wise:
            for shift_wise_data_key, shift_wise_data_value in shift_wise_data.items():
                if shift_wise_data_key == "created_on":
                    created_on_date = datetime.datetime.strptime(str(shift_wise_data_value), "%Y-%m-%d %H:%M:%S.%f")
                    for day in range(int(month_days) + 1):
                        day_ = int(day) + 1
                        if created_on_date >= date_[int(day)] and created_on_date <= date_[int(day_)]:
                            if dates[int(day)] not in shiftdata_on_datewise:
                                shiftdata_on_datewise[dates[int(day)]] = [shift_wise_data]
                            else:
                                shiftdata_on_datewise[dates[int(day)]].append(shift_wise_data)
        shiftwise_report_data = []
        for shiftdata_on_datewise_key, shiftdata_on_datewise_value in shiftdata_on_datewise.items():
            first_shift_layer_point = 0
            second_shift_layer_point = 0
            third_shift_layer_point = 0
            first_opr = []
            second_opr = []
            third_opr = []
            for shiftdata_on_datewise_value_ in shiftdata_on_datewise_value:
                for shiftdata_on_datewise_value_key, shiftdata_on_datewise_value_value1 in shiftdata_on_datewise_value_.items():
                    if shiftdata_on_datewise_value_value1 == "first_shift":
                        first_shift_layer_point += shiftdata_on_datewise_value_["layer_point"]
                        if shiftdata_on_datewise_value_["knowledge_leaders"]:
                            knowledge_leadersss = shiftdata_on_datewise_value_["knowledge_leaders"].split()
                            first_shift_operator = eval(str(knowledge_leadersss).replace("'", ""))
                            first_opr += first_shift_operator
                    if shiftdata_on_datewise_value_value1 == "second_shift":
                        second_shift_layer_point += shiftdata_on_datewise_value_["layer_point"]
                        if shiftdata_on_datewise_value_["knowledge_leaders"]:
                            knowledge_leadersss = shiftdata_on_datewise_value_["knowledge_leaders"].split()
                            second_shift_operator = eval(str(knowledge_leadersss).replace("'", ""))
                            second_opr += second_shift_operator
                    if shiftdata_on_datewise_value_value1 == "third_shift":
                        third_shift_layer_point += shiftdata_on_datewise_value_["layer_point"]
                        if shiftdata_on_datewise_value_["knowledge_leaders"]:
                            knowledge_leadersss = shiftdata_on_datewise_value_["knowledge_leaders"].split()
                            third_shift_operator = eval(str(knowledge_leadersss).replace("'", ""))
                            third_opr += third_shift_operator
            first_op = set(first_opr)
            first_opr = list(first_op)
            second_op = set(second_opr)
            second_opr = list(second_op)
            third_op = set(third_opr)
            third_opr = list(third_op)
            shiftwise_report_data.append({
                "date": shiftdata_on_datewise_key,
                "first_shift": first_shift_layer_point,
                "first_shift_op": first_opr,
                "second_shift": second_shift_layer_point,
                "second_shift_op": second_opr,
                "third_shift": third_shift_layer_point,
                "third_shift_op": third_opr,
                "total": first_shift_layer_point + second_shift_layer_point + third_shift_layer_point,
            })

        operators = Operator.objects.values("id", "user__username")
        operator_name = {}
        for operator in operators:
            operator_name[operator["id"]] = operator["user__username"]
        knowledge_leaders_first = {}
        knowledge_leaders_second = {}
        knowledge_leaders_third = {}
        for shiftwise_report_data_ in shiftwise_report_data:
            knowledge_leaders_first[shiftwise_report_data_["date"]] = str(
                [operator_name[first_shift_operator_name] for first_shift_operator_name in shiftwise_report_data_["first_shift_op"]]
            ).replace("[", "").replace("]", "").replace("'", "") if shiftwise_report_data_["first_shift_op"] != [] else "-"
        for shiftwise_report_data_ in shiftwise_report_data:
            knowledge_leaders_second[shiftwise_report_data_["date"]] = str(
                [operator_name[second_shift_operator_name] for second_shift_operator_name in shiftwise_report_data_["second_shift_op"]]
            ).replace("[", "").replace("]", "").replace("'", "") if shiftwise_report_data_["second_shift_op"] != [] else "-"
        for shiftwise_report_data_ in shiftwise_report_data:
            knowledge_leaders_third[shiftwise_report_data_["date"]] = str(
                [operator_name[third_shift_operator_name] for third_shift_operator_name in shiftwise_report_data_["third_shift_op"]]
            ).replace("[", "").replace("]", "").replace("'", "") if shiftwise_report_data_["third_shift_op"] != [] else "-"
        for data in shiftwise_report_data:
            query_result.append(
                {
                    "created_on__date": datetime.datetime.strptime(str(data["date"]).strip(), "%Y-%m-%d").strftime("%d-%m-%Y"),
                    "first_shift" : data["first_shift"] if data["first_shift"] else 0,
                    "knowledge_leaders_first" : knowledge_leaders_first[data["date"]] if data["date"] in knowledge_leaders_first else "-",
                    "second_shift" : data["second_shift"] if data["second_shift"] else 0,
                    "knowledge_leaders_second" : knowledge_leaders_second[data["date"]] if data["date"] in knowledge_leaders_second else "-",
                    "third_shift" : data["third_shift"] if data["third_shift"] else 0,
                    "knowledge_leaders_third" : knowledge_leaders_third[data["date"]] if data["date"] in knowledge_leaders_third else "-",
                    "total_point" : float(Util.decimal_to_str(request, (data["total"] / 450) * 100)) if data["total"] else 0,
                }
            )
        sort_col_asc = ["first_shift", "second_shift", "third_shift", "total_point", "knowledge_leaders_first", "knowledge_leaders_second", "knowledge_leaders_third"]
        sort_col_desc = ["-first_shift", "-second_shift", "-third_shift", "-total_point", "-knowledge_leaders_first", "-knowledge_leaders_second", "-knowledge_leaders_third"]
        if sort_col in sort_col_desc:
            query_result = sorted(query_result, key=lambda i: i[sort_col[1:]], reverse=True)
        if sort_col in sort_col_asc:
            query_result = sorted(query_result, key=lambda i: i[sort_col])
        query_result = query_result[start : (start + length)]
        headers = [
            {"title": "Performance date"},
            {"title": "First shift"},
            {"title": "Knowledge leaders"},
            {"title": "Second shift"},
            {"title": "Knowledge leaders"},
            {"title": "Third shift"},
            {"title": "Knowledge leaders"},
            {"title": "efficiency points"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "user_efficiency_shift_wise_report.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def techHelp(request):
    try:
        TechnicalHelp.objects.create(created_by_id=request.user.id, status="attend")
        response = {"code": 1, "msg": "Technical help has been applied."}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def resolveTechHelp(request):
    try:
        tech_help_id = request.POST.get("tech_help")
        leader = request.POST.get("leader")
        TechnicalHelp.objects.filter(id=tech_help_id).update(attended_by=leader, attended_on=datetime.datetime.now(), status="open")
        response = {"code": 1, "msg": "Technical help has been resolve."}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def compare_order_and_inq(request):
    try:
        compare_type = request.GET.get("compare_type")
        if compare_type == "ECORDERS":
            pws_service = PWSEcPyService()
            ec_response = pws_service.get_ecc({}, "/ecpy/pws/get_orders_for_pws_compare")
            CompareData.objects.filter(import_from="ECORDERS").delete()
            if len(ec_response) > 0:
                orders_bulk = []
                for order in ec_response:
                    orders_bulk.append(CompareData(number=order["OrderNumber"], order_status=order["OrderStatus"], import_from="ECORDERS"))
                CompareData.objects.bulk_create(orders_bulk)
                return HttpResponse(AppResponse.get({"code": 1, "msg": "EC order(s) inserted"}), content_type="json")
            else:
                return HttpResponse(AppResponse.get({"code": 0, "msg": "Ec order(s) data not available"}), content_type="json")
        if compare_type == "ECINQ":
            pws_service = PWSEcPyService()
            ec_response = pws_service.get_ecc({}, "/ecpy/pws/get_inq_for_pws_compare")
            CompareData.objects.filter(import_from="ECINQ").delete()
            if len(ec_response) > 0:
                inq_bulk = []
                for order in ec_response:
                    inq_bulk.append(CompareData(number=order["InqNumber"], order_status=order["InqOfferStatus"], import_from="ECINQ"))
                CompareData.objects.bulk_create(inq_bulk)
                return HttpResponse(AppResponse.get({"code": 1, "msg": "EC inquiry(s) inserted"}), content_type="json")
            else:
                return HttpResponse(AppResponse.get({"code": 0, "msg": "EC inquiry(s) data not available"}), content_type="json")

        if compare_type == "POWERORDERS":
            url = settings.PPM_URL + "/pwsAPI/GetOrders?type=OrderTracker"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            power_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            data = None
            try:
                data = power_res.json()
                CompareData.objects.filter(import_from="POWERORD").delete()
                if data and len(data) > 0:
                    order_bulk = []
                    for order in data:
                        order_bulk.append(CompareData(number=order["OrderNr"], order_status=order["Order Status"], import_from="POWERORD"))
                    CompareData.objects.bulk_create(order_bulk)
                return HttpResponse(AppResponse.get({"code": 1, "msg": "Power order(s) inserted"}), content_type="json")
            except Exception:
                return HttpResponse(AppResponse.get({"code": 0, "msg": "Power order(s) data not available"}), content_type="json")

        if compare_type == "POWERINQUIRY":
            url = settings.PPM_URL + "/pwsAPI/GetOrders?type=InquiryTracker"
            post_data = ""
            headers = {"Key": settings.PPM_KEY}
            power_res = requests.get(url, data=json.dumps(post_data), headers=headers, timeout=5)
            data = None
            try:
                data = power_res.json()
                CompareData.objects.filter(import_from="POWERINQ").delete()
                if data and len(data) > 0:
                    inquiry_bulk = []
                    for order in data:
                        inquiry_bulk.append(CompareData(number=order["cInquiryNo"], order_status=order["Inquiry_Status"], import_from="POWERINQ"))
                    CompareData.objects.bulk_create(inquiry_bulk)
                    return HttpResponse(AppResponse.get({"code": 1, "msg": "Power inquiry(s) inserted"}), content_type="json")
            except Exception:
                return HttpResponse(AppResponse.get({"code": 0, "msg": "Power inquiry(s) data not available"}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def last_imported_on(request):
    status = request.POST.get("status")
    total_data = None
    if status == "ec_compare":
        total_data = CompareData.objects.filter(import_from__in=["ECINQ", "ECORDERS"]).values("id", "compared_on")
    if status == "power_compare":
        total_data = CompareData.objects.filter(import_from__in=["POWERINQ", "POWERORD"]).values("id", "compared_on")
    if total_data:
        last_imported_on = total_data[0]["compared_on"]
        current_time = datetime.datetime.now()
        time_diff = relativedelta(current_time, last_imported_on)
        if time_diff.years:
            text = "year ago" if time_diff.years == 1 else "Years ago"
            time_ = str(time_diff.years) + " " + text
        elif time_diff.months:
            text = "month ago" if time_diff.months == 1 else "Months ago"
            time_ = str(time_diff.months) + " " + text
        elif time_diff.days:
            text = "day ago" if time_diff.days == 1 else "Days ago"
            time_ = str(time_diff.days) + " " + text
        elif time_diff.hours:
            text = "hour ago" if time_diff.hours == 1 else "Hours ago"
            time_ = str(time_diff.hours) + " " + text
        elif time_diff.minutes:
            text = "minute ago" if time_diff.minutes == 1 else "Minutes ago"
            time_ = str(time_diff.minutes) + " " + text
        else:
            text = "second ago" if time_diff.seconds == 1 else "Seconds ago"
            time_ = str(time_diff.seconds) + " " + text
        time = time_
        return HttpResponse(AppResponse.get({"code" : 1, "data" : time}), content_type="json")
    else:
        return HttpResponse(AppResponse.get({"code" : 0, "data" : ""}), content_type="json")


@check_view_permission([{"performance_index": "pws_performance_index"}])
def performance_indexes(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_add_performance_index", "can_update_performance_index", "can_delete_performance_index"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/performance_indexes.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def performance_indexes_search(request):
    try:
        request.POST = Util.get_post_data(request)
        query = Q()
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)

        years_of_experiences = dict(years_of_experience)
        if request.POST.get("years_of_experience"):
            name = request.POST.get("years_of_experience").lower()
            years_of_experience_code = [key for key, value in years_of_experiences.items() if name in value.lower()]
            query.add(Q(years_of_experience__in=years_of_experience_code), query.connector)
        if request.POST.get("target_efficiency"):
            query.add(Q(target_efficiency__icontains=request.POST["target_efficiency"]), query.connector)
        if request.POST.get("minimum_efficiency"):
            query.add(Q(minimum_efficiency__icontains=request.POST["minimum_efficiency"]), query.connector)
        query.add(Q(is_deleted=False), query.connector)
        recordsTotal = PerformanceIndex.objects.filter(query).count()
        performance_indexes = (
            PerformanceIndex.objects.filter(query).values("id", "years_of_experience", "target_efficiency", "minimum_efficiency").order_by(sort_col)[start : (start + length)]
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for performance_index in performance_indexes:
            response["data"].append(
                {
                    "id": performance_index["id"],
                    "years_of_experience": dict(years_of_experience)[performance_index["years_of_experience"]]
                    if performance_index["years_of_experience"] in dict(years_of_experience) else "",
                    "target_efficiency": performance_index["target_efficiency"],
                    "minimum_efficiency": performance_index["minimum_efficiency"],
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def performance_index(request):
    try:
        id = request.POST.get("id")
        if id != 0:
            performance_indexes = PerformanceIndex.objects.filter(id=id).values("id", "years_of_experience", "target_efficiency", "minimum_efficiency").first()
        return render(request, "pws/performance_index.html", {"performance_indexes": performance_indexes})
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_performance_index(request):
    try:
        with transaction.atomic():
            performance_indexes_id = request.POST.get("performance_indexes_id")
            year_of_exp = request.POST.get("year_of_exp")
            target_efficiency_pt = request.POST.get("target_efficiency_pt") if request.POST.get("target_efficiency_pt") else 0
            min_efficiency_pt = request.POST.get("min_efficiency_pt") if request.POST.get("min_efficiency_pt") else 0
            c_ip = base_views.get_client_ip(request)
            if performance_indexes_id:
                if not PerformanceIndex.objects.filter(years_of_experience=year_of_exp, is_deleted=False).exclude(id=performance_indexes_id).exists():
                    PerformanceIndex.objects.filter(id=performance_indexes_id).update(
                        years_of_experience=year_of_exp,
                        target_efficiency=target_efficiency_pt,
                        minimum_efficiency=min_efficiency_pt
                    )
                    action = AuditAction.UPDATE
                    log_views.insert(
                        "pws",
                        "PerformanceIndex",
                        [performance_indexes_id],
                        action,
                        request.user.id,
                        c_ip,
                        "Performance index has been updated.",
                    )
                    response = {"code": 1, "msg": "Performance index has been updated"}
                else:
                    response = {"code": 0, "msg": "Performance index is already exists."}
            else:
                if not PerformanceIndex.objects.filter(years_of_experience=year_of_exp, is_deleted=False).exists():
                    performance_indexes = PerformanceIndex.objects.create(
                        years_of_experience=year_of_exp,
                        target_efficiency=target_efficiency_pt,
                        minimum_efficiency=min_efficiency_pt
                    )
                    action = AuditAction.INSERT
                    log_views.insert(
                        "pws",
                        "PerformanceIndex",
                        [performance_indexes.id],
                        action,
                        request.user.id,
                        c_ip,
                        "Performance index has been created.",
                    )
                    response = {"code": 1, "msg": "Performance index has been created"}
                else:
                    response = {"code": 0, "msg": "Performance index is already exists."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def performance_index_delete(request):
    try:
        with transaction.atomic():
            if Util.has_perm("can_delete_performance_index", request.user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            else:
                performance_index_ids_list = []
                performance_index_ids = request.POST.get("ids")
                for performance_index_id in performance_index_ids.split(","):
                    performance_index_ids_list.append(performance_index_id)
                PerformanceIndex.objects.filter(id__in=performance_index_ids_list).update(is_deleted=True)
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.DELETE
                log_views.insert("pws", "PerformanceIndex", performance_index_ids.split(","), action, request.user.id, c_ip, "Performance index has been deleted.")
                response = {"code": 1, "msg": "Performance index has been deleted."}
                return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def modify_nc(request):
    try:
        id = request.POST.get("id")
        nc_reports = (
            NonConformity.objects.prefetch_related("nonconformitydetail_set")
            .filter(id=id)
            .values(
                "id",
                "order_id",
                "nc_number",
                "company__name",
                "category__name",
                "sub_category__name",
                "created_on",
                "nc_type",
                "order__customer_order_nr",
                "nc_from",
                "root_cause",
                "problem",
                "solution",
                "nc_date",
                "sub_category",
                "category",
                "order__order_date",
                "order__order_number"
            )
            .annotate(
                process=F("nonconformitydetail__process__name"),
                order_number=F("order__order_number"),
                service_name=F("order__service__name"),
                operator=F("nonconformitydetail__operator__user__username"),
                created_by_id=F("created_by"),
                created_by=F("created_by__username"),
                audit_log=F("nonconformitydetail__audit_log"),
            )
        ).first()
        nc_files = (
            Order_Attachment.objects.filter(object_id=nc_reports["order_id"], file_type__code="NC_FILE", source_doc=nc_reports["nc_number"], deleted=False)
            .values("id", "name", "uid", "size")
            .first()
        )
        car_files = (
            Order_Attachment.objects.filter(object_id=nc_reports["order_id"], file_type__code="CAR_FILE", source_doc=nc_reports["nc_number"], deleted=False)
            .values("id", "name", "uid", "size")
            .first()
        )
        order_id = nc_reports["order_id"]
        query = Q()
        query.add(Q(content_type_id__model="order"), query.connector)
        query.add(Q(object_id=order_id), query.connector)
        query.add(
            Q(descr__icontains="</b> from <b>") |
            Q(descr="Exception generated on order") |
            Q(descr__istartswith="Order has been  <b> Finished </b> from <b>"), query.connector
        )
        query.add(~Q(descr__istartswith="Order sent back"), query.connector)
        query.add(~Q(descr__istartswith="Order status changed"), query.connector)
        query.add(~Q(descr__istartswith="Order has been  <b> Cancel"), query.connector)
        auditlogs = Auditlog.objects.filter(query).values("id", "operator__user__username", "descr", "action_by__username").order_by("-action_on")
        audit_logs = []
        for log in auditlogs:
            if log["descr"] == "Exception generated on order":
                audit_logs.append({"id": log["id"], "operator__user__username": log["action_by__username"], "descr": "Exception"})
            else:
                descr = log["descr"].split("from <b> ", 1)[1]
                descr = descr.split(" </b>")[0]
                audit_logs.append({"id": log["id"], "operator__user__username": log["operator__user__username"], "descr": descr if descr else ""})
        created_by = Operator.objects.filter(user_id=nc_reports["created_by_id"]).values("id").first()
        con = {
            "nc_reports": nc_reports,
            "nc_files": nc_files,
            "car_files": car_files,
            "auditlogs": audit_logs,
            "order__order_date": Util.get_local_time(nc_reports["order__order_date"], False),
            "nc_date": Util.get_local_time(nc_reports["nc_date"], True),
            "nc_type": dict(nc_type)[nc_reports["nc_type"]] if nc_reports["nc_type"] in dict(nc_type) else "",
            "nc_from": dict(order_status)[nc_reports["nc_from"]] if nc_reports["nc_from"] in dict(order_status) else "",
            "created_by": created_by["id"],
        }
        return render(request, "pws/reports/modify_nc.html", con)
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def modify_nc_save(request):
    try:
        with transaction.atomic():
            nc_id = request.POST.get("nc_id")
            nc_type = request.POST.get("nc_type")
            main_category = request.POST.get("main_category")
            sub_category = request.POST.get("sub_category")
            check = request.POST.get("check")
            root_cause = request.POST.get("root_cause")
            problem = request.POST.get("problem")
            solution = request.POST.get("solution")
            nc_number = request.POST.get("nc_number")
            order_number = request.POST.get("order_number")
            order_id = request.POST.get("order_id")
            nc_file = request.FILES.get("nc_file")
            car_file = request.FILES.get("car_file")
            nc_create_by = request.POST.get("nc_create_by")
            c_ip = base_views.get_client_ip(request)
            nc_create_date = request.POST.get("nc_create_date")
            nc_create_date = datetime.datetime.strptime(str(nc_create_date).strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:01.111111")

            auditlogs = Auditlog.objects.filter(id=check).values("id", "action_by__username", "action_by", "descr", "operator__user__id").first()
            if auditlogs:
                nc_create_by = Operator.objects.filter(id=nc_create_by).values("user_id").first()
                if auditlogs["descr"] == "Exception generated on order":
                    descr = "Exception"
                    nc_operator_id = auditlogs["action_by"]
                else:
                    descr = auditlogs["descr"].split("from <b> ", 1)[1]
                    descr = descr.split(" </b>")[0]
                    nc_operator_id = auditlogs["operator__user__id"]
                operator = Operator.objects.filter(user__id=nc_operator_id).values("id").first()
                process = OrderProcess.objects.filter(name__iexact=descr).values("id").first()
                operator_id = operator["id"] if operator else None
                process_id = process["id"] if process else None

                NonConformity.objects.filter(id=nc_id).update(
                    nc_type=nc_type,
                    category_id=main_category,
                    sub_category_id=sub_category,
                    root_cause=root_cause,
                    problem=problem,
                    solution=solution,
                    nc_date=nc_create_date,
                    created_by_id=nc_create_by["user_id"]
                )
                NonConformityDetail.objects.filter(non_conformity_id=nc_id).update(
                    operator_id=operator_id,
                    process_id=process_id,
                    audit_log_id=check,
                    nc_detail_date=nc_create_date
                )
                if nc_file is not None:
                    Order_Attachment.objects.filter(object_id=order_id, file_type__code="NC_FILE", name__icontains=nc_number).update(deleted=True)
                    nc_file_name = str(nc_file)
                    nc_file_data = nc_file.read()
                    upload_and_save_impersonate(nc_file_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "NC_FILE", nc_file_name, order_number, nc_number)
                if car_file is not None:
                    car_file_name = str(car_file)
                    car_file_data = car_file.read()
                    upload_and_save_impersonate(car_file_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "CAR_FILE", car_file_name, order_number, nc_number)
                action = AuditAction.UPDATE
                log_views.insert("pws", "nonconformity", [nc_id], action, request.user.id, c_ip, "NC report updated.")
                response = {"code": 1, "msg": "NC report has been updated."}
            return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_orders_with_qta": "reports_orders_with_qta"}])
def orders_with_qta(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_orders_with_qta"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/reports/orders_with_qta_reports.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_orders_with_qta(request):
    try:
        query = Q()
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        query.add(Q(user__user_id=request.user.id), query.connector)
        recordsTotal = Order.objects.filter(query).count()
        orders = (
            Order.objects.prefetch_related("ordertechparameter_set").filter(query)
            .values("id", "order_date", "order_number", "customer_order_nr")
            .annotate(qta=F("ordertechparameter__is_qta"))
            .order_by(sort_col)[start : (start + length)]
        )
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for order in orders:
            response["data"].append(
                {
                    "id": order["id"],
                    "order_number": order["order_number"],
                    "customer_order_nr": order["customer_order_nr"],
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "qta": "Yes" if order["qta"] else "No",
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_orders_with_qta(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_orders_with_qta", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        query.add(Q(user__user_id=request.user.id), query.connector)
        orders = (
            Order.objects.prefetch_related("ordertechparameter_set").filter(query)
            .values("id", "order_date", "order_number", "customer_order_nr")
            .annotate(qta=F("ordertechparameter__is_qta"))
            .order_by(order_by)[start : (start + length)]
        )
        query_result = []
        for order in orders:
            query_result.append(
                {
                    "order_date": Util.get_local_time(order["order_date"], True),
                    "order_number": order["order_number"],
                    "customer_order_nr": order["customer_order_nr"],
                    "qta": "Yes" if order["qta"] else "No",
                }
            )
        headers = [
            {"title": "Order date"},
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "QTA"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "Orders with QTA / No QTA report.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def viewpi(request):
    try:
        id = request.POST.get("id")
        today = datetime.date.today()
        current_year = today.year
        query = Q()
        query.add(Q(operator__user__id=id), query.connector)
        query.add(Q(non_conformity__created_on__year=current_year), query.connector)

        query1 = Q()
        query1.add(Q(operator__user__id=id), query1.connector)
        query1.add(Q(created_on__year=current_year), query1.connector)

        nc_counts = (
            NonConformityDetail.objects.filter(query)
            .values(
                "operator__user__id",
            )
            .annotate(
                nc_remark_jan=Count("id", filter=Q(non_conformity__created_on__month=1, non_conformity__nc_type="remark")),
                nc_remark_feb=Count("id", filter=Q(non_conformity__created_on__month=2, non_conformity__nc_type="remark")),
                nc_remark_mar=Count("id", filter=Q(non_conformity__created_on__month=3, non_conformity__nc_type="remark")),
                nc_remark_apr=Count("id", filter=Q(non_conformity__created_on__month=4, non_conformity__nc_type="remark")),
                nc_remark_may=Count("id", filter=Q(non_conformity__created_on__month=5, non_conformity__nc_type="remark")),
                nc_remark_june=Count("id", filter=Q(non_conformity__created_on__month=6, non_conformity__nc_type="remark")),
                nc_remark_july=Count("id", filter=Q(non_conformity__created_on__month=7, non_conformity__nc_type="remark")),
                nc_remark_aug=Count("id", filter=Q(non_conformity__created_on__month=8, non_conformity__nc_type="remark")),
                nc_remark_sep=Count("id", filter=Q(non_conformity__created_on__month=9, non_conformity__nc_type="remark")),
                nc_remark_oct=Count("id", filter=Q(non_conformity__created_on__month=10, non_conformity__nc_type="remark")),
                nc_remark_nov=Count("id", filter=Q(non_conformity__created_on__month=11, non_conformity__nc_type="remark")),
                nc_remark_dec=Count("id", filter=Q(non_conformity__created_on__month=12, non_conformity__nc_type="remark")),
                nc_rejection_jan=Count("id", filter=Q(non_conformity__created_on__month=1, non_conformity__nc_type="rejection")),
                nc_rejection_feb=Count("id", filter=Q(non_conformity__created_on__month=2, non_conformity__nc_type="rejection")),
                nc_rejection_mar=Count("id", filter=Q(non_conformity__created_on__month=3, non_conformity__nc_type="rejection")),
                nc_rejection_apr=Count("id", filter=Q(non_conformity__created_on__month=4, non_conformity__nc_type="rejection")),
                nc_rejection_may=Count("id", filter=Q(non_conformity__created_on__month=5, non_conformity__nc_type="rejection")),
                nc_rejection_june=Count("id", filter=Q(non_conformity__created_on__month=6, non_conformity__nc_type="rejection")),
                nc_rejection_july=Count("id", filter=Q(non_conformity__created_on__month=7, non_conformity__nc_type="rejection")),
                nc_rejection_aug=Count("id", filter=Q(non_conformity__created_on__month=8, non_conformity__nc_type="rejection")),
                nc_rejection_sep=Count("id", filter=Q(non_conformity__created_on__month=9, non_conformity__nc_type="rejection")),
                nc_rejection_oct=Count("id", filter=Q(non_conformity__created_on__month=10, non_conformity__nc_type="rejection")),
                nc_rejection_nov=Count("id", filter=Q(non_conformity__created_on__month=11, non_conformity__nc_type="rejection")),
                nc_rejection_dec=Count("id", filter=Q(non_conformity__created_on__month=12, non_conformity__nc_type="rejection")),
            )
        )

        user_efficiencylogs = (
            UserEfficiencyLog.objects.filter(query1)
            .values(
                "operator__user__id"
            )
            .annotate(
                target_efficiency_jan=Max("target_efficiency", filter=Q(created_on__month=1)),
                target_efficiency_feb=Max("target_efficiency", filter=Q(created_on__month=2)),
                target_efficiency_mar=Max("target_efficiency", filter=Q(created_on__month=3)),
                target_efficiency_apr=Max("target_efficiency", filter=Q(created_on__month=4)),
                target_efficiency_may=Max("target_efficiency", filter=Q(created_on__month=5)),
                target_efficiency_june=Max("target_efficiency", filter=Q(created_on__month=6)),
                target_efficiency_july=Max("target_efficiency", filter=Q(created_on__month=7)),
                target_efficiency_aug=Max("target_efficiency", filter=Q(created_on__month=8)),
                target_efficiency_sep=Max("target_efficiency", filter=Q(created_on__month=9)),
                target_efficiency_oct=Max("target_efficiency", filter=Q(created_on__month=10)),
                target_efficiency_nov=Max("target_efficiency", filter=Q(created_on__month=11)),
                target_efficiency_dec=Max("target_efficiency", filter=Q(created_on__month=12)),
                minimum_efficiency_jan=Max("minimum_efficiency", filter=Q(created_on__month=1)),
                minimum_efficiency_feb=Max("minimum_efficiency", filter=Q(created_on__month=2)),
                minimum_efficiency_mar=Max("minimum_efficiency", filter=Q(created_on__month=3)),
                minimum_efficiency_apr=Max("minimum_efficiency", filter=Q(created_on__month=4)),
                minimum_efficiency_may=Max("minimum_efficiency", filter=Q(created_on__month=5)),
                minimum_efficiency_june=Max("minimum_efficiency", filter=Q(created_on__month=6)),
                minimum_efficiency_july=Max("minimum_efficiency", filter=Q(created_on__month=7)),
                minimum_efficiency_aug=Max("minimum_efficiency", filter=Q(created_on__month=8)),
                minimum_efficiency_sep=Max("minimum_efficiency", filter=Q(created_on__month=9)),
                minimum_efficiency_oct=Max("minimum_efficiency", filter=Q(created_on__month=10)),
                minimum_efficiency_nov=Max("minimum_efficiency", filter=Q(created_on__month=11)),
                minimum_efficiency_dec=Max("minimum_efficiency", filter=Q(created_on__month=12)),
            )
        )
        response = {
            "nc_count": [],
            "efficiency": [],
        }
        for nc_count in nc_counts:
            response["nc_count"].append(
                {
                    "remark_jan": nc_count["nc_remark_jan"],
                    "remark_feb": nc_count["nc_remark_feb"],
                    "remark_mar": nc_count["nc_remark_mar"],
                    "remark_apr": nc_count["nc_remark_apr"],
                    "remark_may": nc_count["nc_remark_may"],
                    "remark_june": nc_count["nc_remark_june"],
                    "remark_july": nc_count["nc_remark_july"],
                    "remark_aug": nc_count["nc_remark_aug"],
                    "remark_sep": nc_count["nc_remark_sep"],
                    "remark_oct": nc_count["nc_remark_oct"],
                    "remark_nov": nc_count["nc_remark_nov"],
                    "remark_dec": nc_count["nc_remark_dec"],
                    "rejection_jan": nc_count["nc_rejection_jan"],
                    "rejection_feb": nc_count["nc_rejection_feb"],
                    "rejection_mar": nc_count["nc_rejection_mar"],
                    "rejection_apr": nc_count["nc_rejection_apr"],
                    "rejection_may": nc_count["nc_rejection_may"],
                    "rejection_june": nc_count["nc_rejection_june"],
                    "rejection_july": nc_count["nc_rejection_july"],
                    "rejection_aug": nc_count["nc_rejection_aug"],
                    "rejection_sep": nc_count["nc_rejection_sep"],
                    "rejection_oct": nc_count["nc_rejection_oct"],
                    "rejection_nov": nc_count["nc_rejection_nov"],
                    "rejection_dec": nc_count["nc_rejection_dec"],
                }
            )
        for user_efficiencylog in user_efficiencylogs:
            response["efficiency"].append(
                {
                    "target_efficiency_jan": user_efficiencylog["target_efficiency_jan"] if user_efficiencylog["target_efficiency_jan"] else 0,
                    "target_efficiency_feb": user_efficiencylog["target_efficiency_feb"] if user_efficiencylog["target_efficiency_feb"] else 0,
                    "target_efficiency_mar": user_efficiencylog["target_efficiency_mar"] if user_efficiencylog["target_efficiency_mar"] else 0,
                    "target_efficiency_apr": user_efficiencylog["target_efficiency_apr"] if user_efficiencylog["target_efficiency_apr"] else 0,
                    "target_efficiency_may": user_efficiencylog["target_efficiency_may"] if user_efficiencylog["target_efficiency_may"] else 0,
                    "target_efficiency_june": user_efficiencylog["target_efficiency_june"] if user_efficiencylog["target_efficiency_june"] else 0,
                    "target_efficiency_july": user_efficiencylog["target_efficiency_july"] if user_efficiencylog["target_efficiency_july"] else 0,
                    "target_efficiency_aug": user_efficiencylog["target_efficiency_aug"] if user_efficiencylog["target_efficiency_aug"] else 0,
                    "target_efficiency_sep": user_efficiencylog["target_efficiency_sep"] if user_efficiencylog["target_efficiency_sep"] else 0,
                    "target_efficiency_oct": user_efficiencylog["target_efficiency_oct"] if user_efficiencylog["target_efficiency_oct"] else 0,
                    "target_efficiency_nov": user_efficiencylog["target_efficiency_nov"] if user_efficiencylog["target_efficiency_nov"] else 0,
                    "target_efficiency_dec": user_efficiencylog["target_efficiency_dec"] if user_efficiencylog["target_efficiency_dec"] else 0,
                    "minimum_efficiency_jan": user_efficiencylog["minimum_efficiency_jan"] if user_efficiencylog["minimum_efficiency_jan"] else 0,
                    "minimum_efficiency_feb": user_efficiencylog["minimum_efficiency_feb"] if user_efficiencylog["minimum_efficiency_feb"] else 0,
                    "minimum_efficiency_mar": user_efficiencylog["minimum_efficiency_mar"] if user_efficiencylog["minimum_efficiency_mar"] else 0,
                    "minimum_efficiency_apr": user_efficiencylog["minimum_efficiency_apr"] if user_efficiencylog["minimum_efficiency_apr"] else 0,
                    "minimum_efficiency_may": user_efficiencylog["minimum_efficiency_may"] if user_efficiencylog["minimum_efficiency_may"] else 0,
                    "minimum_efficiency_june": user_efficiencylog["minimum_efficiency_june"] if user_efficiencylog["minimum_efficiency_june"] else 0,
                    "minimum_efficiency_july": user_efficiencylog["minimum_efficiency_july"] if user_efficiencylog["minimum_efficiency_july"] else 0,
                    "minimum_efficiency_aug": user_efficiencylog["minimum_efficiency_aug"] if user_efficiencylog["minimum_efficiency_aug"] else 0,
                    "minimum_efficiency_sep": user_efficiencylog["minimum_efficiency_sep"] if user_efficiencylog["minimum_efficiency_sep"] else 0,
                    "minimum_efficiency_oct": user_efficiencylog["minimum_efficiency_oct"] if user_efficiencylog["minimum_efficiency_oct"] else 0,
                    "minimum_efficiency_nov": user_efficiencylog["minimum_efficiency_nov"] if user_efficiencylog["minimum_efficiency_nov"] else 0,
                    "minimum_efficiency_dec": user_efficiencylog["minimum_efficiency_dec"] if user_efficiencylog["minimum_efficiency_dec"] else 0,
                }
            )
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_remark": "remarks_report"}])
def remark_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_remarks_report"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/reports/remark_report.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_remark_report(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "id":
            sort_col = "-id"
        company_id = request.POST.get("company_id")
        remark_id = request.POST.get("remark_id")
        start_date = request.POST.get("start_date__date")
        end_date = request.POST.get("end_date__date")
        query = Q()
        query2 = Q()

        if company_id:
            query.add(Q(company_id=company_id), query.connector)

        if start_date and end_date is not None:
            query2.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(start_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(end_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query2.connector,
            )
        if remark_id:
            query2.add(Q(comment_type_id__in=remark_id), query2.connector)
        query2.add(Q(content_type_id__model="order"), query2.connector)
        if "load_data" in request.POST:
            orders = Order.objects.filter(query).values("id", "company__name", "customer_order_nr", "order_number", "layer", "service__name")
            order_id = [order["id"] for order in orders if order["id"]]
            query2.add(Q(entity_id__in=order_id), query2.connector)
            recordsTotal = Remark.objects.filter(query2).count()
            sort_col_ = [
                "company__name", "-company__name",
                "customer_order_nr", "-customer_order_nr",
                "order_number", "-order_number",
                "service__name", "-service__name",
                "sub_group", "-sub_group"
            ]
            all_remarks = (
                Remark.objects.filter(query2)
                .values("id", "entity_id", "remark", "prep_on", "prep_section")
                .annotate(
                    remarks_type=F("comment_type__name"),
                    remarks_date=F("created_on"),
                    remark_by=F("created_by__username"),
                    prep_by=F("prep_by__username")
                )
                .order_by(sort_col if sort_col not in sort_col_ else "id")
            )
            layer = {}
            company__name = {}
            customer_order_nr = {}
            order_number = {}
            service__name = {}
            for order in orders:
                layer[order["id"]] = order["layer"]
                company__name[order["id"]] = order["company__name"]
                customer_order_nr[order["id"]] = order["customer_order_nr"]
                order_number[order["id"]] = order["order_number"]
                service__name[order["id"]] = order["service__name"]

            layers = [order["layer"] for order in orders if order["layer"]]
            layer_ = Layer.objects.filter(code__in=layers).values("name", "code")
            layers_ = {}
            for layer_ in layer_:
                layers_[layer_["code"]] = layer_["name"]

            operators = Operator.objects.values("user__username", "sub_group_of_operator__sub_group_name")
            sub_group = {}
            for operator in operators:
                if operator["sub_group_of_operator__sub_group_name"]:
                    sub_group[operator["user__username"]] = operator["sub_group_of_operator__sub_group_name"]

            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }
            for remark in all_remarks:
                response["data"].append(
                    {
                        "id": remark["id"],
                        "company__name": company__name[remark["entity_id"]] if remark["entity_id"] in company__name else "",
                        "customer_order_nr": customer_order_nr[remark["entity_id"]] if remark["entity_id"] in customer_order_nr else "",
                        "order_number": order_number[remark["entity_id"]] if remark["entity_id"] in order_number else "",
                        "layer": layers_[layer[remark["entity_id"]] if remark["entity_id"] in layer else ""] if layer[remark["entity_id"]] in layers_ else "",
                        "service__name": service__name[remark["entity_id"]] if remark["entity_id"] in service__name else "",
                        "remark": "<span>" + remark["remark"] + "</span>",
                        "remark_by": remark["remark_by"],
                        "remarks_date": Util.get_local_time(remark["remarks_date"], True),
                        "remarks_type": remark["remarks_type"],
                        "prep_by": remark["prep_by"],
                        "prep_on": Util.get_local_time(remark["prep_on"], True),
                        "prep_section": dict(order_status)[remark["prep_section"]] if remark["prep_section"] in dict(order_status) else "",
                        "sub_group": dict(sub_group)[remark["prep_by"]] if remark["prep_by"] in dict(sub_group) else "",
                        "sort_col": sort_col,
                        "recordsTotal": recordsTotal,
                    }
                )
            sort_col_asc = ["company__name", "customer_order_nr", "order_number", "service__name", "sub_group"]
            sort_col_desc = ["-company__name", "-customer_order_nr", "-order_number", "-service__name", "-sub_group"]
            if sort_col in sort_col_desc:
                response["data"] = sorted(response["data"], key=lambda i: i[sort_col[1:]], reverse=True)
            if sort_col in sort_col_asc:
                response["data"] = sorted(response["data"], key=lambda i: i[sort_col])
            response["data"] = response["data"][start : (start + length)]
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_remark_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_remarks_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = request.POST.get("order_by")
        company_id = request.POST.get("company_id")
        remark_id = request.POST.get("remark_id")
        from_date = request.POST.get("from")
        to_date = request.POST.get("to")

        query = Q()
        query2 = Q()
        if company_id:
            query.add(Q(company_id=company_id), query.connector)
        if from_date and to_date is not None:
            query2.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(from_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(to_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query2.connector,
            )
        if remark_id:
            query2.add(Q(comment_type_id__in=list(map(int, remark_id.split(",")))), query2.connector)
        query2.add(Q(content_type_id__model="order"), query2.connector)
        orders = Order.objects.filter(query).values("id", "company__name", "customer_order_nr", "order_number", "layer", "service__name")
        order_id = [order["id"] for order in orders if order["id"]]
        query2.add(Q(entity_id__in=order_id), query2.connector)
        sort_col_ = [
            "company__name", "-company__name",
            "customer_order_nr", "-customer_order_nr",
            "order_number", "-order_number",
            "service__name", "-service__name",
            "sub_group", "-sub_group"
        ]
        all_remarks = (
            Remark.objects.filter(query2)
            .values("id", "entity_id", "remark", "prep_on", "prep_section")
            .annotate(
                remarks_type=F("comment_type__name"),
                remarks_date=F("created_on"),
                remark_by=F("created_by__username"),
                prep_by=F("prep_by__username")
            )
            .order_by(sort_col if sort_col not in sort_col_ else "id")
        )
        layer = {}
        company__name = {}
        customer_order_nr = {}
        order_number = {}
        service__name = {}
        for order in orders:
            layer[order["id"]] = order["layer"]
            company__name[order["id"]] = order["company__name"]
            customer_order_nr[order["id"]] = order["customer_order_nr"]
            order_number[order["id"]] = order["order_number"]
            service__name[order["id"]] = order["service__name"]

        layers = [order["layer"] for order in orders if order["layer"]]
        layer_ = Layer.objects.filter(code__in=layers).values("name", "code")
        layers_ = {}
        for layer_ in layer_:
            layers_[layer_["code"]] = layer_["name"]

        operators = Operator.objects.values("user__username", "sub_group_of_operator__sub_group_name")
        sub_group = {}
        for operator in operators:
            if operator["sub_group_of_operator__sub_group_name"]:
                sub_group[operator["user__username"]] = operator["sub_group_of_operator__sub_group_name"]

        query_result = []
        for remark in all_remarks:
            query_result.append(
                {
                    "order_number": order_number[remark["entity_id"]] if remark["entity_id"] in order_number else "",
                    "customer_order_nr": customer_order_nr[remark["entity_id"]] if remark["entity_id"] in customer_order_nr else "",
                    "company__name": company__name[remark["entity_id"]] if remark["entity_id"] in company__name else "",
                    "layer": layers_[layer[remark["entity_id"]] if remark["entity_id"] in layer else ""] if layer[remark["entity_id"]] in layers_ else "",
                    "service__name": service__name[remark["entity_id"]] if remark["entity_id"] in service__name else "",
                    "remarks_type": remark["remarks_type"],
                    "remarks": BeautifulSoup(remark["remark"], features="html5lib").get_text() if remark["remark"] else "",
                    "remark_by": remark["remark_by"],
                    "remarks_date": Util.get_local_time(remark["remarks_date"], True),
                    "prep_by": remark["prep_by"],
                    "sub_group": dict(sub_group)[remark["prep_by"]] if remark["prep_by"] in dict(sub_group) else "",
                    "prep_on": Util.get_local_time(remark["prep_on"], True),
                    "prep_section": dict(order_status)[remark["prep_section"]] if remark["prep_section"] in dict(order_status) else "",
                }
            )
        sort_col_asc = ["company__name", "customer_order_nr", "order_number", "service__name", "sub_group"]
        sort_col_desc = ["-company__name", "-customer_order_nr", "-order_number", "-service__name", "-sub_group"]
        if sort_col in sort_col_desc:
            query_result = sorted(query_result, key=lambda i: i[sort_col[1:]], reverse=True)
        if sort_col in sort_col_asc:
            query_result = sorted(query_result, key=lambda i: i[sort_col])
        query_result = query_result[start : (start + length)]
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Customer"},
            {"title": "Layer"},
            {"title": "Service"},
            {"title": "Remark type"},
            {"title": "Remarks"},
            {"title": "Remark by"},
            {"title": "Remark added on"},
            {"title": "Prep by"},
            {"title": "Sub group"},
            {"title": "Prep on"},
            {"title": "Prep section"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "remark_report.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiency_add_remark(request, operator_id, select_date):
    try:
        remarks = CommentType.objects.filter(code="monthwise_performance_remark").values("id", "name").first()
        context = {
            "remark_id": remarks["id"],
            "remark_name": remarks["name"],
            "operator_id": operator_id,
            "select_date": select_date.replace(" ", "")
        }
        return render(request, "pws/reports/user_efficiency_add_remark.html", context)
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def user_efficiency_customer_reports_export(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_user_efficiency_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = request.POST.get("order_by")
        date_range = request.POST.get("today_date_")
        start_date_ = date_range.split("-")
        start_date = date_range + "-1"
        any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        Last_date = next_month - datetime.timedelta(days=next_month.day)
        dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
        last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        start_dt_ = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
        date_range = last_date_time - start_dt_
        dates = list()
        for days in range(0, date_range.days + 1):
            dates.append((start_dt_ + datetime.timedelta(days)).strftime('%Y-%m-%d'))
        dates_query = []
        for date in dates:
            dates_query.append(datetime.datetime.strptime(str(date) + " 06:00", "%Y-%m-%d %H:%M"))
        date29 = Q()
        if len(dates) > 29:
            date29.add(Q(created_on__range=[dates_query[28], dates_query[29]]), date29.connector)
        else:
            date29.add(Q(created_on__day__range=["29", "30"]), date29.connector)
        date30 = Q()
        if len(dates) > 30:
            date30.add(Q(created_on__range=[dates_query[29], dates_query[30]]), date30.connector)
        else:
            date30.add(Q(created_on__day__range=["30", "31"]), date30.connector)
        date31 = Q()
        if len(dates) > 31:
            date31.add(Q(created_on__range=[dates_query[30], dates_query[31]]), date31.connector)
        else:
            date31.add(Q(created_on__day__range=["31", "1"]), date31.connector)
        month_sundays = len([1 for i in calendar.monthcalendar(int(start_date_[0]), int(start_date_[1])) if i[6] != 0])
        month_days = calendar.monthrange(int(start_date_[0]), int(start_date_[1]))[1]
        total_days = int(month_days) - int(month_sundays)
        if sort_col == "pi" or sort_col == "working_pi":
            sort_col = "total_efficiency"
        if sort_col == "-pi" or sort_col == "-working_pi":
            sort_col = "-total_efficiency"
        query_user = Q()
        nc_count = Q()
        query_user.add(
            Q(
                created_on__range=[
                    datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                    datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                ]
            ),
            query_user.connector,
        )
        query_user.add(~Q(operator=None), query_user.connector)
        nc_count.add(
            Q(
                non_conformity__created_on__range=[
                    datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M"),
                    datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M"),
                ]
            ),
            nc_count.connector,
        )
        request_user = request.user.id
        request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
        operator_id = Operator.objects.filter(user__id=request_user_id["id"]).values("operator_type").first()
        if operator_id:
            if operator_id["operator_type"]:
                if operator_id["operator_type"] == "PLANET_ENG":
                    query_user.add(Q(operator__user__id=request_user_id["id"]), query_user.connector)

        # for current month days count till today without sunday's
        today_ = datetime.datetime.now()
        today = datetime.date(today_.year, today_.month, today_.day)
        current_month_first_day_ = today_.replace(day=1)
        current_month_first_day = datetime.date(current_month_first_day_.year, current_month_first_day_.month, current_month_first_day_.day)
        delta = today - current_month_first_day
        date_list = []
        for i in range(delta.days + 1):
            day = current_month_first_day + datetime.timedelta(days=i)
            date_list.append(day)
        sundays = 0
        for date_ in date_list:
            if date_.weekday() == 6:
                sundays += 1
        total_days_month_till_today = int(len(date_list)) - int(sundays)

        sort_col_ = [
            "user_role", "-user_role", "rejection", "-rejection", "remarks", "-remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7",
            "date8", "date9", "date10", "date11", "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21",
            "date22", "date23", "date24", "date25", "date26", "date27", "date28", "date29", "date30", "date31", "-date1", "-date2", "-date3", "-date4",
            "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11", "-date12", "-date13", "-date14", "-date15", "-date16", "-date17",
            "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25", "-date26", "-date27", "-date28", "-date29",
            "-date30", "-date31", "manual_days", "-manual_days"
        ]
        userefficiencylogs_ = (
            UserEfficiencyLog.objects.filter(query_user)
            .values(
                "operator__user__username",
                "company__name",
                "operator__user__id",
                "operator__sub_group_of_operator__sub_group_name"
            )
        ).order_by(sort_col if sort_col not in sort_col_ else "operator__user__username")
        userefficiencylogs = userefficiencylogs_.annotate(
            target_efficiency=Max("target_efficiency"),
            minimum_efficiency=Max("minimum_efficiency"),
            date1=Sum("layer_point", filter=Q(created_on__range=[dates_query[0], dates_query[1]])),
            date2=Sum("layer_point", filter=Q(created_on__range=[dates_query[1], dates_query[2]])),
            date3=Sum("layer_point", filter=Q(created_on__range=[dates_query[2], dates_query[3]])),
            date4=Sum("layer_point", filter=Q(created_on__range=[dates_query[3], dates_query[4]])),
            date5=Sum("layer_point", filter=Q(created_on__range=[dates_query[4], dates_query[5]])),
            date6=Sum("layer_point", filter=Q(created_on__range=[dates_query[5], dates_query[6]])),
            date7=Sum("layer_point", filter=Q(created_on__range=[dates_query[6], dates_query[7]])),
            date8=Sum("layer_point", filter=Q(created_on__range=[dates_query[7], dates_query[8]])),
            date9=Sum("layer_point", filter=Q(created_on__range=[dates_query[8], dates_query[9]])),
            date10=Sum("layer_point", filter=Q(created_on__range=[dates_query[9], dates_query[10]])),
            date11=Sum("layer_point", filter=Q(created_on__range=[dates_query[10], dates_query[11]])),
            date12=Sum("layer_point", filter=Q(created_on__range=[dates_query[11], dates_query[12]])),
            date13=Sum("layer_point", filter=Q(created_on__range=[dates_query[12], dates_query[13]])),
            date14=Sum("layer_point", filter=Q(created_on__range=[dates_query[13], dates_query[14]])),
            date15=Sum("layer_point", filter=Q(created_on__range=[dates_query[14], dates_query[15]])),
            date16=Sum("layer_point", filter=Q(created_on__range=[dates_query[15], dates_query[16]])),
            date17=Sum("layer_point", filter=Q(created_on__range=[dates_query[16], dates_query[17]])),
            date18=Sum("layer_point", filter=Q(created_on__range=[dates_query[17], dates_query[18]])),
            date19=Sum("layer_point", filter=Q(created_on__range=[dates_query[18], dates_query[19]])),
            date20=Sum("layer_point", filter=Q(created_on__range=[dates_query[19], dates_query[20]])),
            date21=Sum("layer_point", filter=Q(created_on__range=[dates_query[20], dates_query[21]])),
            date22=Sum("layer_point", filter=Q(created_on__range=[dates_query[21], dates_query[22]])),
            date23=Sum("layer_point", filter=Q(created_on__range=[dates_query[22], dates_query[23]])),
            date24=Sum("layer_point", filter=Q(created_on__range=[dates_query[23], dates_query[24]])),
            date25=Sum("layer_point", filter=Q(created_on__range=[dates_query[24], dates_query[25]])),
            date26=Sum("layer_point", filter=Q(created_on__range=[dates_query[25], dates_query[26]])),
            date27=Sum("layer_point", filter=Q(created_on__range=[dates_query[26], dates_query[27]])),
            date28=Sum("layer_point", filter=Q(created_on__range=[dates_query[27], dates_query[28]])),
            date29=Sum("layer_point", filter=date29),
            date30=Sum("layer_point", filter=date30),
            date31=Sum("layer_point", filter=date31),
            total_efficiency=Sum("layer_point"),
        )
        user_ids = [user["operator__user__id"] for user in userefficiencylogs]
        user_roles = UserGroup.objects.filter(user__in=user_ids).values("user_id", "group__name")
        role_data = {}
        for user_role in user_roles:
            role_data[user_role["user_id"]] = user_role["group__name"]

        nc_count = (
            NonConformityDetail.objects.filter(nc_count, operator__user__id__in=user_ids)
            .values(
                "operator__user__username",
                "non_conformity__company__name",
            )
            .annotate(
                total_nc_remark=Count("id", filter=Q(non_conformity__nc_type="remark")),
                total_nc_rejection=Count("id", filter=Q(non_conformity__nc_type="rejection")),
            )
        )
        nc_remark = {}
        for nc_count_ in nc_count:
            nc_remark[nc_count_["operator__user__username"], nc_count_["non_conformity__company__name"]] = nc_count_["total_nc_remark"]

        nc_rejection = {}
        for nc_count_ in nc_count:
            nc_rejection[nc_count_["operator__user__username"], nc_count_["non_conformity__company__name"]] = nc_count_["total_nc_rejection"]
        query_result = []
        for userefficiencylog in userefficiencylogs:
            manual_days_ = []
            for id in range(1, 32):
                date = "date" + str(id)
                if userefficiencylog[date] is not None:
                    manual_days_.append(1)
            manual_days = len(manual_days_)
            query_result.append(
                {
                    "operator__user__username": userefficiencylog["operator__user__username"],
                    "user_role": role_data[userefficiencylog["operator__user__id"]] if userefficiencylog["operator__user__id"] in role_data else "",
                    "operator__sub_group_of_operator__sub_group_name": userefficiencylog["operator__sub_group_of_operator__sub_group_name"],
                    "pi": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today))) if
                    userefficiencylog["total_efficiency"] else 0,
                    "working_pi": Util.decimal_to_str(request, (int(userefficiencylog["total_efficiency"]) * 100) / (450 * int(manual_days)))
                    if userefficiencylog["total_efficiency"] else 0,
                    "manual_days": manual_days if manual_days else 0,
                    "total_efficiency": Util.decimal_to_str(request, (userefficiencylog["total_efficiency"] * 100) / (450 * int(total_days_month_till_today)))
                    if userefficiencylog["total_efficiency"] else 0,
                    "company__name": userefficiencylog["company__name"],
                    "minimum_efficiency": userefficiencylog["minimum_efficiency"] if userefficiencylog["minimum_efficiency"] else 0,
                    "target_efficiency": userefficiencylog["target_efficiency"] if userefficiencylog["target_efficiency"] else 0,
                    "rejection": nc_rejection[userefficiencylog["operator__user__username"], userefficiencylog["company__name"]]
                    if (userefficiencylog["operator__user__username"], userefficiencylog["company__name"]) in nc_rejection else 0,
                    "remarks": nc_remark[userefficiencylog["operator__user__username"], userefficiencylog["company__name"]]
                    if (userefficiencylog["operator__user__username"], userefficiencylog["company__name"]) in nc_remark else 0,
                    "date1": userefficiencylog["date1"] if userefficiencylog["date1"] else 0,
                    "date2": userefficiencylog["date2"] if userefficiencylog["date2"] else 0,
                    "date3": userefficiencylog["date3"] if userefficiencylog["date3"] else 0,
                    "date4": userefficiencylog["date4"] if userefficiencylog["date4"] else 0,
                    "date5": userefficiencylog["date5"] if userefficiencylog["date5"] else 0,
                    "date6": userefficiencylog["date6"] if userefficiencylog["date6"] else 0,
                    "date7": userefficiencylog["date7"] if userefficiencylog["date7"] else 0,
                    "date8": userefficiencylog["date8"] if userefficiencylog["date8"] else 0,
                    "date9": userefficiencylog["date9"] if userefficiencylog["date9"] else 0,
                    "date10": userefficiencylog["date10"] if userefficiencylog["date10"] else 0,
                    "date11": userefficiencylog["date11"] if userefficiencylog["date11"] else 0,
                    "date12": userefficiencylog["date12"] if userefficiencylog["date12"] else 0,
                    "date13": userefficiencylog["date13"] if userefficiencylog["date13"] else 0,
                    "date14": userefficiencylog["date14"] if userefficiencylog["date14"] else 0,
                    "date15": userefficiencylog["date15"] if userefficiencylog["date15"] else 0,
                    "date16": userefficiencylog["date16"] if userefficiencylog["date16"] else 0,
                    "date17": userefficiencylog["date17"] if userefficiencylog["date17"] else 0,
                    "date18": userefficiencylog["date18"] if userefficiencylog["date18"] else 0,
                    "date19": userefficiencylog["date19"] if userefficiencylog["date19"] else 0,
                    "date20": userefficiencylog["date20"] if userefficiencylog["date20"] else 0,
                    "date21": userefficiencylog["date21"] if userefficiencylog["date21"] else 0,
                    "date22": userefficiencylog["date22"] if userefficiencylog["date22"] else 0,
                    "date23": userefficiencylog["date23"] if userefficiencylog["date23"] else 0,
                    "date24": userefficiencylog["date24"] if userefficiencylog["date24"] else 0,
                    "date25": userefficiencylog["date25"] if userefficiencylog["date25"] else 0,
                    "date26": userefficiencylog["date26"] if userefficiencylog["date26"] else 0,
                    "date27": userefficiencylog["date27"] if userefficiencylog["date27"] else 0,
                    "date28": userefficiencylog["date28"] if userefficiencylog["date28"] else 0,
                    "date29": userefficiencylog["date29"] if userefficiencylog["date29"] else 0,
                    "date30": userefficiencylog["date30"] if userefficiencylog["date30"] else 0,
                    "date31": userefficiencylog["date31"] if userefficiencylog["date31"] else 0,
                }
            )
        sort_col_asc = [
            "user_role", "rejection", "remarks", "date1", "date2", "date3", "date4", "date5", "date6", "date7", "date8", "date9", "date10", "date11",
            "date12", "date13", "date14", "date15", "date16", "date17", "date18", "date19", "date20", "date21", "date22", "date23", "date24", "date25",
            "date26", "date27", "date28", "date29", "date30", "date31", "manual_days"
        ]
        sort_col_desc = [
            "-user_role", "-rejection", "-remarks", "-date1", "-date2", "-date3", "-date4", "-date5", "-date6", "-date7", "-date8", "-date9", "-date10", "-date11",
            "-date12", "-date13", "-date14", "-date15", "-date16", "-date17", "-date18", "-date19", "-date20", "-date21", "-date22", "-date23", "-date24", "-date25",
            "-date26", "-date27", "-date28", "-date29", "-date30", "-date31", "-manual_days"
        ]
        if sort_col in sort_col_desc:
            query_result = sorted(query_result, key=lambda i: i[sort_col[1:]], reverse=True)
        if sort_col in sort_col_asc:
            query_result = sorted(query_result, key=lambda i: i[sort_col])
        query_result = query_result[start : (start + length)]
        headers = [
            {"title": "Username"},
            {"title": "Userrole"},
            {"title": "Sub group"},
            {"title": "PI"},
            {"title": "Working PI"},
            {"title": "Worked days"},
            {"title": "Total efficiency"},
            {"title": "Minimum efficiency"},
            {"title": "Target efficiency"},
            {"title": "Company"},
            {"title": "Rejection"},
            {"title": "Remarks"},
            {"title": "date1"},
            {"title": "date2"},
            {"title": "date3"},
            {"title": "date4"},
            {"title": "date5"},
            {"title": "date6"},
            {"title": "date7"},
            {"title": "date8"},
            {"title": "date9"},
            {"title": "date10"},
            {"title": "date11"},
            {"title": "date12"},
            {"title": "date13"},
            {"title": "date14"},
            {"title": "date15"},
            {"title": "date16"},
            {"title": "date17"},
            {"title": "date18"},
            {"title": "date19"},
            {"title": "date20"},
            {"title": "date21"},
            {"title": "date22"},
            {"title": "date23"},
            {"title": "date24"},
            {"title": "date25"},
            {"title": "date26"},
            {"title": "date27"},
            {"title": "date28"},
            {"title": "date29"},
            {"title": "date30"},
            {"title": "date31"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "user_efficiency_customer_wise_report.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def update_user_efficiency_report(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_edit", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            min_and_tar_efficiency_list = list(eval(request.POST.get("min_and_tar_efficiency_list")))
            min_and_tar_efficiency_list_len = len(min_and_tar_efficiency_list)

            select_date = request.POST.get("select_date")
            start_date_ = select_date.split("-")
            start_date = select_date + "-1"
            any_day = datetime.date(int(start_date_[0]), int(start_date_[1]), 1)
            next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
            Last_date = next_month - datetime.timedelta(days=next_month.day)
            dt = datetime.datetime(Last_date.year, Last_date.month, Last_date.day)
            last_date_time = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
            last_date_ = datetime.datetime.strptime(str(last_date_time).strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            start_date = datetime.datetime.strptime(str(start_date) + " 06:00", "%Y-%m-%d %H:%M")
            end_date = datetime.datetime.strptime(str(last_date_) + " 06:00", "%Y-%m-%d %H:%M")

            query = Q()
            query.add(Q(created_on__range=[start_date, end_date]), query.connector)
            minimum_efficiency_ids = UserEfficiencyLog.objects.filter(query).values("id", "operator_id", "minimum_efficiency", "target_efficiency")

            min_tar_efficiency_update = []
            user_efficiency_id_list = []
            for data in minimum_efficiency_ids:
                operator_id = data["operator_id"]
                minimum_efficiency = data["minimum_efficiency"]
                target_efficiency = data["target_efficiency"]
                for x in range(min_and_tar_efficiency_list_len):
                    if operator_id == min_and_tar_efficiency_list[x]["operator_id"] and (
                        minimum_efficiency != int(min_and_tar_efficiency_list[x]["minimum_efficiency"])
                        or target_efficiency != int(min_and_tar_efficiency_list[x]["target_efficiency"])
                    ):
                        user_efficiency_id_list.append(data["id"])
                        min_tar_efficiency_update.append(
                            UserEfficiencyLog(
                                id=data["id"],
                                minimum_efficiency=min_and_tar_efficiency_list[x]["minimum_efficiency"],
                                target_efficiency=min_and_tar_efficiency_list[x]["target_efficiency"]
                            )
                        )
            UserEfficiencyLog.objects.bulk_update(min_tar_efficiency_update, ["minimum_efficiency", "target_efficiency"])
            action = AuditAction.UPDATE
            c_ip = base_views.get_client_ip(request)
            log_views.insert("pws", "userefficiencylog", user_efficiency_id_list, action, request.user.id, c_ip, "Minimum efficiency and Target efficiency has been updated.")
            response = {"code": 1, "msg": "Minimum efficiency and Target efficiency has been updated."}
            return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"report_exception": "exceptions_report"}])
def exceptions_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_export_exceptions_report"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws/reports/exceptions_report.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_exceptions_report(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "id":
            sort_col = "-id"
        company_id = request.POST.get("company_id")
        exception_type_id = request.POST.get("exception_type_id")
        start_date = request.POST.get("start_date__date")
        end_date = request.POST.get("end_date__date")

        query = Q()
        if company_id:
            query.add(Q(order__company=company_id), query.connector)
        if start_date and end_date is not None:
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(start_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(end_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        if exception_type_id:
            query.add(Q(pre_define_problem=exception_type_id), query.connector)
        if "load_data" in request.POST:
            recordsTotal = OrderException.objects.filter(query).count()
            order_exceptions = (
                OrderException.objects.filter(query)
                .values(
                    "id",
                    "created_on",
                    "put_to_customer_date",
                    "send_back_date"
                )
                .annotate(
                    pws_id=F("order__order_number"),
                    order_number=F("order__customer_order_nr"),
                    customer=F("order__company__name"),
                    exception_type=F("pre_define_problem__code"),
                    operator=F("created_by__username"),
                    put_to_customer_by=F("put_to_customer_by__username"),
                    send_back_by=F("send_back_by__username"),
                )
                .order_by(sort_col)[start : (start + length)]
            )
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }
            for order_exception in order_exceptions:
                response["data"].append(
                    {
                        "id": order_exception["id"],
                        "pws_id": order_exception["pws_id"],
                        "order_number": order_exception["order_number"],
                        "customer": order_exception["customer"],
                        "exception_type": order_exception["exception_type"],
                        "operator": order_exception["operator"],
                        "created_on": Util.get_local_time(order_exception["created_on"], True),
                        "put_to_customer_by": order_exception["put_to_customer_by"],
                        "put_to_customer_date": Util.get_local_time(order_exception["put_to_customer_date"], True),
                        "send_back_by": order_exception["send_back_by"],
                        "send_back_date": Util.get_local_time(order_exception["send_back_date"], True),
                        "sort_col": sort_col,
                        "recordsTotal": recordsTotal,
                    }
                )
        else:
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
            }
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_exceptions_report(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_exceptions_report", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = request.POST.get("order_by")
        company_id = request.POST.get("company_id")
        exception_type_id = request.POST.get("exception_type_id")
        from_date = request.POST.get("from")
        to_date = request.POST.get("to")

        query = Q()
        if company_id:
            query.add(Q(order__company=company_id), query.connector)
        if from_date and to_date is not None:
            query.add(
                Q(
                    created_on__range=[
                        datetime.datetime.strptime(str(from_date) + " 00:00", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(to_date) + " 23:59", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        if exception_type_id:
            query.add(Q(pre_define_problem=exception_type_id), query.connector)
        order_exceptions = (
            OrderException.objects.filter(query)
            .values(
                "id",
                "created_on",
                "put_to_customer_date",
                "send_back_date"
            )
            .annotate(
                pws_id=F("order__order_number"),
                order_number=F("order__customer_order_nr"),
                customer=F("order__company__name"),
                exception_type=F("pre_define_problem__code"),
                operator=F("created_by__username"),
                put_to_customer_by=F("put_to_customer_by__username"),
                send_back_by=F("send_back_by__username"),
            )
            .order_by(sort_col)[start : (start + length)]
        )

        query_result = []
        for order_exception in order_exceptions:
            query_result.append(
                {
                    "pws_id": order_exception["pws_id"],
                    "order_number": order_exception["order_number"],
                    "operator": order_exception["operator"],
                    "put_to_customer_by": order_exception["put_to_customer_by"],
                    "put_to_customer_date": Util.get_local_time(order_exception["put_to_customer_date"], True),
                    "send_back_by": order_exception["send_back_by"],
                    "send_back_date": Util.get_local_time(order_exception["send_back_date"], True),
                    "exception_type": order_exception["exception_type"],
                    "customer": order_exception["customer"],
                    "created_on": Util.get_local_time(order_exception["created_on"], True),
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Engineer"},
            {"title": "Put to customer by"},
            {"title": "Put to customer on"},
            {"title": "Send back by"},
            {"title": "Send back on"},
            {"title": "Exception type"},
            {"title": "Customer"},
            {"title": "Created on"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "exceptions_report.xls")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong. " + str(e))
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def incoming_reminder_mail_screen(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_send_reminder", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        order_id = request.POST.get("order_id")
        exception_id = request.POST.get("order_exception_id")
        order_number = request.POST.get("order_number")
        company_name = request.POST.get("company_name")

        order_detail = (
            OrderException.objects.filter(id=exception_id)
            .values(
                "order__company__name",
                "order__company",
                "order__order_number",
                "order__customer_order_nr",
                "order__pcb_name",
                "order__layer",
                "order__delivery_term",
                "order__delivery_date",
                "pre_define_problem__code",
                "order_status",
            )
            .first()
        )
        is_si_file = OrderException.objects.filter(id=exception_id).values("is_si_file", "order__user_id", "internal_remark").first()
        internal_remark = is_si_file["internal_remark"] if is_si_file else None
        company_gen_mail = (
            CompanyParameter.objects.filter(company=order_detail["order__company"])
            .values("gen_mail", "is_send_attachment", "is_exp_file_attachment", "ord_exc_rem_mail", "int_exc_to", "int_exc_cc").first()
        )
        if company_gen_mail["is_exp_file_attachment"]:
            upload_image = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="EXCEPTION").values("url", "name", "uid").last()
        else:
            upload_image = ""

        if company_gen_mail["is_send_attachment"]:
            if is_si_file["is_si_file"]:
                si_file = Order_Attachment.objects.filter(object_id=order_id, deleted=False, file_type__code="SI").values("url", "name", "uid").last()
            else:
                si_file = ""
        else:
            si_file = ""

        order_status_name = OrderProcess.objects.filter(code=order_detail["order_status"]).values("code", "name").first()
        layer = Layer.objects.filter(code=order_detail["order__layer"]).values("code", "name").first()
        if layer:
            layers = layer["name"]
        else:
            layers = ""
        delivery_terms = dict(delivery_term)[order_detail["order__delivery_term"]] if order_detail["order__delivery_term"] in dict(delivery_term) else ""
        email_id_ = company_gen_mail["int_exc_to"] if company_gen_mail["int_exc_to"] else settings.INTERNAL_EXCEPTION_MAIL
        cc_mail_ = company_gen_mail["int_exc_cc"] if company_gen_mail["int_exc_cc"] else settings.INTERNAL_EXCEPTION_CC_MAIL
        subject = "Reminder: Internal Exception #" + str(order_detail["order__customer_order_nr"]) + "."
        title = "Dear Concern,<br>Please check on below details and suggest us back asap : #" + str(order_detail["order__customer_order_nr"]) + "."
        head = company_name + " #" + order_number + "."
        message = render_to_string(
            "pws/mail_order.html",
            {
                "internal_remark": internal_remark,
                "head": head,
                "title": title,
                "layers": layers,
                "order_detail": order_detail,
                "company_gen_mail": company_gen_mail,
                "delivery_terms": delivery_terms,
                "order_status_name": order_status_name["name"] if order_status_name is not None else "",
            },
        )
        response = {
            "code": 1,
            "msg": "Order cancel.",
            "upload_image": upload_image,
            "si_file": si_file,
            "subject": subject,
            "message": message,
            "pre_define_problem__code": order_detail["pre_define_problem__code"],
            "mail_to_customer": email_id_,
            "mail_to_cc": cc_mail_,
        }
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def incoming_send_reminder(request):
    try:
        order_exception_id = request.POST.get("order_exception_id")
        order_id = request.POST.get("order_id")
        c_ip = base_views.get_client_ip(request)
        action = AuditAction.INSERT
        log_views.insert("pws", "OrderException", [order_exception_id], action, request.user.id, c_ip, "Internal exception reminder sent")
        log_views.insert("pws", "Order", [order_id], action, request.user.id, c_ip, "Internal exception reminder sent")
        response = {"code": 1, "msg": "Internal exception reminder sent successfully"}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
