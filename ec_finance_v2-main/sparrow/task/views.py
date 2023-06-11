from cProfile import Profile
import datetime
from email import message
import itertools
import json
import logging
from datetime import date
from multiprocessing.dummy import Array
from urllib import response
from django.core.paginator import Paginator
from attachment.views import upload_and_save_impersonate
from django.contrib.postgres.aggregates import ArrayAgg
import base.views as base_views
import psycopg2 as pg
from accounts.models import UserProfile
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import choices
from base.models import AppResponse, TaskScheduler
from base.scheduler_view import create_task_scheduler
from base.util import Util
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from exception_log import manager
# from logistics.models import TransferOrder
from mails.views import send_email_by_tmpl, send_sms
from messaging.models import Notification
from messaging.notification_view import (subscribe_notifications,
                                         user_notification)
# from partners.models import Partner
from post_office.models import EmailTemplate
from stronghold.decorators import public
from task.forms import TaskForm
from task.models import Task, task_priority, task_status, Task_Attachment, Message
from base.choices import task_priority
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

# from tenant_schemas.utils import schema_context


def tasks(request):
    permissions = ''
    user_perms = User.objects.get(id=request.user.id)
    perms = ["can_add_message", "can_update_message", "can_delete_message"]
    permissions = Util.get_permission_role(user_perms, perms)
    return render(request, "task/tasks.html", {"permissions": json.dumps(permissions)})


