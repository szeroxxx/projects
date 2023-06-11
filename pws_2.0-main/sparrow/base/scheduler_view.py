import datetime
import json
import logging
import threading
import time
import urllib
import urllib.request
from datetime import timedelta

from auditlog import views as log_views
from auditlog.models import AuditAction
from cron_descriptor import get_description
from croniter import croniter
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt
from post_office.models import EmailTemplate
from sparrow.decorators import check_view_permission
from stronghold.decorators import public

import base.views as base_views
from base.forms import TaskScheduleForm
from base.models import AppResponse, TaskScheduler
from base.util import Util


def execute_scheduler(schema, task, doamin_url):
    with schema_context(schema):
        TaskScheduler.objects.filter(id=task["id"]).update(is_running=True)
        task_url = task["url"].split("?")
        if len(task_url) > 1:
            # if task["url"].startswith("eda/"):
            #     url = doamin_url + "/" + task_url[0] + "?" + task_url[1]
            # else:
            url = doamin_url + "/" + task_url[0] + "" + settings.SCHEDULER_KEY + "/?" + task_url[1]
        else:
            # if task["url"].startswith("eda/"):
            #     url = doamin_url + "/" + task_url[0]
            # else:
            url = doamin_url + "/" + task_url[0] + "" + settings.SCHEDULER_KEY + "/"

        next_run = None
        last_run = task["next_run"]
        response = run_scheduler_post(url)

        if task["pattern"] not in ["", None]:
            next_run = croniter(task["pattern"], datetime.datetime.utcnow()).get_next(datetime.datetime)

        TaskScheduler.objects.filter(id=task["id"]).update(last_run=last_run, next_run=next_run, last_run_result=response, is_running=False)
        if task["notification_email"] not in ["", None]:
            send_scheduler_mail(task["notification_email"], task["title"], next_run, last_run, response, schema)


def send_scheduler_mail(email, title, next_run, last_run, last_run_result, schema):
    email_to = email.split(",")
    template = EmailTemplate.objects.filter(name__iexact="scheduler_notification").first()
    mail_context = Context({"title": title, "last_run": last_run, "last_run_result": last_run_result, "next_run": next_run if next_run is not None else "-"})
    template_subject = Template(template.subject).render(mail_context)
    template_content = Template(template.html_content).render(mail_context)
    send_mail(True, schema, email_to, template_subject, template_content, [])


def db_table_exists(table_name):
    return table_name in connection.introspection.table_names()


@public
@csrf_exempt
def start_schedulers(request):
    try:
        schema = "public"
        doamin_url = request.POST["client_domain"]
        two_hour_before = datetime.datetime.utcnow() - timedelta(hours=1)
        TaskScheduler.objects.filter(is_active=True, is_running=True, last_run__lte=two_hour_before).update(is_running=False)
        task_schedulers = TaskScheduler.objects.filter(is_active=True, is_running=False).values("next_run", "pattern", "id", "url", "notification_email", "title", "is_running")

        for task_scheduler in task_schedulers:
            if (task_scheduler["next_run"] not in ["", None]) and (time.mktime(task_scheduler["next_run"].timetuple()) <= time.mktime(datetime.datetime.utcnow().timetuple())):
                thread = threading.Thread(target=execute_scheduler, args=(schema, task_scheduler, doamin_url,))
                thread.setDaemon(True)
                thread.start()
        return HttpResponse(AppResponse.msg(1, ""), content_type="json")
    except Exception as e:
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
@csrf_exempt
def sheduler_format(request, scheduler_key=""):
    if scheduler_key == settings.SCHEDULER_KEY:

        """
            Always add scheduler_kye param
            Always create schedule in this formate
        """
        print("===========================================================")
        time.sleep(120)
        return HttpResponse(AppResponse.msg(1, "Success"), content_type="json")
    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")


def run_scheduler(request):
    try:
        doamin_url = ""
        # from clients.models import Client

        schemas = Client.objects.all().values("schema_name", "domain_url")
        for schema in schemas:
            with schema_context(schema["schema_name"]):
                table_name = db_table_exists("base_taskscheduler")
                if table_name is False:
                    continue

                doamin_url = "http://" + schema["domain_url"]
        task_url = request.POST["url"].split("?")
        if len(task_url) > 1:
            url = doamin_url + "/" + task_url[0] + "" + settings.SCHEDULER_KEY + "/?" + task_url[1]
        else:
            if request.POST["url"].startswith("logistics/"):
                url = doamin_url + "/" + task_url[0]
            else:
                url = doamin_url + "/" + task_url[0] + "" + settings.SCHEDULER_KEY + "/"
        req = urllib.request.Request(url)
        req.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(req).read()
        return HttpResponse(AppResponse.msg(1, json.loads(response)["msg"]), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def run_scheduler_post(post_url):
    try:
        req = urllib.request.Request(post_url)
        response = urllib.request.urlopen(req).read()
        return response[:500]
    except Exception as e:
        return str(e)[:500]


def task_scheduler(request):
    try:
        task_scheduler = TaskScheduler.objects.filter(id=request.POST["id"]).values("title", "schedule", "url", "id", "notification_email", "is_active", "is_running").first()
        response = {
            "task_scheduler": task_scheduler,
        }
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)


