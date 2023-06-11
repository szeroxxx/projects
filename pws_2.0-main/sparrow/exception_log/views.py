import logging
from datetime import datetime

from base.models import AppResponse
from base.util import Util
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from sparrow.decorators import check_view_permission
from stronghold.decorators import public
from tenant_schemas.utils import schema_context

from exception_log import manager
from exception_log.models import ErrorBase


@check_view_permission([{"admin_tools": "exception_log_dashboard"}])
def dashboard(request):
    query = Q()
    exception_log_data = []
    exception_logs = ErrorBase.objects.filter(query).values("class_name").annotate(class_count=Count("class_name")).order_by("-class_count")
    other_errors = ["", 0, None, "0"]
    all_count = 0
    other_count = 0
    for exception_log in exception_logs:
        all_count += exception_log["class_count"]
        if exception_log["class_name"] in other_errors:
            other_count += exception_log["class_count"]
            continue
        exception_log_data.append(exception_log)
    exception_log_data.append({"class_name": "Others", "class_count": other_count})
    exception_log_data.append({"class_name": "All", "class_count": all_count})

    exception_log_data.sort(key=lambda obj: obj["class_count"], reverse=True)

    # exception_log_data = sorted(exception_logs, key=lambda i: i["class_name"])
    return render(request, "exception_log/exception_log_dashboard.html", {"exception_logs": exception_log_data})


@check_view_permission([{"admin_tools": "exception_log_dashboard"}])
def logs(request, type=None):
    return render(request, "exception_log/exception_logs.html", {"type": type})


def exception_log_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        exception_type = request.POST["exception_type"].replace("%20", " ")

        query = Q()
        if exception_type not in ["All", "Others"]:
            query = Q(class_name__iexact=exception_type)
        elif exception_type == "Others":
            query = Q(class_name__in=["", 0, None, "0"])
        if request.POST.get("class_name") is not None:
            query.add(Q(class_name__icontains=str(request.POST.get("class_name"))), query.connector)
        elif request.POST.get("message") is not None:
            query.add(Q(message__icontains=str(request.POST.get("message"))), query.connector)

        exception_logs = ErrorBase.objects.filter(query).order_by(sort_col)[start : (start + length)]

        recordsTotal = ErrorBase.objects.filter(query).count()

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for exception_log in exception_logs:
            response["data"].append(
                {
                    "id": exception_log.id,
                    "class_name": exception_log.class_name,
                    "message": exception_log.message,
                    "traceback": exception_log.traceback,
                    "created_on": exception_log.created_on.strftime("%d/%m/%Y"),
                }
            )

        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def delete_exception_log(request):
    try:
        exception_log_ids = request.POST.get("ids")
        exception_type = request.POST.get("exception_type")

        if exception_type is not None:
            ErrorBase.objects.filter(class_name=exception_type).delete()

        elif not exception_log_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")

        if exception_log_ids:
            exception_log_ids = [int(x) for x in exception_log_ids.split(",")]
            ErrorBase.objects.filter(id__in=exception_log_ids).delete()

        return HttpResponse(AppResponse.msg(1, "Data removed"), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def exception_log_remove(request, scheduler_key):
    with schema_context("ec"):
        try:
            if scheduler_key == settings.SCHEDULER_KEY:
                long_ago = datetime.now() - relativedelta(months=+3)
                ErrorBase.objects.filter(created_on__lte=long_ago).delete()
            return HttpResponse(AppResponse.msg(1, "Success"), content_type="json")
        except Exception as e:
            manager.create_from_exception(e)
            logging.exception("Something went wrong.")
            return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
