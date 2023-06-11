import json
from datetime import timedelta

from auditlog.models import AuditAction, Auditlog
from base.models import AppResponse, User
from base.util import Util
from dateutil import parser
# from sparrow.settings import EC_API_URL
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from exception_log import manager
from qualityapp.models import CompanyUser, Operator, Order


def logs(request, model=None, ids=None):
    operator_id = Operator.objects.filter(user=request.user.id).values("id").first()
    customer_user = None
    if operator_id is None:
        customer_user = True
    else:
        customer_user = False
    if model == "order_attachment":
        order_attachment= True
    else:
        order_attachment =False
    return render(request, "auditlog/logs.html", {"customer_user": customer_user, "order_attachment":order_attachment})


def logs_search(request, model=None, ids=None):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        q_objects = Q()
        sort_col = Util.get_sort_column(request.POST)
        if model != "unidentified_parts" and model != "stencil_parts":
            if ids is not None and ids != "":
                obejct_ids = [int(x) for x in ids.split("-")]
                # q_objects &= Q(object_id__in = obejct_ids)
                q_objects.add(Q(object_id__in=obejct_ids), q_objects.connector)
            if model is not None:
                q_objects.add(Q(content_type_id__model__in=[str(model)]), q_objects.connector)

            if request.POST["order"][0]["column"] == 0 and request.POST["order"][0]["dir"] == "asc":
                sort_col = "action_on"

            customer_user_id = CompanyUser.objects.filter(user=request.user.id).values("id").first()
            if customer_user_id:
                action_desc = [
                    "Order has been created",
                    "Exception sent to Customer.",
                    "Exception replied",
                    "Order has been updated",
                    "Order has been Cancelled",
                    "Set order priority",
                    "Order has been finished",
                ]
                q_objects.add(Q(descr__in=action_desc) | Q(descr__endswith="has been Upload."), q_objects.connector)
                # q_objects.add(Q(descr__in=action_desc) | Q(descr__startswith="Order has been  <b> Finished </b>") | Q(descr__startswith="Order status changed  <b> Order Finish </b>") | Q(descr__endswith="has been Upload."), q_objects.connector)

            recordsTotal = Auditlog.objects.filter(q_objects).count()
            logs = (
                Auditlog.objects.filter(q_objects)
                .values("id", "action_by__username", "ip_addr", "action__name", "action_by", "descr", "action_on", "object_id", "operator__user__username", "prep_time")
                .order_by(sort_col)[start : (start + length)]
            )
            response = {
                "code": 1,
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }

            for log in logs:
                time_taken = None
                if log["prep_time"] is not None:
                    pre = int(log["prep_time"])
                    hour = pre // 3600
                    pre %= 3600
                    minutes = pre // 60
                    pre %= 60
                    preparation_time = str(hour) + ":" + str(minutes).zfill(2)
                    time_taken = int(log["prep_time"])
                action_on = Util.get_local_time(log["action_on"], "%d/%m/%Y%H:%M:%S")
                customer_user_id = CompanyUser.objects.filter(user=request.user.id).values("id").first()
                if customer_user_id:
                    customer_user_ids = CompanyUser.objects.filter(user=log["action_by"]).values("id").first()
                    if customer_user_ids:
                        is_customer_user = log["action_by__username"].split(")")[-1]
                    else:
                        is_customer_user = ""
                else:
                    is_customer_user = log["action_by__username"].split(")")[-1]

                response["data"].append(
                    {
                        "id": log["id"],
                        "action_by__username": is_customer_user,
                        "ip_addr": log["ip_addr"],
                        "action__name": log["action__name"],
                        "descr": log['descr'],
                        "object_id": log["object_id"],
                        "action_on": action_on,
                        "operator__user__username": log["operator__user__username"],
                        "prep_time": preparation_time if time_taken is not None else "",
                    }
                )

        elif model == "unidentified_parts":

            # THIS IS ONLY FOR Unidentified Parts from VCDB due to API Keys

            part_id = ids
            payload = json.dumps({"key": settings.SPARROW_API_KEY, "funname": "GetUnidentifiedPartHistory", "param": {"Id": part_id}})
            headers = {"Content-Type": "application/json"}
            response = Util.stencil_post_data(payload, headers, "POST")
            response = response.json()
            logs = json.loads(response)
            response = history_unidentified__and_stencil_parts(model, logs, request)

        # THIS IS ONLY FOR Stencil Parts

        elif model == "stencil_parts":
            dataset_number = ids
            user_id = request.user.id
            payload = json.dumps({"funname": "StencilDataSetHistory", "key": "yhlC0v6OTSY0lys9MHmFWkhYyzyaEG09", "param": {"number": dataset_number, "user_id": user_id}})
            headers = {"Content-Type": "application/json"}
            response = Util.stencil_post_data(payload, headers, "POST")
            response = response.json()
            logs = json.loads(response)
            response = history_unidentified__and_stencil_parts(model, logs, request)

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def history_unidentified__and_stencil_parts(model, logs, request):
    try:
        recordsTotal = len(logs["data"])
        response = {
            "code": 1,
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        logs["descr"] = None
        logs["object_id"] = None
        user_id_list = []
        for log in logs["data"]:
            if model == "unidentified_parts":
                user_id = log["UserId"]
            else:
                user_id = log["user_id"]
            user_id_list.append(user_id)
        user_names = User.objects.filter(id__in=user_id_list).values("username", "id")
        user_names = Util.get_dict_from_quryset("id", "username", user_names)

        for log in logs["data"]:

            if model == "unidentified_parts":
                action_by__username = user_names[log["UserId"]] if log["UserId"] in user_names else None
                description = log["Action"] + " - " + log["Operator_name"]
                id = log["bspid"]
                date = parser.parse(log["Changed_date"])
                action_on = Util.get_local_time(date, "%d/%m/%Y%H:%M:%S")

            elif model == "stencil_parts":
                action_by__username = user_names[log["user_id"]] if log["user_id"] in user_names else None
                description = log["action"] + " for " + log["number"] if log["action"] is not None and log["number"] is not None else ""
                id = ""
                date = parser.parse(log["created_on"])
                action_on = Util.get_local_time(date, "%d/%m/%Y%H:%M:%S")
            response["data"].append(
                {"id": id, "action_by__username": action_by__username, "ip_addr": "", "action__name": "", "descr": description, "object_id": "", "action_on": action_on}
            )
        return response
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def insert(app_name, model_name, object_ids, action_id, action_by_id, ip_addr, descr):
    app_name = app_name.lower()
    model_name = model_name.lower()
    model_id = ContentType.objects.filter(app_label=app_name, model=model_name)[0].id
    for object_id in object_ids:
        log = Auditlog(content_type_id=model_id, object_id=object_id, action_id=action_id, action_by_id=action_by_id, ip_addr=ip_addr, descr=descr)
        log.save()


def insert_(app_name, model_name, object_ids, action_id, action_by_id, ip_addr, descr, operator, pre_time):
    app_name = app_name.lower()
    model_name = model_name.lower()
    model_id = ContentType.objects.filter(app_label=app_name, model=model_name)[0].id
    for object_id in object_ids:
        log = Auditlog(
            content_type_id=model_id, object_id=object_id, action_id=action_id, action_by_id=action_by_id, ip_addr=ip_addr, descr=descr, operator_id=operator, prep_time=pre_time
        )
        log.save()


def getLogDesc(entity, action_id):
    if action_id == AuditAction.INSERT:
        return entity + " created"
    elif action_id == AuditAction.UPDATE:
        return entity + " updated"
    elif action_id == AuditAction.DELETE:
        return entity + " deleted"
    else:
        return ""