def schedule_pattern(schedule):
    if schedule != "":
        obj = json.loads(schedule)
        date_time = str(obj["start_date"] + " " + obj["start_time"]).replace(" ", "/").replace(":", "/").split("/")

        if obj["recur_type"] == "infinity":
            if obj["infinity_type"] == "minute":
                return "*/" + obj["recur_inf_time"] + " * * * *"
            elif obj["infinity_type"] == "hours":
                return date_time[4] + " */" + obj["recur_inf_time"] + " * * *"
        elif obj["recur_type"] == "once":
            return ""
        elif obj["recur_type"] == "daily":
            return date_time[4] + " " + date_time[3] + " */" + obj["recur_day"] + " * *"
        elif obj["recur_type"] == "weekly":
            week_days = ",".join(obj["recur_week_days"])
            return date_time[4] + " " + date_time[3] + " * * " + week_days
        elif obj["recur_type"] == "monthly":
            # "0" Means Last day of month
            if "0" in obj["recur_month_days"]:
                obj["recur_month_days"].remove("0")
                obj["recur_month_days"].append("L")

            month_days = ",".join((map(str, obj["recur_month_days"])))

            return date_time[4] + " " + date_time[3] + " " + str(month_days) + " * *"
    return ""


def save_task_schedule(request):
    try:
        if request.method == "POST":
            request.POST._mutable = True  # make the QueryDict mutable

            form, task = None, None
            task_id = request.POST["id"]
            action = AuditAction.INSERT
            obj = json.loads(request.POST["schedule"])
            request.POST["pattern"] = schedule_pattern(request.POST["schedule"])
            date_time = datetime.datetime.strptime(obj["start_date"] + " " + obj["start_time"], "%d/%m/%Y %H:%M")
            request.POST["next_run"] = date_time
            request.POST["last_run_result"] = ""
            request.POST["notification_email"] = request.POST.get("notification_email", "")

            request.POST._mutable = False  # make QueryDict immutable again

            if task_id is None or (Util.is_integer(task_id) and int(task_id) in [0, -1]):
                if TaskScheduler.objects.filter(title__iexact=request.POST["title"]).first() is not None:
                    return HttpResponse(json.dumps({"code": 0, "msg": "This task scheduler is already exists"}), content_type="json")
                form = TaskScheduleForm(request.POST)
            else:
                if TaskScheduler.objects.filter(title__iexact=request.POST["title"]).exclude(id=task_id).first() is not None:
                    return HttpResponse(json.dumps({"code": 0, "msg": "This task scheduler is already exists"}), content_type="json")
                action = AuditAction.UPDATE
                task_scheduler = TaskScheduler.objects.filter(id=task_id).first()
                form = TaskScheduleForm(request.POST, instance=task_scheduler)

            if form.is_valid():
                task = form.save()
                log_views.insert("base", "taskscheduler", [task.id], action, request.user.id, base_views.get_client_ip(request), log_views.getLogDesc(task.title, action))
            # get_schedular(True)
            return HttpResponse(json.dumps({"code": 1, "msg": "Data saved.", "id": task.id}), content_type="json")
        else:
            return render(request, "base/task_scheduler.html")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("1")
        return HttpResponse(AppResponse(0, str(e)), content_type="json")


def create_task_scheduler(title, url, schedule, notification_email, user_id, c_ip, code=None):
    try:
        task_scheduler = TaskScheduler.objects.filter(title__iexact=title).first()
        pattern = schedule_pattern(schedule)
        schedule_obj = json.loads(schedule)
        next_run = datetime.datetime.strptime(schedule_obj["start_date"] + " " + schedule_obj["start_time"], "%d/%m/%Y %H:%M")
        action = AuditAction.UPDATE
        if task_scheduler:
            task_scheduler.url = url
            task_scheduler.schedule = schedule
            task_scheduler.pattern = pattern
            task_scheduler.next_run = next_run
            task_scheduler.notification_email = notification_email
            task_scheduler.code = code
        else:
            action = AuditAction.INSERT
            task_scheduler = TaskScheduler.objects.create(
                title=title, code=code, url=url, schedule=schedule, pattern=pattern, next_run=next_run, notification_email=notification_email
            )
        log_views.insert("base", "taskscheduler", [task_scheduler.id], action, user_id, c_ip, log_views.getLogDesc(title, action))
        # get_schedular(True)
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("1")
        return HttpResponse(AppResponse(0, str(e)), content_type="json")


