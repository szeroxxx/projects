import datetime
import json
import logging
from datetime import timedelta

from accounts.services import UserService
from attachment.views import upload_and_save_impersonate
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import views as base_views
from base.choices import layer_code_gtn, order_status
from base.models import AppResponse, DocNumber
from base.util import Util
from base.views import Remark, create_remark, get_client_ip
from django.contrib.auth.models import User
from django.db.models import Case, Count, F, IntegerField, Q, Value, When
from django.db.models.aggregates import Count
from django.db.models.functions import Cast, Replace
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from exception_log import manager
from mails.views import send_mail
from pws.models import (CompanyParameter, CompanyUser, Layer, Order,
                        Order_Attachment, OrderException, OrderFlowMapping,
                        OrderProcess, OrderScreen, OrderScreenParameter,
                        OrderTechParameter, Service)
from pws.views import skill_matrix_order
from django.db import transaction
from sparrow.decorators import check_view_permission


def place_order(request):
    try:
        operator = CompanyUser.objects.filter(user_id=request.user.id).values("id", "company_id").first()
        company_id = operator["company_id"] if operator else None
        if company_id:
            order_screen_master = list(
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
            sub_parameter_ids = [y for x in order_screen_master if x["display_ids"] for y in x["display_ids"].split(",")]
            response = list(OrderScreenParameter.objects.filter(id__in=sub_parameter_ids).values("code", "name", "parent_id").order_by("sequence"))
            service_sub_ids = [y for x in order_screen_master if x["order_screen_parameter__code"] == "cmb_service" for y in x["display_ids"].split(",") if x["display_ids"]]
            if service_sub_ids:
                service_data = Service.objects.filter(id__in=service_sub_ids).values("id", "name", "code")
            else:
                applied_services = OrderFlowMapping.objects.filter(~Q(service_id=None), company_id=company_id, is_deleted=False).values("service_id")
                service_sub_ids = [x["service_id"] for x in applied_services]
                if service_sub_ids:
                    service_data = Service.objects.filter(id__in=service_sub_ids).values("id", "name", "code")
                else:
                    service_data = None
            return render(request, "pws_portal/place_order.html", {"order_screen_master": order_screen_master, "response": response, "service_data": service_data})
        else:
            return render(request, "pws_portal/place_order.html")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"order_tracking": "order_tracking"}])