def get_tasks(request, app_name=None, model_name=None, entity_id=None):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST) if "order" in request.POST else "-id"
        task_filter = request.COOKIES.get("taskFilter")
        if sort_col == "id" or sort_col == "-task_id":
            sort_col = "id"
        if sort_col == "task_id":
            sort_col = "-id"

        query = Q()
        # if request.POST.get("model_name") is not None:
        #     model_name = request.POST.get("model_name")
        #     if model_name == "Purchase order":
        #         model_name = "PurchaseOrder"
        #     elif model_name == "Sales order":
        #         model_name = "order"
        #     elif model_name == "Lead":
        #         model_name = "lead"
        #     elif model_name == "Receipt":
        #         model_name = "receipt"
        #     elif model_name == "Shipment":
        #         model_name = "shipment"

        if request.POST.get("name__icontains") is not None:
            query.add(Q(name__icontains=str(request.POST.get("name__icontains"))), query.connector)
        if request.POST.get("due_date__date") is not None:
            query.add(Q(due_date__date=datetime.datetime.strptime(str(request.POST["due_date__date"]), "%d/%m/%Y %H:%M").strftime("%m/%d/%Y %H:%M")), query.connector)
        if request.POST.get("task_type__name__icontains") is not None:
            query.add(Q(task_type__name__icontains=str(request.POST.get("task_type__name__icontains"))), query.connector)
        if request.POST.get("status__icontains") is not None:
            query.add(Q(status__icontains=str((request.POST.get("status__icontains")).replace(" ", "_"))), query.connector)
        if request.POST.get("priority__icontains") is not None:
            query.add(Q(priority__icontains=str(request.POST.get("priority__icontains"))), query.connector)

        if app_name != "0" and model_name != "0" and entity_id != "0":
            content_type = ContentType.objects.filter(app_label=app_name.lower(), model=model_name.lower()).first()
            query.add(Q(entity_id=int(entity_id), content_type=content_type), query.connector)
        # elif model_name != "0":
        #     if model_name == "crm":
        #         content_type_ids = ContentType.objects.filter(model__in=["contact", "lead", "deal"]).values_list("id", flat=True)
        #         query.add(Q(content_type_id__in=content_type_ids), query.connector)
        #     if model_name == "receipt":
        #         receipt_ids = TransferOrder.objects.filter(id__in=task_ids, transfer_type__in=["receipt", "so_return", "customer_supplied"]).values_list("id", flat=True)
        #         query.add(Q(entity_id__in=receipt_ids), query.connector)
        #     elif model_name == "shipment":
        #         ship_ids = TransferOrder.objects.filter(id__in=task_ids, transfer_type__in=["ship", "purchase_return"]).values_list("id", flat=True)
        #         query.add(Q(entity_id__in=ship_ids), query.connector)
        #     elif model_name != "crm":
        #         content_type = ContentType.objects.filter(model=model_name.lower()).first()
        #         query.add(Q(content_type=content_type), query.connector)
        #         # query.add(Q(content_type = content_type__app_label), query.connector)
        #     else:
        #         content_type = ContentType.objects.filter(model="transferorder").first()
        #         # task_ids = Task.objects.filter(content_type=content_type).values_list("entity_id", flat=True)

        if task_filter:
            if task_filter == "due_date":
                sort_col = "due_date"

            if task_filter == "assign_to":
                sort_col = "assign_to__first_name"

            if task_filter == "alphabetical":
                sort_col = "name"

            if task_filter != "completed":
                query.add(~Q(status="completed"), query.connector)
                if task_filter == "my" or task_filter == "my_due":
                    query.add(Q(assign_to_id=request.user.id), query.connector)
            else:
                query.add(Q(status="completed"), query.connector)

        else:
            query.add(~Q(status="completed"), query.connector)

        # tasks = (
        #     Task.objects.filter(~Q(status="completed"))
        #     .values(
        #         "id",
        #         "name",
        #         "description",
        #         "due_date",
        #         "status",
        #         "priority",
        #         "related_to",
        #         "entity_id",
        #         # "assign_to_id",
        #         # "assign_to",
        #         "created_by",
        #         "private",
        #         "assign_to_id",
        #         "created_by_id",
        #         "content_type",
        #         "content_type__model",
        #         "content_type__app_label",
        #         "assign_to__first_name",
        #         "assign_to__last_name",
        #         "created_by__first_name",
        #         "created_by__last_name",
        #         "created_on",
        #         "task_type_id",
        #         "task_type__name",
        #         "task_type__icon",
        #         "remarks",
        #     )
        #     .annotate(
        #         assign_to=ArrayAgg("assign_to")
        #     )
        #     .order_by(sort_col)[start:length]
        # )
        # Task.objects.filter(due_date__lte=datetime.datetime.now()).update(is_delete=True)
        task = (
            Task.objects.filter(is_delete=False, created_by=request.user.id)
            .values(
                "id",
                "name",
                "description",
                "due_date",
                "status",
                "priority",
                "related_to",
                "entity_id",
                "assign_to",
                "created_by",
                "created_by__username",
                "private",
                "created_by_id",
                "content_type",
                "created_on",
                "general"
            )
        ).order_by(sort_col, "-id")[start:length]

        user_ids = [tasks["created_by_id"] for tasks in task]
        users = User.objects.filter(id__in=user_ids).values("id", "first_name", "last_name")
        username = {}
        for user in users:
            username[user["id"]] = user["first_name"]+" "+user["last_name"]

        operator_ids = [tasks["created_by_id"] for tasks in task]
        users = UserProfile.objects.filter(user_id__in=operator_ids).values("user_id__username", "profile_image")
        imageurl = {}
        for user in users:
            imageurl[user["user_id__username"]] = user["profile_image"]

        date = {}
        for task_date_ in task:
            if task_date_["due_date"] is not None:
                if datetime.datetime.now() > task_date_["due_date"]:
                    date[task_date_["id"]] = "red"
                else:
                    date[task_date_["id"]] = "gray"
        user_task = Task.objects.filter(assign_to__in=[request.user.id]).exclude(status="completed").count()
        response = {
            # 'draw': request.POST['draw'] if request.POST['draw'] else '',
            "recordsTotal": task.count(),
            "recordsFiltered": task.count(),
            "user_count": user_task,
            "data": [],
            "tasks": [],
        }

        for task_ in task:
            current_time = datetime.datetime.now()
            created_on_time = task_["created_on"]
            time_diff = relativedelta(current_time, created_on_time)
            if time_diff.years:
                text = "year ago" if time_diff.years == 1 else "years ago"
                time_ = str(time_diff.years) + " " + text
            elif time_diff.months:
                text = "month ago" if time_diff.months == 1 else "months ago"
                time_ = str(time_diff.months) + " " + text
            elif time_diff.days:
                text = "day ago" if time_diff.days == 1 else "days ago"
                time_ = str(time_diff.days) + " " + text
            elif time_diff.hours:
                text = "hour ago" if time_diff.hours == 1 else "hours ago"
                time_ = str(time_diff.hours) + " " + text
            elif time_diff.minutes:
                text = "minute ago" if time_diff.minutes == 1 else "minutes ago"
                time_ = str(time_diff.minutes) + " " + text
            else:
                text = "second ago" if time_diff.seconds == 1 else "seconds ago"
                time_ = str(time_diff.seconds) + " " + text
            time = time_
            created_on_time = task_["created_on"]
            if "," in task_["assign_to"]:
                assign_to = task_["assign_to"].split(",")
                operator = Operator.objects.filter(id__in=assign_to).values("user__username", "user__id", "id")
                assign_to_username = [x["user__username"] for x in operator]
                assign_to_username = (",".join(assign_to_username)).replace(",",", ")
            else:
                assign_to = task_["assign_to"]
                operator = Operator.objects.filter(id=assign_to).values("user__username", "user__id", "id")
                assign_to_username = [x["user__username"] for x in operator]
            response["tasks"].append(
                {
                    "id": task_["id"],
                    "name": task_["name"],
                    "description": task_["description"],
                    "due_date": Util.get_local_time(task_["due_date"], True),
                    "priority": dict(task_priority)[task_["priority"]] if task_["priority"] in dict(task_priority) else "",
                    "related_to": task_["related_to"],
                    "entity_id": task_["entity_id"],
                    "created_by": task_["created_by"],
                    "private": task_["private"],
                    "created_by__username": task_["created_by__username"],
                    "created_by_id": task_["created_by_id"],
                    "content_type": task_["content_type"],
                    "assign_to": task_["assign_to"],
                    "assign_to_username": assign_to_username,
                    "created_on": Util.get_local_time(task_["created_on"], True),
                    "created_on_": time if created_on_time is not None else " ",
                    "username": username[task_["created_by_id"]] if task_["created_by_id"] in username else "",
                    "general": task_["general"],
                    "avatar" : Util.get_resource_url("profile", str(imageurl[task_["created_by__username"]])) if task_["created_by__username"] in imageurl and imageurl[task_["created_by__username"]] else "",
                    "current_date": date[task_["id"]] if task_["id"] in date else "",
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_task_calendar(request):
    try:
        # request.POST = Util.get_post_data(request)
        # query = Q()
        # task_filter = request.COOKIES.get("taskFilter")
        # user_id = request.user.id
        # model_name = request.POST.get("model_name")
        # if task_filter:
        #     if task_filter != "completed":
        #         query.add(~Q(status="completed"), query.connector)
        #         if task_filter == "my" or task_filter == "my_due":
        #             query.add(Q(assign_to_id=request.user.id), query.connector)
        #     else:
        #         query.add(Q(status="completed"), query.connector)
        # else:
        #     query.add(~Q(status="completed"), query.connector)
        #     query.add(Q(assign_to_id=request.user.id), query.connector)

        # current_month = int(request.POST.get("current_month"))
        # query.add(Q(due_date__month=current_month), query.connector)
        # response = {"data": []}

        # if model_name == "crm":
        #     content_type_ids = ContentType.objects.filter(model__in=["contact", "lead", "deal"]).values_list("id", flat=True)
        #     query.add(Q(content_type_id__in=content_type_ids), query.connector)

        # tasks = Task.objects.filter(query).values(
        #     "id",
        #     "name",
        #     "description",
        #     "due_date",
        #     "status",
        #     "priority",
        #     "related_to",
        #     "assign_to",
        #     "created_by",
        #     "private",
        #     "assign_to_id",
        #     "created_by_id",
        #     "assign_to__first_name",
        #     "assign_to__last_name",
        #     "created_by__first_name",
        #     "created_by__last_name",
        #     "created_on",
        #     "task_type_id",
        #     "task_type__name",
        #     "task_type__icon",
        #     "remarks",
        # )

        # assign_ids = tasks.values_list("assign_to_id", flat=True)

        # users = UserProfile.objects.filter(user_id__in=assign_ids).values("user_id", "profile_image")

        # imageurl = {}
        # for user in users:
        #     imageurl[user["user_id"]] = user["profile_image"]

        # for task in tasks:
        #     if task["private"]:
        #         if user_id != task["created_by_id"] and user_id != task["assign_to_id"]:
        #             continue
        #     img_src = Util.get_resource_url("profile", str(imageurl[task["assign_to_id"]])) if task["assign_to_id"] and imageurl[task["assign_to_id"]] else ""
        #     if task_filter == "overdue" or task_filter == "my_due":
        #         if Util.get_local_time(task["due_date"], True) and Util.get_local_time(datetime.datetime.utcnow(), True) > Util.get_local_time(task["due_date"], True):
        #             response["data"].append(
        #                 {"id": task["id"], "title": task["name"], "start": Util.get_local_time(task["due_date"], True, "%Y-%m-%dT%H:%M"), "imageurl": img_src, "color": "#FFA500"}
        #             )
        #     else:
        #         response["data"].append(
        #             {"id": task["id"], "title": task["name"], "start": Util.get_local_time(task["due_date"], True, "%Y-%m-%dT%H:%M"), "imageurl": img_src, "color": "#FFA500"}
        #         )
        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def task_kanban_data(request):
    try:
    #     request.POST = Util.get_post_data(request)
    #     query = Q()
    #     task_filter = request.COOKIES.get("taskFilter")
    #     start_length = request.POST.get("start_length")
    #     end_length = request.POST.get("end")
    #     model_name = request.POST.get("model_name")
    #     response = {"data": []}

    #     all_task_status = [key for key in dict(task_status).keys()]
    #     task_status_list = []
    #     status_name = request.POST.get("status_name", None)
    #     task_status_list = all_task_status if status_name is None else [status_name]

    #     response["all_task_status"] = all_task_status

    #     status_class = {}
    #     for status in all_task_status:
    #         if status == "completed":
    #             status_class[status] = "completed"
    #         elif status == "in_progress":
    #             status_class[status] = "inProgress"
    #         elif status == "not_started":
    #             status_class[status] = "notStarted"

    #     if task_filter:
    #         if task_filter != "completed":
    #             if task_filter == "my" or task_filter == "my_due":
    #                 query.add(Q(assign_to_id=request.user.id), query.connector)
    #         else:
    #             query.add(Q(status="completed"), query.connector)
    #     else:
    #         query.add(Q(assign_to_id=request.user.id), query.connector)

    #     if model_name == "crm":
    #         content_type_ids = ContentType.objects.filter(model__in=["contact", "lead", "deal"]).values_list("id", flat=True)
    #         query.add(Q(content_type_id__in=content_type_ids), query.connector)

    #     assign_ids = Task.objects.filter(query).values_list("assign_to_id", flat=True)
    #     users = UserProfile.objects.filter(user_id__in=assign_ids).values("user_id", "profile_image")
    #     imageurl = {}
    #     for user in users:
    #         imageurl[user["user_id"]] = user["profile_image"]

    #     for status in task_status_list:
    #         item = []
    #         tasks = (
    #             Task.objects.filter(query, status=status)
    #             .values("id", "name", "created_by_id", "due_date", "private", "assign_to_id", "assign_to__first_name", "assign_to__last_name", "remarks", "priority")
    #             .order_by("-id")[int(start_length) : int(end_length)]
    #         )
    #         total_tasks_count = Task.objects.filter(query, status=status).count()
    #         for task in tasks:
    #             if task["private"]:
    #                 if request.user.id != task["created_by_id"] and request.user.id != task["assign_to_id"]:
    #                     continue
    #             color = "gray"
    #             if Util.get_local_time(task["due_date"], True) and Util.get_local_time(datetime.datetime.utcnow(), True) > Util.get_local_time(task["due_date"], True):
    #                 color = "#EF7878"
    #             img_src = (
    #                 Util.get_resource_url("profile", str(imageurl[task["assign_to_id"]]))
    #                 if task["assign_to_id"] and task["assign_to_id"] in imageurl and imageurl[task["assign_to_id"]]
    #                 else ""
    #             )
    #             assign_info = (
    #                 '<img id="taskUserImg" src="'
    #                 + img_src
    #                 + '" width="22" height="22" title="'
    #                 + task["assign_to__first_name"]
    #                 + " "
    #                 + task["assign_to__last_name"]
    #                 + '" style="float:right">'
    #                 if img_src
    #                 else ""
    #             )
    #             assign_info += (
    #                 '<span class="icon-message-3-write" style="color: #989898;float:right;padding:3px;font-size:18px;margin-right: 5px;"></span>' if task["remarks"] else ""
    #             )
    #             if task["priority"] == "low":
    #                 task_priority = '<span style="background-color:#75bddf;color: #fff;padding:2px 4px;border-radius: 6px;">' + task["priority"]
    #             elif task["priority"] == "medium":
    #                 task_priority = '<span style="background-color:#feb739;color: #fff;padding:2px 4px;border-radius: 6px;">' + task["priority"]
    #             elif task["priority"] == "high":
    #                 task_priority = '<span style="background-color:#EF7878;color: #fff;padding:2px 4px;border-radius: 6px;">' + task["priority"]
    #             elif task["priority"] == "urgent":
    #                 task_priority = '<span style="background-color:red;color: #fff;padding:2px 4px;border-radius: 6px;">' + task["priority"]
    #             else:
    #                 task_priority = ""
    #             # assign_info += '<span class="assignName">'+task['assign_to__first_name']+' '+task['assign_to__last_name']+'</span>' if task['assign_to_id'] else ''
    #             due_date = Util.get_local_time(task["due_date"], True, "%d, %b") if task["due_date"] else ""
    #             assign_info += ' <span class="kanbanDueDate" style="color:' + color + ';float:left;margin-top: 2px;"> Due on ' + due_date + "</span>" if due_date else ""
    #             item.append({"id": str(task["id"]), "title": "<div>" + task["name"] + '</div><div style="margin-top: 12px;">' + assign_info + task_priority + "</div>"})
    #         response["data"].append(
    #             {
    #                 "id": status,
    #                 "title": dict(task_status)[status],
    #                 "item": item,
    #                 "class": status_class[status] if status != "cancelled" else "",
    #                 "total_" + status: total_tasks_count,
    #             }
    #         )
        response={}
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_task_status(request):
    try:
        task_id = int(request.POST.get("task_id"))
        task_status = request.POST.get("status_name")
        task = Task.objects.filter(id=task_id).update(status=task_status)
        task = (
            Task.objects.filter(id=task_id)
            .values(
                "id",
                "name",
                "description",
                "due_date",
                "status",
                "related_to",
                "priority",
                "assign_to",
                "assign_to_id",
                "created_by",
                "created_by_id",
                "assign_to__first_name",
                "assign_to__last_name",
                "entity_id",
                "created_by__first_name",
                "created_by__last_name",
                "created_on",
                "task_type_id",
                "content_type__model",
                "content_type__app_label",
                "task_type__name",
                "task_type__icon",
                "remarks",
                "private",
            )
            .first()
        )
        task_obj = get_task_obj(task)

        if task_obj["status"] == "Completed":
            send_notification(request, task_obj, "completed")

        return HttpResponse(AppResponse.msg(1, ""), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_event_date(request):
    try:
        task_id = request.POST.get("task_id")
        change_date = request.POST.get("drop_date").replace("T", " ")
        timezone = request.session["timezone"]
        change_date = datetime.datetime.strptime(change_date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        change_date = Util.get_utc_datetime(change_date, True, timezone)
        Task.objects.filter(id=task_id).update(due_date=change_date)
        return HttpResponse(AppResponse.msg(1, "Date changed"), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_task_obj(task):
    # first_name = task.assign_to__user__first_name if task.assign_to else ""
    first_name = task["assign_to__first_name"] if task["assign_to"] else ""
    last_name = task["assign_to__last_name"] if task["assign_to"] else ""
    cfirst_name = task["created_by__first_name"] if task["created_on"] else ""
    clast_name = task["created_by__last_name"] if task["created_on"] else ""
    is_due = False

    if Util.get_local_time(task["due_date"]) and str(date.today()) > task["due_date"].strftime("%Y-%m-%d"):
        is_due = True

    model_type = ""

    if task["content_type__app_label"] == "partners":
        if task["content_type__model"] == "partner":
            partner = Partner.objects.filter(id=task["entity_id"]).values("is_supplier", "is_customer").first()

            if partner["is_supplier"]:
                model_type = "supplier"

            if partner["is_customer"]:
                model_type = "customer"

    if task["content_type__app_label"] == "logistics":
        if task["content_type__model"] == "transferorder":
            trasfer_type = TransferOrder.objects.filter(id=task["entity_id"]).values("transfer_type").first()

            if trasfer_type["transfer_type"] == "ship":
                model_type = "shipment"

            if trasfer_type["transfer_type"] == "customer_supplied":
                model_type = "receipt"

    return {
        "id": task["id"],
        "task_id": task["id"],
        "name": task["name"],
        "description": task["description"],
        "related_to": task["related_to"],
        "due_date": Util.get_local_time(task["due_date"], True) if task["due_date"] is not None else "",
        "is_due": is_due,
        "task_type__name": task["task_type__name"],
        "task_type__icon": task["task_type__icon"],
        "status": dict(task_status).get(task["status"]),
        "priority": dict(task_priority).get(task["priority"]),
        "assign_to": first_name + " " + last_name,
        "created_by": cfirst_name + " " + clast_name,
        "created_on": Util.get_local_time(task["created_on"], True),
        "remarks": task["remarks"] if task["remarks"] is not None else "",
        "entityId": task["entity_id"],
        "private": task["private"],
        "assign_to_id": task["assign_to_id"],
        "created_by_id": task["created_by_id"],
        "modelName": task["content_type__model"],
        "appName": task["content_type__app_label"],
        "type": model_type,
    }


def task(request):
    try:
        if request.method == "POST":
            task_id = request.POST.get("id")
            assign_to_ = []
            list2 = []
            data = Task.objects.filter(id=task_id).values("assign_to")
            for x in data:
                assign_to_.append(x["assign_to"])
            task_status = json.dumps(dict(choices.task_status))
            task_priority = json.dumps(dict(choices.task_priority))
            show_private = False
            operators = Operator.objects.filter(is_deleted=False,is_active=True).values("operator_group", "id", "user__username")
            group_b = []
            group_fee = []
            customer = []
            backoffice_and_oth = []
            no_group = []
            no_group_ids = []
            group_b_ids = []
            group_fee_ids = []
            customer_ids = []
            backoffice_and_oth_ids = []
            for user in operators:
                if user["operator_group"] == "GROUP_B":
                    group_b_ids.append(user["id"])
                    group_b.append(
                        {
                            "id": user["id"],
                            "username": user["user__username"],
                        }
                    )
                if user["operator_group"] == "GROUP_FEE":
                    group_fee_ids.append(user["id"])
                    group_fee.append(
                        {
                            "id": user["id"],
                            "username": user["user__username"],
                        }
                    )
                if user["operator_group"] == "CUSTOMER":
                    customer_ids.append(user["id"])
                    customer.append(
                        {
                            "id": user["id"],
                            "username": user["user__username"],
                        }
                    )
                if user["operator_group"] == "BACKOFFICE_AND_OTH":
                    backoffice_and_oth_ids.append(user["id"])
                    backoffice_and_oth.append(
                        {
                            "id": user["id"],
                            "username": user["user__username"],
                        }
                    )
                if user["operator_group"] == None:
                    no_group_ids.append(user["id"])
                    no_group.append(
                        {
                            "id": user["id"],
                            "username": user["user__username"],
                        }
                    )
            if task_id is not None and task_id != "0":
                user = User.objects.get(id=request.user.id)
                if Util.has_perm("can_update_message", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                task = Task.objects.get(id=int(task_id))
                operator_ = task.assign_to
                select_oper_group_b = []
                select_oper_group_fee = []
                select_oper_customer = []
                select_oper_backoffice = []
                select_oper_no_group = []

                for data in operator_.split(","):
                    if int(data) in group_b_ids:
                        select_oper_group_b.append(int(data))
                    if int(data) in group_fee_ids:
                        select_oper_group_fee.append(int(data))
                    if int(data) in customer_ids:
                        select_oper_customer.append(int(data))
                    if int(data) in backoffice_and_oth_ids:
                        select_oper_backoffice.append(int(data))
                    if int(data) in no_group_ids:
                        select_oper_no_group.append(int(data))
                file = Task_Attachment.objects.filter(object_id=int(task_id),deleted=False).values("name","uid").last()
                if task.created_by_id == request.user.id:
                    show_private = True
                return HttpResponse(
                    render_to_string(
                        "task/task.html",
                        {
                            "task": task,
                            "file": file,
                            "data":operator_,
                            "select_oper_group_b":select_oper_group_b,
                            "select_oper_group_fee":select_oper_group_fee,
                            "select_oper_customer":select_oper_customer,
                            "select_oper_backoffice":select_oper_backoffice,
                            "select_oper_no_group":select_oper_no_group,
                            # "tz_info": tz_info,
                            "show_private": show_private,
                            "task_status": task_status,
                            "task_priority": task_priority,
                            "is_remark": True,
                            "group_b":group_b,
                            "group_fee":group_fee,
                            "customer":customer,
                            "backoffice_and_oth":backoffice_and_oth,
                            "no_group":no_group,
                        },
                    )
                )
            else:
                user = User.objects.get(id=request.user.id)
                if Util.has_perm("can_add_message", user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                return HttpResponse(
                    render_to_string(
                        "task/task.html",
                        {
                            # "tz_info": tz_info,
                            "assign_to_id": request.user.id,
                            "new_task": True,
                            "show_private": True,
                            "task_status": task_status,
                            "task_priority": task_priority,
                            "is_remark": False,
                            "group_b":group_b,
                            "group_fee":group_fee,
                            "customer":customer,
                            "backoffice_and_oth":backoffice_and_oth,
                            "no_group":no_group,
                        },
                    )
                )

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def save_task(request):
    try:

        with transaction.atomic():
            if request.method == "POST":
                file = request.FILES.get("file")
                draft = request.POST.get("draft")
                check = request.POST.get("check")
                form = None
                action = AuditAction.UPDATE
                task_id = request.POST.get("task_id")
                entity_id = request.POST.get("entity_id")
                related_to = request.POST.get("related_to")
                if related_to == "undefined":
                    related_to = None
                app_name = request.POST.get("app_name").lower()
                model_name = request.POST.get("model_name").lower()
                model_name = model_name if model_name != "crm" else "deal"
                app_name = app_name if app_name != "0" and model_name != "deal" else "crm"
                c_ip = base_views.get_client_ip(request)
                user_id = request.user.id
                id_group_b = request.POST.getlist("id_group_b")
                id_group_fee = request.POST.getlist("id_group_fee")
                id_customer = request.POST.getlist("id_customer")
                id_backoffice_and_oth = request.POST.getlist("id_backoffice_and_oth")
                id_other = request.POST.getlist("id_other")
                group_list = id_group_b + id_group_fee + id_customer + id_backoffice_and_oth + id_other
                operator_ids = ','.join(group_list)

                has_reminder = False
                if check == "check":
                    assign_to_operator = []
                    assign_to_ = Operator.objects.filter(is_active=True, is_deleted=False).values("id")
                    general = True
                    for ids in assign_to_:
                        assign_to_operator.append(ids["id"])
                    operator_ids = ",".join(map(str, assign_to_operator))
                else:
                    general =False

                if Util.is_integer(task_id) and int(task_id) in [0, -1]:
                    action = AuditAction.INSERT
                    form = TaskForm(request.POST)
                    form.assign_to = operator_ids
                else:
                    task = Task.objects.get(id=int(task_id))
                    form = TaskForm(request.POST, instance=task)


                reminder_on = request.POST.get("reminder_on", None)

                request.POST._mutable = True
                request.POST["reminder_on_text"] = reminder_on
                if request.POST["due_date"] is not None and request.POST["due_date"] != "":
                    request.POST["due_date"] = datetime.datetime.strptime(str(request.POST["due_date"]).strip(), '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')

                if reminder_on and request.POST["reminder_on"] == "OTHER":
                    if request.POST["due_date_reminder"]:
                        has_reminder = True
                        request.POST["reminder_on"] = datetime.datetime.strptime(str(request.POST["due_date"]).strip(), '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        request.POST["reminder_on"] = None

                elif reminder_on and request.POST["due_date"] and request.POST["reminder_on"]:
                    # user_profile = UserProfile.objects.filter(user_id=user_id).first()
                    # if user_profile.notification_email is None or user_profile.notification_email == "":
                    #     return HttpResponse(
                    #         AppResponse.msg(0, "Your email address is not set to receive notifications. Notification email can be set from your profile."), content_type="json"
                    #     )

                    reminder_on = request.POST.get("reminder_on")
                    minutes = 0
                    if reminder_on == "30_MIN_BFR":
                        minutes = 30
                    elif reminder_on == "1_HR_BFR":
                        minutes = 60
                    elif reminder_on == "3_HR_BFR":
                        minutes = 180
                    elif reminder_on == "6_HR_BFR":
                        minutes = 360
                    elif reminder_on == "24_HR_BFR":
                        minutes = 1440
                    if minutes:
                        has_reminder = True
                        request.POST["reminder_on"] = datetime.datetime.fromisoformat(request.POST["due_date"]) - datetime.timedelta(minutes=minutes)
                request.POST._mutable = False
                if form.is_valid():
                    task = form.save(commit=False)
                    if action == AuditAction.INSERT:
                        content_type = ContentType.objects.filter(app_label=app_name.lower(), model=model_name.lower()).first()
                        task.created_by_id = request.user.id
                        if entity_id == "0":
                            entity_id = None
                        task.entity_id = entity_id
                        task.content_type = content_type
                        task.related_to = related_to
                    task.general = general
                    task.assign_to = operator_ids
                    task.private = draft.capitalize()
                    task = form.save()
                    if task:
                        operator_id = task.assign_to.split(",")
                        Message.objects.filter(task_id_id=task.id).delete()
                        message = []
                        for operator_id_ in operator_id:
                            if not Message.objects.filter(task_id_id=task.id, operator_id_id=operator_id_):
                                message.append(Message(task_id_id=task.id, operator_id_id=operator_id_))
                        Message.objects.bulk_create(message)
                    task_id = task.id
                    message = "task"+ str(task_id)

                    if file is not None:
                        if Task_Attachment.objects.filter(object_id=task_id, file_type__code="MESSAGE_FILE", deleted=False).exists():
                            Task_Attachment.objects.filter(object_id=task_id, file_type__code="MESSAGE_FILE", deleted=False).update(deleted=True)
                        file_name = str(file)
                        file_data = file.read()
                        upload_and_save_impersonate(file_data, "task", "task_attachment", task_id, request.user.id, c_ip, "MESSAGE_FILE", file_name, message, "")
                    log_views.insert("task", "task", [task.id], action, request.user.id, c_ip, log_views.getLogDesc("Message has been", action))


                    # email_to = []

                    # if task.email_notification:
                    # if action == AuditAction.INSERT:
                    # if task.assign_to and task.created_by_id != task.assign_to_id:
                    #     email_to = [task.assign_to.email]
                    # else:
                    # if request.user.id != task.created_by_id:
                    #     email_to = [task.created_by.email]
                    # if task.assign_to and task.created_by.email != task.assign_to.email:
                    #     email_to = [task.created_by.email, task.assign_to.email]
                    # if task.assign_to and task.created_by_id != task.assign_to_id:
                    # if request.user.id == task.created_by_id:
                    #     email_to = [task.assign_to.email]
                    # if request.user.id == task.assign_to_id:
                    #     email_to = [task.created_by.email]

                    # task = (
                    #     Task.objects.filter(id=task.id)
                    #     .values(
                    #         "id",
                    #         "name",
                    #         "description",
                    #         "due_date",
                    #         "status",
                    #         "related_to",
                    #         "entity_id",
                    #         "priority",
                    #         "assign_to",
                    #         "assign_to_id",
                    #         "created_by",
                    #         "created_by_id",
                    #         "assign_to__first_name",
                    #         "assign_to__last_name",
                    #         "content_type",
                    #         "created_by__first_name",
                    #         "created_by__last_name",
                    #         "created_on",
                    #         "task_type_id",
                    #         "content_type__app_label",
                    #         "content_type__model",
                    #         "task_type__name",
                    #         "task_type__icon",
                    #         "remarks",
                    #         "private",
                    #     )
                    #     .first()
                    # )

                    # task_obj = get_task_obj(task)

                    # if action == AuditAction.INSERT:
                    #     send_notification(request, task_obj, "created")

                    # if task_obj["status"] == "Completed":
                    #     send_notification(request, task_obj, "completed")

                    # if has_reminder:
                    #     title = task_obj["name"]
                    #     url = "task/task_reminder/?task_id=" + str(task_obj["id"])
                    #     notification_email = ""
                    #     start_date = request.POST["reminder_on"].date().strftime("%d/%m/%Y")
                    #     start_time = request.POST["reminder_on"].time().strftime("%H:%M")

                    #     schedule = {"start_date": start_date, "start_time": start_time, "recur_type": "once"}

                    #     create_task_scheduler(title, url, json.dumps(schedule), notification_email, user_id, c_ip)

                    return HttpResponse(AppResponse.msg(1, "Message saved."), content_type="json")
                else:
                    return HttpResponse(AppResponse.msg(0, form.errors), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_notification(request, task_obj, notification_type):
    # Below code for when task will marked as public:
    if not task_obj["private"]:
        subscribe_notifications(
            request.user.id,
            "others",
            "task",
            "new",
            task_obj["id"],
            id=task_obj["id"],
            related_to=task_obj["related_to"],
            task_name=task_obj["name"],
            user_name=task_obj["created_by"],
            due_date=task_obj["due_date"],
            status=task_obj["status"],
            priority=task_obj["priority"],
            assign_to=task_obj["assign_to"],
            assign_to_id=task_obj["assign_to_id"],
            description=task_obj["description"],
            private=task_obj["private"],
            subject=task_obj["name"] + " " + notification_type,
        )

    user_notification(
        request,
        request.user.id,
        "others",
        "task",
        "new",
        task_obj["id"],
        id=task_obj["id"],
        related_to=task_obj["related_to"],
        task_name=task_obj["name"],
        user_name=task_obj["created_by"],
        due_date=task_obj["due_date"],
        status=task_obj["status"],
        priority=task_obj["priority"],
        assign_to=task_obj["assign_to"],
        description=task_obj["description"],
        subject=task_obj["name"] + " " + notification_type,
    )
    # Below code for when task will marked as private also task creator and assign-to person must be different:
    if task_obj["private"] and task_obj["assign_to_id"] != task_obj["created_by_id"]:
        user_notification(
            request,
            task_obj["assign_to_id"],
            "others",
            "task",
            "new",
            task_obj["id"],
            id=task_obj["id"],
            related_to=task_obj["related_to"],
            task_name=task_obj["name"],
            user_name=task_obj["created_by"],
            due_date=task_obj["due_date"],
            status=task_obj["status"],
            priority=task_obj["priority"],
            assign_to=task_obj["assign_to"],
            description=task_obj["description"],
            subject=task_obj["name"] + " " + notification_type,
        )


def task_delete(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.user.id)
            if Util.has_perm("can_delete_message", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
            task_id = int(request.POST.get("id"))
            c_ip = base_views.get_client_ip(request)
            Task.objects.filter(id=int(task_id)).update(is_delete=True)
            Message.objects.filter(task_id=task_id).update(is_delete=True)
            # if user.has_perm('task.delete_task') == False:
            #     return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type='json')

            # task.delete()
            log_views.insert("task", "task", [task_id], AuditAction.DELETE, request.user.id, c_ip, "Message has been deleted.")
            return HttpResponse(AppResponse.msg(1, "Message has been deleted."), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def reminder_for_task():
    with schema_context(settings.PURCHASE_PLAN_SCHEMA):
        try:
            query = Q()
            time_now = datetime.datetime.utcnow().replace(tzinfo=utc)

            furure_time_age = datetime.timedelta(minutes=31)
            future_time = time_now + furure_time_age

            past_time_age = datetime.timedelta(minutes=-31)
            past_time = time_now + past_time_age

            query.add(Q(due_date__range=(past_time, future_time), due_mail_sent_time__isnull=True, email_notification=True), query.connector)
            query.add(~Q(status__in=["completed", "cancelled"]), query.connector)

            tasks = Task.objects.filter(query)

            template = EmailTemplate.objects.filter(name__icontains="tasks_overdue").values("id")

            dbname = settings.DATABASES["default"]["NAME"]
            user = settings.DATABASES["default"]["USER"]
            password = settings.DATABASES["default"]["PASSWORD"]
            host = settings.DATABASES["default"]["HOST"]
            port = settings.DATABASES["default"]["PORT"]
            db = pg.connect(dbname=dbname, user=user, password=password, host=host, port=port)
            cursor = db.cursor()
            cursor.execute(""" select domain_url from clients_client where schema_name ='%s' """ % (settings.PURCHASE_PLAN_SCHEMA))
            domain = cursor.fetchone()[0]
            db.close()

            if "http://" not in domain or "https://" not in domain:
                domain = "http://" + domain

            url = domain + "/b/#/task/tasks/"

            due_email_data = []

            for task in tasks:
                profile_assign_obj = UserProfile.objects.filter(user_id__in=[task.assign_to_id, task.created_by_id]).values("user_id", "notification_email")
                email_of_assign = ""
                email_of_created = ""
                for email in profile_assign_obj:
                    if email["user_id"] == task.assign_to_id:
                        email_of_assign = email["notification_email"]
                    elif email["user_id"] == task.created_by_id:
                        email_of_created = email["notification_email"]

                has_assign_data = False
                has_created_data = False

                for due_data in due_email_data:
                    if due_data["email"] == email_of_assign:
                        has_assign_data = True

                    if due_data["email"] == email_of_created:
                        has_created_data = True

                if has_assign_data is False and email_of_assign is not None:
                    context_task = list(
                        filter(
                            lambda n: (n["assign_to_id"] == task.assign_to_id or n["created_by_id"] == task.assign_to_id),
                            tasks.values("id", "name", "created_by_id", "assign_to_id"),
                        )
                    )

                    context = {"user": task.assign_to.first_name, "count": len(context_task), "task_overdue_url": url, "tasks": list(context_task[:10])}

                    due_email_data.append({"email": email_of_assign, "context": context})

                if has_created_data is False and email_of_created is not None:
                    context_task = list(
                        filter(
                            lambda n: (n["assign_to_id"] == task.created_by_id or n["created_by_id"] == task.created_by_id),
                            tasks.values("id", "name", "created_by_id", "assign_to_id"),
                        )
                    )

                    context = {"user": task.created_by.first_name, "count": len(context_task), "task_overdue_url": url, "tasks": list(context_task[:10])}

                    due_email_data.append({"email": email_of_created, "context": context})

            for email_data in due_email_data:
                send_email_by_tmpl(True, settings.PURCHASE_PLAN_SCHEMA, [email_data["email"]], template[0]["id"], email_data["context"])

            for task in tasks:
                task.due_mail_sent_time = datetime.datetime.utcnow()
                task.save()

        except Exception as e:
            manager.create_from_exception(e)
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
@csrf_exempt
def task_reminder(request, scheduler_key):
    try:
        # task_id = int(request.GET.get("task_id"))
        # if scheduler_key == settings.SCHEDULER_KEY:
        #     task = (
        #         Task.objects.filter(id=task_id, has_reminder_sent=False)
        #         .values(
        #             "id",
        #             "name",
        #             "due_date",
        #             "reminder_on",
        #             "assign_to_id",
        #             "assign_to__first_name",
        #             "assign_to__last_name",
        #             "created_by_id",
        #             "created_by__first_name",
        #             "created_by__last_name",
        #             "related_to",
        #             "status",
        #             "priority",
        #             "description",
        #         )
        #         .first()
        #     )
        #     if task:
        #         created_by_contact = UserProfile.objects.filter(user_id=task["created_by_id"]).values("user_id", "notification_email", "notification_mob").first()
        #         template = EmailTemplate.objects.filter(name="task_reminder").first().id
        #         mail_context = {
        #             "task_name": task["name"],
        #             "user_name": task["created_by__first_name"] + " " + task["created_by__last_name"],
        #             "related_to": task["related_to"],
        #             "due_date": Util.get_local_time(task["due_date"], True),
        #             "status": dict(task_status).get(task["status"]),
        #             "priority": dict(task_priority).get(task["priority"]),
        #             "assign_to": task["assign_to__first_name"] + " " + task["assign_to__last_name"] if task["assign_to_id"] else "-",
        #             "description": task["description"],
        #         }
        #         sms_context = {"task_name": task["name"]}
        #         send_email_to = {}
        #         send_sms_to = {}

        #         if task["assign_to_id"]:
        #             #  Below condition will avoid if assign-to person and task creator are same then person got twice email-reminder.
        #             if task["assign_to_id"] != task["created_by_id"]:
        #                 assign_to_contact = UserProfile.objects.filter(user_id=task["assign_to_id"]).values("user_id", "notification_email", "notification_mob").first()

        #                 send_email_to[assign_to_contact["user_id"]] = assign_to_contact["notification_email"]
        #                 send_sms_to[assign_to_contact["user_id"]] = assign_to_contact["notification_mob"]

        #                 send_email_by_tmpl(False, "public", [send_email_to[task["assign_to_id"]]], template, mail_context)

        #                 Notification.objects.create(subject=task["name"], text=task["name"], user_id=task["assign_to_id"])
        #                 if send_sms_to[task["assign_to_id"]]:
        #                     send_sms([send_sms_to[task["assign_to_id"]]], "task_reminder", sms_context)

        #         send_email_to[created_by_contact["user_id"]] = created_by_contact["notification_email"]
        #         send_sms_to[created_by_contact["user_id"]] = created_by_contact["notification_mob"]

        #         send_email_by_tmpl(False, "public", [send_email_to[task["created_by_id"]]], template, mail_context)

        #         Notification.objects.create(subject=task["name"], text=task["name"], user_id=task["created_by_id"])
        #         if send_sms_to[task["created_by_id"]]:
        #             send_sms([send_sms_to[task["created_by_id"]]], "task_reminder", sms_context)

        #         Task.objects.filter(id=task["id"]).update(has_reminder_sent=True)
        #         url = "task/task_reminder/?task_id=" + str(task["id"])
        #         task = TaskScheduler.objects.filter(url=url).first()
        #         # log_views.insert("base", "taskscheduler", [task.id], AuditAction.DELETE, admin_user["user_id"], c_ip, log_views.getLogDesc(task.title, AuditAction.DELETE))
        #         task.delete()
        return HttpResponse(AppResponse.msg(1, ""), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def messages(request):
    try:
        task = (
                Message.objects.filter((Q(task_id__due_date__gte=datetime.datetime.now()) | Q(task_id__due_date__isnull=True)),task_id__private=False, operator_id__user__username=request.user, is_delete=False)
                .values(
                    "id",
                    "task_id__name",
                    "task_id__description",
                    "task_id__due_date",
                    "task_id__priority",
                    "task_id__private",
                    "task_id__created_by__username",
                    "operator_id__user__username",
                    "task_id__general",
                    "is_read",
                    "task_id__created_by_id",
                    "created_on"
                )
                .annotate(
                    assign_to=ArrayAgg("task_id__assign_to")
                )
            ).order_by("-created_on")
        operator_ids = [tasks["task_id__created_by_id"] for tasks in task]
        users = UserProfile.objects.filter(user_id__in=operator_ids).values("user_id__username", "profile_image")
        imageurl = {}
        for user in users:
            imageurl[user["user_id__username"]] = user["profile_image"]

        user_ids = [tasks["task_id__created_by_id"] for tasks in task]
        users = User.objects.filter(id__in=user_ids).values("id","first_name","last_name")
        username = {}
        for user in users:
            username[user["id"]] = user["first_name"]+" "+user["last_name"]
        tasks = []
        for task_ in task:
            current_time = datetime.datetime.now()
            created_on_time = task_["created_on"]
            time_diff = relativedelta(current_time, created_on_time)
            if time_diff.years:
                text = "year ago" if time_diff.years == 1 else "years ago"
                time_ = str(time_diff.years) + " " + text
            elif time_diff.months:
                text = "month ago" if time_diff.months == 1 else "months ago"
                time_ = str(time_diff.months) + " " + text
            elif time_diff.days:
                text = "day ago" if time_diff.days == 1 else "days ago"
                time_ = str(time_diff.days) + " " + text
            elif time_diff.hours:
                text = "hour ago" if time_diff.hours == 1 else "hours ago"
                time_ = str(time_diff.hours) + " " + text
            elif time_diff.minutes:
                text = "minute ago" if time_diff.minutes == 1 else "minutes ago"
                time_ = str(time_diff.minutes) + " " + text
            else:
                text = "second ago" if time_diff.seconds == 1 else "seconds ago"
                time_ = str(time_diff.seconds) + " " + text
            time = time_
            created_on_time = task_["created_on"]
            tasks.append(
                {
                    "id": task_["id"],
                    "task_id__name": task_["task_id__name"],
                    "task_id__description": task_["task_id__description"],
                    "task_id__due_date": task_["task_id__due_date"],
                    "task_id__priority": dict(task_priority)[task_["task_id__priority"]] if task_["task_id__priority"] in dict(task_priority) else "",
                    "task_id__private": task_["task_id__private"],
                    "task_id__created_by__username": task_["task_id__created_by__username"],
                    "operator_id__user__username": task_["operator_id__user__username"],
                    "task_id__general": task_["task_id__general"],
                    "is_read": task_["is_read"],
                    "username": username[task_["task_id__created_by_id"]] if task_["task_id__created_by_id"] in username else "",
                    "created_on_": task_["created_on"],
                    "created_on": time if created_on_time is not None else " ",
                    "avatar" : Util.get_resource_url("profile", str(imageurl[task_["task_id__created_by__username"]])) if task_["task_id__created_by__username"] in imageurl and imageurl[task_["task_id__created_by__username"]] else "",
                }
            )
        return render(request, "task/messages.html", {"tasks": tasks})
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def task_detail(request):
    try:
        id = request.POST.get("id")
        task =Message.objects.filter(id=id).values("id","task_id", "task_id__name", "task_id__description", "task_id__priority", "is_read").first()
        if task["is_read"] == False:
            Message.objects.filter(id=id).update(is_read=True, read_on=datetime.datetime.now())
        files = Task_Attachment.objects.filter(object_id=task["task_id"],deleted=False).values("name", "uid").last()
        response = {
            "id": task["id"],
            "task_name": task["task_id__name"],
            "task_description": task["task_id__description"],
            "task_priority": dict(task_priority)[task["task_id__priority"]] if task["task_id__priority"] in dict(task_priority) else "",
            "file": files["name"] if files else None,
            "uid": files["uid"] if files else None,
        }
        return render(request, "task/message.html", {"task": response})
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def message_read(request):
    try:
        id = request.POST.get("id")
        if id == "true":
            Message.objects.filter(operator_id__user__username=request.user,task_id__general=False, is_read=False, is_delete=False).update(is_read=True, read_on=datetime.datetime.now())
        else:
            Message.objects.filter(operator_id__user__username=request.user,task_id__general=True, is_read=False, is_delete=False).update(is_read=True, read_on=datetime.datetime.now())
        response = []
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def message_unread(request):
    try:
        id = request.POST.get("id")
        Message.objects.filter(id=id).update(is_read=False, read_on=None)
        response = {"code": 1, "msg": "Message unread"}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_message(request):
    try:
        id = request.POST.get("id")
        Message.objects.filter(id=id).update(is_delete=True)
        response = {"code": 1, "msg": "Message has been deleted"}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def unread_message(request):
    try:
        id = request.POST.get("id")
        is_read_ = request.POST.get("is_read")
        if is_read_ == "True":
            is_read = False
            read_on = None
            msg = "Message unread"
        else:
            is_read = True
            read_on = datetime.datetime.now()
            msg = "Message read"

        Message.objects.filter(id=id).update(is_read=is_read, read_on=read_on)
        response = {"code": 1, "msg": msg}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_file(request):
    try:
        id = request.POST.get("id")
        Task_Attachment.objects.filter(uid=id).update(deleted=True)
        response = {}
        return HttpResponse(json.dumps(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")