def delete_task_scheduler(request):
    try:
        post_ids = request.POST.get("ids")
        if not post_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")

        ids = [int(x) for x in post_ids.split(",")]
        c_ip = base_views.get_client_ip(request)
        user_id = request.user.id
        task_schedular_delete(ids, user_id, c_ip)
        return HttpResponse(AppResponse.msg(1, "Data removed"), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def task_schedular_delete(ids, user_id, c_ip):
    TaskScheduler.objects.filter(id__in=ids).delete()
    # get_schedular(True)
    log_views.insert("base", "taskscheduler", ids, AuditAction.DELETE, user_id, c_ip, log_views.getLogDesc("", AuditAction.DELETE))


@check_view_permission([{"admin_tools": "task_schedulers"}])
def task_schedulers(request):
    return render(request, "base/task_schedulers.html")


def task_schedulers_search(request):
    try:
        request.POST = Util.get_post_data(request)
        sort_col = Util.get_sort_column(request.POST)
        recordsTotal = TaskScheduler.objects.filter().count()
        task_schedulers = (
            TaskScheduler.objects.filter()
            .values("id", "title", "url", "next_run", "last_run", "last_run_result", "is_active", "pattern", "schedule", "status", "is_running")
            .order_by(sort_col)
        )

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for task_scheduler in task_schedulers:
            response["data"].append(
                {
                    "id": task_scheduler["id"],
                    "title": task_scheduler["title"],
                    "url": task_scheduler["url"],
                    "is_active": task_scheduler["is_active"],
                    "triggers": get_description(task_scheduler["pattern"]) if task_scheduler["pattern"] else "One time",
                    "next_run": datetime.datetime.strptime(str(task_scheduler["next_run"]).split("+")[0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                    if task_scheduler["next_run"] is not None
                    else "",
                    "last_run": datetime.datetime.strptime(str(task_scheduler["last_run"]).split("+")[0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                    if task_scheduler["last_run"] is not None
                    else "",
                    "last_run_result": task_scheduler["last_run_result"].replace("<", "").replace(">", "") if task_scheduler["last_run_result"] is not None else "",
                    "show_run": task_scheduler["url"],
                    "schedule": task_scheduler["schedule"],
                    "status": task_scheduler["status"],
                    "is_running": task_scheduler["is_running"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("1")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def change_status(request):
    is_active = True
    if request.POST["status"] == "true":
        is_active = False
    TaskScheduler.objects.filter(id=request.POST["id"]).update(is_active=is_active)
    # get_schedular(True)
    return HttpResponse(AppResponse.msg(1, "Status changed"), content_type="json")


def insert_system_scheduler(request):
    c_ip = base_views.get_client_ip(request)
    user_id = request.user.id
    insert_defualt_scheduler(c_ip, user_id)
    return HttpResponse(AppResponse.msg(1, "Dave saved."), content_type="json")


def insert_defualt_scheduler(c_ip, user_id):
    try:
        codes = ["LEAVESUM", "PROREORD"]
        task_schedulers = TaskScheduler.objects.filter(code__in=codes).values_list("code", flat=True)
        for code in codes:
            if code in task_schedulers:
                continue

            schedule = {}
            schedule_time_obj = datetime.datetime.utcnow()

            schedule_date = schedule_time_obj.strftime("%d/%m/%Y")
            schedule_time = datetime.datetime.strptime("09:00", "%H:%M")  # To hit scheduler at 9 O'clock daily at anywhere

            partner = Partner.objects.filter(is_hc=True).values("timezone_offset").first()
            schedule_on = schedule_time - datetime.timedelta(minutes=partner["timezone_offset"])
            schedule_at = schedule_on.time()
            start_time = schedule_at.strftime("%H:%M")
            if code == "LEAVESUM":
                title = "Summary leave mail"
                url = "hrm/summary_leave_mail/"
                schedule = {"start_date": schedule_date, "start_time": start_time, "recur_end_date": "", "recur_type": "daily", "recur_day": "1"}

            if code == "PROREORD":
                title = "Products reorder notification"
                url = "inventory/product_reorder_notification/"
                schedule = {"start_date": schedule_date, "start_time": start_time, "recur_end_date": "", "recur_type": "daily", "recur_day": "1"}

            create_task_scheduler(title, url, json.dumps(schedule), "", user_id, c_ip, code)
        return
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