def order_tracking(request, id):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_add_new_file", "view_file_history", "view_file_order_tracking", "can_set_order_priority", "can_accept_preparation", "can_modify_order", "can_export_order_tracking"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws_portal/order_tracking.html", {"permissions": json.dumps(permissions), "id": id})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def search_order_tracking(request, id):
    try:
        query = Q()
        excluded_order_status = ["cancel", "exception", "finished"]
        query.add(Q(user__user_id=request.user.id), query.connector)
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        if sort_col == "layer":
            sort_col = "layer_column"
        if sort_col == "-layer":
            sort_col = "-layer_column"
        if id == "1":
            query = query.add(Q(user__user_id=request.user.id) & ~Q(order_status__in=excluded_order_status), query.connector)
        if id == "2":
            query = query.add(Q(order_status="finished"), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("order_status"):
            if request.POST.get("order_status").lower() in "order finish":
                query.add(Q(order_status__icontains="finished"), query.connector)
            else:
                query.add(Q(order_status__icontains=request.POST["order_status"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("service__name"):
            query.add(Q(service__name__icontains=request.POST["service__name"]), query.connector)
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
        if request.POST.get("finished_on") is not None:
            query.add(
                Q(
                    finished_on__range=[
                        datetime.datetime.strptime(str(request.POST.get("finished_on").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("finished_on").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        orders = (
            Order.objects.filter(query)
            .values("id", "order_number", "order_status", "pcb_name", "layer", "service__name", "order_date", "customer_order_nr", "finished_on")
            .annotate(
                created_by=F("user__user__username"),
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
        recordsTotal = Order.objects.filter(query).count()
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        layer_codes = [order["layer"] for order in orders if order["layer"]]
        layer = Layer.objects.filter(code__in=layer_codes).values("name", "code")
        layers_ = Util.get_dict_from_quryset("code", "name", layer)
        for order in orders:
            response["data"].append(
                {
                    "id": order["id"],
                    "order_number": order["order_number"],
                    "customer_order_nr": order["customer_order_nr"],
                    "order_status": dict(order_status)[order["order_status"]] if order["order_status"] in dict(order_status) else "-",
                    "pcb_name": order["pcb_name"],
                    "layer": layers_[order["layer"]] if order["layer"] in layers_ else "",
                    "service__name": order["service__name"],
                    "created_by": order["created_by"],
                    "finished_on": Util.get_local_time(
                        order["finished_on"],
                        True,
                    ),
                    "order_date": Util.get_local_time(
                        order["order_date"],
                        True,
                    ),
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def set_order_priority(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_set_order_priority", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        order_id = request.POST.get("id")
        due_time_code = request.POST.get("due_time")
        time = due_time_code.replace("Due_time_", "").replace("H", "")
        order = Order.objects.get(id=order_id)
        order.preparation_due_date = order.order_date + timedelta(hours=int(time))
        order.save()
        c_ip = base_views.get_client_ip(request)
        action = AuditAction.UPDATE
        log_views.insert("pws", "Order", [str(order_id)], action, request.user.id, c_ip, "Set order priority")
        return HttpResponse(AppResponse.msg(1, " Order priority set successfully"), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_order_tracking(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_order_tracking", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        excluded_order_status = ["cancel", "exception", "finished"]
        query.add(Q(user__user_id=request.user.id), query.connector)
        if request.POST.get("page_id") == "1":
            query = query.add(Q(user__user_id=request.user.id) & ~Q(order_status__in=excluded_order_status), query.connector)
        if request.POST.get("page_id") == "2":
            query = query.add(Q(order_status="finished"), query.connector)
        if request.POST.get("order_number"):
            query.add(Q(order_number__icontains=request.POST["order_number"]), query.connector)
        if request.POST.get("customer_order_nr"):
            query.add(Q(customer_order_nr__icontains=request.POST["customer_order_nr"]), query.connector)
        if request.POST.get("order_status"):
            if request.POST.get("order_status").lower() in "order finish":
                query.add(Q(order_status__icontains="finished"), query.connector)
            else:
                query.add(Q(order_status__icontains=request.POST["order_status"]), query.connector)
        if request.POST.get("pcb_name"):
            query.add(Q(pcb_name__icontains=request.POST["pcb_name"]), query.connector)
        if request.POST.get("layer"):
            layer = [int(s) for s in request.POST.get("layer").split() if s.isdigit()]
            query.add(Q(layer__icontains=layer[0] if layer else request.POST.get("layer")), query.connector)
        if request.POST.get("service__name"):
            query.add(Q(service__name__icontains=request.POST["service__name"]), query.connector)
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
        if request.POST.get("finished_on"):
            query.add(
                Q(
                    finished_on__range=[
                        datetime.datetime.strptime(str(request.POST.get("finished_on").split("-")[0] + " 00:00").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                        datetime.datetime.strptime(str(request.POST.get("finished_on").split("-")[1] + " 23:59").strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M"),
                    ]
                ),
                query.connector,
            )
        order_data = (
            Order.objects.filter(query)
            .values("order_number", "order_status", "pcb_name", "layer", "service__name", "order_date", "customer_order_nr", "finished_on")
            .annotate(
                created_by=F("user__user__username"),
                layer_column=Case(
                    When(layer__endswith=" L", then=(Cast(Replace("layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(layer__in=layer_code_gtn, then=(Cast(Replace("layer", Value("L"), Value("")), output_field=IntegerField()))),
                    When(layer="", then=None),
                    default=None,
                    output_field=IntegerField(),
                ),
            ).order_by(order_by)[start : (start + length)]
        )
        layer_codes = [order["layer"] for order in order_data if order["layer"]]
        layer = Layer.objects.filter(code__in=layer_codes).values("name", "code")
        layers_ = Util.get_dict_from_quryset("code", "name", layer)
        query_result = []
        for data in order_data:
            query_result.append(
                {
                    "order_number": data["order_number"],
                    "customer_order_nr": data["customer_order_nr"],
                    "order_status": data["order_status"],
                    "pcb_name": data["pcb_name"],
                    "layer": layers_[data["layer"]] if data["layer"] in layers_ else "",
                    "service_name": data["service__name"],
                    "created_by": data["created_by"],
                    "order_date": Util.get_local_time(
                        data["order_date"],
                        True,
                    ),
                    "finished_on": Util.get_local_time(
                        data["finished_on"],
                        True,
                    ),
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Order status"},
            {"title": "PCB name"},
            {"title": "Layer"},
            {"title": "Service name"},
            {"title": "Created by"},
            {"title": "Order date"},
            {"title": "Finished on"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "OrderTracking.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def modify_order(request, order_id, is_exception):
    operator = CompanyUser.objects.filter(user_id=request.user.id).values("id", "company_id").first()
    company_id = operator["company_id"] if operator else None
    if company_id:
        order_screen_data = list(
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
        files = Order_Attachment.objects.filter(object_id=order_id, file_type__code="ORDERFILE", deleted=False).values("id", "name", "uid", "size").last()
        sub_parameter_ids = [y for x in order_screen_data if x["display_ids"] for y in x["display_ids"].split(",")]
        response = (OrderScreenParameter.objects.filter(id__in=sub_parameter_ids).values("code", "name", "parent_id", "parent_id__code").order_by("sequence"))
        order_tech_parameter = OrderTechParameter.objects.filter(order__id=order_id).values().first()
        order_values = Order.objects.filter(id=order_id).values().first()
        services = Service.objects.filter(id=order_values["service_id"]).values("name").first()
    return render(
        request,
        "pws_portal/modify_order.html",
        {
            "order_screen_data": order_screen_data,
            "order_values": order_values,
            "order_tech_parameter": order_tech_parameter,
            "response": response,
            "services": services["name"],
            "is_exception": is_exception,
            "files": files if files else None,
        },
    )


def modify_and_place_order(request, order_id):
    try:
        with transaction.atomic():
            order_params = request.POST.dict()
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

            order_number = order_params.pop("order_number")
            service_type_code = order_params.pop("service_type") if "service_type" in order_params else None
            company_user = CompanyUser.objects.filter(user_id=request.user.id).values("id", "company_id").first()
            company_id = company_user["company_id"] if company_user else None
            order_flow = OrderFlowMapping.objects.filter(company_id=company_id, service__code=service_type_code).values("process_ids", "service_id").first()
            service_id = order_flow["service_id"] if order_flow and order_flow["service_id"] else None
            remarks = order_tech.pop("remarks") if "remarks" in order_tech else ""
            layer = order_tech.pop("layer") if "layer" in order_tech else None
            delivery_format = order_tech.pop("delivery_format") if "delivery_format" in order_tech else None
            delivery_term = order_tech.pop("delivery_term") if "delivery_term" in order_tech else None
            due_time = order_tech["due_time"] if "due_time" in order_tech else None
            cam_remark = order_tech["cam_remark"] if "cam_remark" in order_tech else None
            model_remark_field = "remarks"
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
            if due_time and due_time != "":
                preparation_due_date = datetime.datetime.now() + timedelta(hours=int(due_time.replace("Due_time_", "").replace("H", ""))) if "due_time" in order_tech else None
            else:
                preparation_due_date = None
            if order_id == "0":
                pcb_name = order_params.pop("pcb_name") if "pcb_name" in order_params else None
                order_tech.pop("order_file") if "order_file" in order_tech else ""
                process_ids = str(order_flow["process_ids"]).split(",") if order_flow and order_flow["process_ids"] != "" else []
                processes = OrderProcess.objects.filter(~Q(code__in=["exception", "back_to_previous", "ppa_exception"]), id__in=process_ids).values("code", "sequence").order_by("sequence")
                order_status = processes[0]["code"] if len(processes) > 0 else ""
                order_next_status = processes[1]["code"] if len(processes) > 1 else None
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.INSERT
                docnumber = DocNumber.objects.filter(code="Order_place").first()
                messages = "Order " + order_number + " created."
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
                    title = "Dear customer,"
                    title_ = "Thank you for placing your order."
                    head = order_detail["company__name"] + " #" + order_detail["customer_order_nr"]
                    message = render_to_string(
                        "pws/mail_order.html",
                        {
                            "mail_type": "place_order",
                            "title_": title_,
                            "head": head,
                            "title": title,
                            "layers": layers,
                            "order_detail": order_detail,
                        },
                    )
                    send_mail(True, "public", [*email_id], subject, message, "", [cc_mail], mail_from)
                log_views.insert("pws", "order", [order.id], action, request.user.id, c_ip, "Order has been created")
                if remarks != "":
                    base_views.create_remark("pws", "order", order.id, remarks, "Cus_rema", request.user.id, model_remark_field, "Customer_Remarks", "", "")
                if cam_remark:
                    base_views.create_remark("pws", "order", order.id, order_tech["cam_remark"], "Cum_rema", request.user.id, model_remark_field, "Customer_CAM_Remarks", "", "")
                skill_matrix_order(request, order.id, order_status, None)
                return HttpResponse(AppResponse.msg(1, messages), content_type="json")
            else:
                file_ = request.FILES.get("order_file")
                if file_ is not None:
                    c_ip = base_views.get_client_ip(request)
                    Order_Attachment.objects.filter(object_id=order_id, file_type__code="ORDERFILE").update(deleted=True)
                    file_name = str(file_)
                    file_data = file_.read()
                    upload_and_save_impersonate(file_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "ORDERFILE", file_name, order_number, "")
                order_tech["is_include_assembly"] = True if request.POST.get("chk_include_assembly") == "on" else False
                order_tech["is_top_stencil"] = True if request.POST.get("chk_top_stencil") == "on" else False
                order_tech["is_bottom_stencil"] = True if request.POST.get("chk_bottom_stencil") == "on" else False
                order_tech["is_special_buildup"] = True if request.POST.get("chk_special_buildup") == "on" else False
                order_tech["is_defined_impedance"] = True if request.POST.get("chk_defined_impedance") == "on" else False
                order_tech["is_bare_board_testing"] = True if request.POST.get("chk_bare_board_testing") == "on" else False
                order_tech["ul_marking"] = True if request.POST.get("is_chk_ul_marking") == "on" else False
                order_tech["specific_marking"] = True if request.POST.get("is_chk_specific_marking") == "on" else False
                order_tech["pth_on_the_board_edge"] = True if request.POST.get("is_chk_pth_on_the_board_edge") == "on" else False
                order_tech["round_edge_plating"] = True if request.POST.get("is_chk_round_edge_plating") == "on" else False
                order_tech["copper_upto_board_edge"] = True if request.POST.get("is_chk_copper_upto_board_edge") == "on" else False
                order_tech["press_fit_holes"] = True if request.POST.get("is_chk_press_fit_holes") == "on" else False
                order_tech["chamfered_holes"] = True if request.POST.get("is_chk_chamfered_holes") == "on" else False
                order_tech["depth_routing"] = True if request.POST.get("is_chk_depth_routing") == "on" else False
                order_tech["is_nda"] = True if request.POST.get("chk_nda") == "on" else False
                order_tech["is_qta"] = True if request.POST.get("chk_qta") == "on" else False
                c_ip = base_views.get_client_ip(request)
                action = AuditAction.UPDATE
                pcb_name = order_params.pop("pcb_name") if "pcb_name" in order_params else None
                order_tech["order_id"] = order_id
                Order.objects.filter(id=order_id).update(
                    customer_order_nr=order_number,
                    layer=layer,
                    pcb_name=pcb_name,
                    delivery_date=delivery_date,
                    act_delivery_date=act_delivery_date,
                    delivery_format=delivery_format,
                    delivery_term=delivery_term,
                    preparation_due_date=preparation_due_date,
                    remarks=remarks,
                )
                Remark.objects.filter(entity_id=order_id, comment_type__code="Customer_Remarks").update(remark=remarks)
                if cam_remark:
                    Remark.objects.filter(entity_id=order_id, comment_type__code="Customer_CAM_Remarks").update(remark=order_tech["cam_remark"])
                OrderTechParameter.objects.filter(order_id=order_id).update(**order_tech)
                if request.POST.get("is_exception") == "Yes":
                    OrderException.objects.filter(order=order_id).update(order_in_exception=True)
                    order_status = OrderException.objects.filter(order=order_id).values("order_status").last()
                    Order_Attachment.objects.filter(object_id=order_id, file_type__code="EXCEPTION").update(deleted=True)
                    Order.objects.filter(id=order_id).update(order_status=order_status["order_status"], in_time=datetime.datetime.now())
                    log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, "Order has been updated from exception")
                else:
                    log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, "Order has been updated")
                return HttpResponse(AppResponse.msg(1, "Order modified successfully"), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"exception_tracking": "exception_tracking"}])
def exception_tracking(request):
    try:
        user = User.objects.get(id=request.user.id)
        perms = ["can_add_new_file", "view_file_history", "can_cancel", "can_replay_exception", "can_exception_tracking_files", "can_modify_exception_order", "can_export_exception_tracking"]
        permissions = Util.get_permission_role(user, perms)
        return render(request, "pws_portal/exception_tracking.html", {"permissions": json.dumps(permissions)})
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"dashboard": "customer_dashboard"}])
def dashboard(request):
    try:
        excluded_order_status = ["cancel", "exception", "finished"]
        query = Q(user__user_id=request.user.id)
        order = Order.objects.filter(query).aggregate(
            total_orders=Count("id"),
            order_in_process=Count("id", filter=~Q(order_status__in=excluded_order_status)),
            order_in_exception=Count("id", filter=Q(order_status="exception")),
            order_in_finished=Count("id", filter=Q(order_status="finished")),
        )
        order_in_exception = OrderException.objects.filter(~Q(order__order_status="cancel"), order_in_exception=False, order__user__user_id=request.user.id).aggregate(
            order_in_exception=Count("id", filter=Q(exception_status="put_to_customer")),
        )
        order_data = Order.objects.filter(query).values("id", "customer_order_nr", "order_date", "order_status", "finished_on").order_by("-id")
        finish_orders = []
        process_orders = []
        orders = []
        for ord in order_data:
            orders.append({"id": ord["id"], "order_number": ord["customer_order_nr"], "order_date": Util.get_local_time(ord["order_date"], True), "order_status": ord["order_status"]})
            if ord["order_status"] != "cancel" and ord["order_status"] != "exception" and ord["order_status"] != "finished":
                process_orders.append(
                    {
                        "id": ord["id"],
                        "order_number": ord["customer_order_nr"],
                        "order_date": Util.get_local_time(ord["order_date"], True),
                        "order_status": ord["order_status"],
                    }
                )
            if ord["order_status"] == "finished":
                finish_orders.append(
                    {
                        "id": ord["id"],
                        "order_number": ord["customer_order_nr"],
                        "order_date": Util.get_local_time(ord["finished_on"], True),
                        "order_status": ord["order_status"],
                    }
                )
        exception_orders = []
        exception_order_data = (
            OrderException.objects.filter(~Q(order__order_status="cancel"), order_in_exception=False, order__user__user_id=request.user.id, exception_status="put_to_customer")
            .values("id", "order__customer_order_nr", "created_on", "order__order_status")
            .order_by("-id")[0:5]
        )
        for exec_ord in exception_order_data:
            exception_orders.append(
                {
                    "id": exec_ord["id"],
                    "order_number": exec_ord["order__customer_order_nr"],
                    "order_date": Util.get_local_time(exec_ord["created_on"], True),
                    "order_status": exec_ord["order__order_status"],
                }
            )
        currentTime = datetime.datetime.now()
        currentTime.hour
        greeting = ""
        if currentTime.hour < 12:
            greeting = "GOOD MORNING!"
        elif 12 <= currentTime.hour < 18:
            greeting = "GOOD AFTERNOON!"
        else:
            greeting = "GOOD EVENING!"
        user = User.objects.get(username=request.session.get("username").strip())
        customer_user_id = CompanyUser.objects.filter(user=request.user.id).values("id").first()
        if customer_user_id:
            customer_user = True
        else:
            customer_user = False
        user_full_name = user.first_name + " " + user.last_name
        theme_info = UserService.get_theme_info(request.session.get("color_scheme", None))
        return render(
            request,
            "pws_portal/customer_dashboard.html",
            {
                "order_in_exception": order_in_exception["order_in_exception"],
                "total_orders": order["total_orders"],
                "orders": orders[0:5],
                "process_orders": process_orders[0:5],
                "exception_orders": exception_orders,
                "finish_orders": finish_orders[0:5],
                "order_in_process": order["order_in_process"],
                "order_in_finished": order["order_in_finished"],
                "greeting": greeting,
                "user_full_name": user_full_name,
                "customer_user": customer_user,
                "db_bg_color": theme_info["db_bg_color"],
            },
        )
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exception_tracking_search(request):
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
        if request.POST.get("order_number"):
            query.add(Q(order__order_number__icontains=request.POST["order_number"]), query.connector)
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
        user = User.objects.get(id=request.user.id)
        query.add(Q(order__user__user__username=user), query.connector)
        query.add(~Q(order__order_status="cancel"), query.connector)
        query.add(Q(order_in_exception=False), query.connector)
        query.add(Q(exception_status="put_to_customer"), query.connector)
        recordsTotal = OrderException.objects.filter(query).count()
        order_exceptions = (
            OrderException.objects.filter(query)
            .values(
                "id",
                "exception_nr",
                "order__order_number",
                "order__customer_order_nr",
                "created_on",
                "order__service__name",
                "created_by__username",
                "order__layer",
                "pre_define_problem__description",
                "order_status",
                "order__pcb_name",
                "order__order_date",
                "order__id",
                "order__delivery_date",
                "order__delivery_term",
            )
            .annotate(
                layer_column=Case(
                    When(order__layer__endswith=" L", then=(Cast(Replace("order__layer", Value(" L"), Value("")), output_field=IntegerField()))),
                    When(order__layer__in=layer_code_gtn, then=(Cast(Replace("order__layer", Value("L"), Value("")), output_field=IntegerField()))),
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

        layers_code = [order_["order__layer"] for order_ in order_exceptions]
        layer = Layer.objects.filter(code__in=layers_code).values("code", "name")
        layers = Util.get_dict_from_quryset("code", "name", layer)

        for order_exception in order_exceptions:
            response["data"].append(
                {
                    "id": order_exception["id"],
                    "order__order_number": order_exception["order__order_number"],
                    "order__customer_order_nr": order_exception["order__customer_order_nr"] if order_exception["order__customer_order_nr"] is not None else None,
                    "created_on": Util.get_local_time(order_exception["created_on"], True),
                    "order__service": order_exception["order__service__name"],
                    "order__layer": layers[order_exception["order__layer"]] if order_exception["order__layer"] in layers else None,
                    "order_status": dict(order_status)[order_exception["order_status"]] if order_exception["order_status"] in dict(order_status) else "",
                    "order_status_code": order_exception["order_status"],
                    "order__pcb_name": order_exception["order__pcb_name"],
                    "order__order_date": Util.get_local_time(order_exception["order__order_date"], True),
                    "order__id": order_exception["order__id"],
                    "pre_define_problem_des": order_exception["pre_define_problem__description"],
                    "delivery_date": Util.get_local_time(order_exception["order__delivery_date"]),
                    "delivery_term": order_exception["order__delivery_term"],
                    "sort_col": sort_col,
                    "recordsTotal": recordsTotal,
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exports_exception_tracking(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_export_exception_tracking", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        query = Q()
        if request.POST.get("ids"):
            selected_ids = list(map(int, request.POST.get("ids").split(",")))
            query.add(Q(id__in=selected_ids), query.connector)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        order_by = request.POST.get("order_by")
        if request.POST.get("order_number"):
            query.add(Q(order__order_number__icontains=request.POST["order_number"]), query.connector)
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
        query.add(Q(order__user__user__username=user), query.connector)
        query.add(~Q(order__order_status="cancel"), query.connector)
        query.add(Q(order_in_exception=False), query.connector)
        query.add(Q(exception_status="put_to_customer"), query.connector)
        exception_tracking = OrderException.objects.filter(query).values(
            "order__order_number",
            "order__customer_order_nr",
            "order_status",
            "order__pcb_name",
            "order__layer",
            "order__service__name",
            "order__order_date",
            "created_on",
        ).annotate(
            layer_column=Case(
                When(order__layer__endswith=" L", then=(Cast(Replace("order__layer", Value(" L"), Value("")), output_field=IntegerField()))),
                When(order__layer__in=layer_code_gtn, then=(Cast(Replace("order__layer", Value("L"), Value("")), output_field=IntegerField()))),
                When(order__layer="", then=None),
                default=None,
                output_field=IntegerField(),
            ),
        ).order_by(order_by)[start : (start + length)]
        layer_codes = [order["order__layer"] for order in exception_tracking if order["order__layer"]]
        layer = Layer.objects.filter(code__in=layer_codes).values("name", "code")
        layers_ = Util.get_dict_from_quryset("code", "name", layer)
        query_result = []
        for exception in exception_tracking:
            query_result.append(
                {
                    "order__order_number": exception["order__order_number"],
                    "order__customer_order_nr": exception["order__customer_order_nr"],
                    "order_status": exception["order_status"],
                    "order__pcb_name": exception["order__pcb_name"],
                    "order__layer": layers_[exception["order__layer"]] if exception["order__layer"] in layers_ else None,
                    "order__service__name": exception["order__service__name"],
                    "order__order_date": Util.get_local_time(exception["order__order_date"], True),
                    "created_on": Util.get_local_time(exception["created_on"], True),
                }
            )
        headers = [
            {"title": "PWS ID"},
            {"title": "Order number"},
            {"title": "Order status"},
            {"title": "PCB name"},
            {"title": "Layer"},
            {"title": "Service"},
            {"title": "Order date"},
            {"title": "Exception date"},
        ]
        return Util.export_to_xls(headers, query_result[:5000], "ExceptionTracking.xls")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def reply_exception_save(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_replay_exception", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            order_exception_id = request.POST.get("order_exception_id")
            order_status = request.POST.get("order_status")
            order_id = request.POST.get("order_id")
            model_remark_field = "remarks"
            remarks_back = request.POST.get("remarks_back")
            remarks_type_back = request.POST.get("remarks_type_back")
            c_ip = get_client_ip(request)
            action = AuditAction.INSERT
            order_number = request.POST.get("order_number")
            order_file = request.FILES.get("order_file")
            delivery_term = request.POST.get("delivery_term")
            delivery_term_days = delivery_term.replace("DEL_", "") if delivery_term and delivery_term != "No" else None
            if request.POST.get("delivery_date"):
                delivery_date = datetime.datetime.strptime(request.POST.get("delivery_date"), "%d/%m/%Y")
                current_date = datetime.datetime.now()
                if current_date >= delivery_date:
                    del_term_date = current_date + timedelta(int(delivery_term_days))
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
            else:
                delivery_date = None
            if order_file is not None:
                order_file_name = str(order_file)
                order_file_data = order_file.read()
                Order_Attachment.objects.filter(object_id=order_id, file_type__code="EXCEPTION_REPLY").update(deleted=True)
                upload_and_save_impersonate(order_file_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "EXCEPTION_REPLY", order_file_name, order_number, "")
            create_remark("pws", "order", order_id, remarks_back, "", request.user.id, model_remark_field, remarks_type_back, "", "")
            Order.objects.filter(id=order_id).update(order_status=order_status, in_time=datetime.datetime.now(), delivery_date=delivery_date)
            OrderException.objects.filter(id=order_exception_id).update(order_in_exception=True)
            Order_Attachment.objects.filter(object_id=order_id, file_type__code="EXCEPTION").update(deleted=True)
            log_views.insert("pws", "order", [order_id], action, request.user.id, c_ip, "Exception replied")
            return HttpResponse(AppResponse.msg(1, str("Exception replied Successfully")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def exception_tracking_order_cancel(request):
    try:
        user = User.objects.get(id=request.user.id)
        if Util.has_perm("can_cancel", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        c_ip = base_views.get_client_ip(request)
        action = AuditAction.UPDATE
        order_id = request.POST.get("order_id")
        exception_id = request.POST.get("exception_id")
        if order_id is not None:
            order = Order.objects.filter(id=order_id).values("order_status").first()
            Order.objects.filter(id=order_id).update(order_status="cancel", in_time=datetime.datetime.now(),order_next_status=None, order_previous_status="exception")
            Order_Attachment.objects.filter(object_id=order_id, file_type__code="EXCEPTION").update(deleted=True)
            OrderException.objects.filter(id=exception_id).update(order_in_exception=True)
            history_status = "Order has been " + " " + "<b>" + " " + "Cancel" + " " + "</b>" + " " + "from" + " " + "<b>" + " " + dict(order_status)[order["order_status"]] + " " + "</b>"
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
            email_id = [email_ids for email_ids in email_id.split(",")]
            subject = "Order cancelled - " + order_detail["company__name"] + " #" + order_detail["customer_order_nr"] + "."
            head = order_detail["company__name"] + " #" + order_detail["customer_order_nr"]
            title = "Dear customer,"
            title_ = "Order " + order_detail["customer_order_nr"] + " has been cancelled"
            message = render_to_string(
                "pws/mail_order.html",
                {
                    "mail_type": "cancel_order",
                    "title_": title_,
                    "head": head,
                    "title": title,
                    "layers": layers,
                    "order_detail": order_detail,
                },
            )
            send_mail(True, "public", [*email_id], subject, message, "", [cc_mail], mail_from)
        return HttpResponse(AppResponse.msg(1, str("Order canceled successfully")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def accept_preparation(request, pre):
    try:
        order_id = request.POST.get("id")
        if pre == "0":
            order = Order.objects.get(id=order_id)
            order.finished_on = datetime.datetime.now()
            order.save()
            return HttpResponse(AppResponse.msg(1, str("Order Completed Successfully")), content_type="json")
        else:
            order_number = request.POST.get("order_number")
            re_preparation_remark = request.POST.get("re_pre_remark")
            file = request.FILES.get("file")
            c_ip = base_views.get_client_ip(request)
            if file is not None:
                file_name = str(file)
                file_data = file.read()
                upload_and_save_impersonate(file_data, "pws", "order_attachment", order_id, request.user.id, c_ip, "ORDERFILE", file_name, order_number, "")
            order = Order.objects.get(id=order_id)
            order.remarks = re_preparation_remark
            order.save()
            return HttpResponse(AppResponse.msg(1, str("Re-preparation Successfully")), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong. " + str(e))
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e), content_type="json"))
