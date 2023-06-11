import ast
import calendar
import datetime
import json
import logging
from decimal import Decimal

from accounts.models import User, UserProfile
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import choices
from base import views as base_views
from base.models import AppResponse
from base.util import Util
from django.conf import settings
from django.db import connection, transaction
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, Template
from exception_log import manager
from mails.views import send_mail
from messaging import notification_view
from partners.forms import HolidayForm
from partners.models import Holiday
from post_office.models import EmailTemplate
from production.forms import LabourForm
# from production.models import Labour, LabourHoliday, WorkWeek, WorkWeekShift, WorkWeekShiftWorker
from sparrow.decorators import check_view_permission
from stronghold.decorators import public

from hrm.forms import LeaveForm, LeavesAllocationForm
from hrm.models import AcademicQualification, LeaveAllocation, LeaveType


@check_view_permission([{"planning": "leave_type"}])
def leave_types(request):
    return render(request, "hrm/leaves_type.html")


def leave_type_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)

        query = Q()

        recordsTotal = LeaveType.objects.filter(query).count()
        records = LeaveType.objects.filter(query).order_by(sort_col)[start : (start + length)].values("id", "name", "days")

        response = {
            "draw": request.POST.get("draw"),
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for data in records:
            response["data"].append({"id": data["id"], "name": data["name"], "days": "%.2f" % data["days"] if data["days"] is not None else ""})
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_leave_type(request):
    leave_type_id = request.POST.get("id")
    leave_type_data = LeaveType.objects.filter(id=int(leave_type_id)).values("name", "days").first()
    leave_type_data["days"] = "%.2f" % leave_type_data["days"] if leave_type_data["days"] is not None else ""
    return HttpResponse(json.dumps({"code": 1, "leave_type": leave_type_data}), content_type="json")


def leave_type_save(request):
    try:
        leave_type_id = request.POST.get("id")
        leave_name = request.POST.get("name")

        if request.method == "POST":
            form = None
            form = LeaveForm(request.POST, request.FILES)
            if leave_type_id == "0":
                if Util.has_perm("can_add_leave_type", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                if LeaveType.objects.filter(name__iexact=leave_name).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Leave type already exist."}), content_type="json")
                form = LeaveForm(request.POST, request.FILES)
            else:
                if Util.has_perm("can_update_leave_type", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                if LeaveType.objects.filter(name__iexact=leave_name).exclude(id=leave_type_id).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Leave type already exist."}), content_type="json")
                leave_type = LeaveType.objects.get(id=int(leave_type_id))
                form = LeaveForm(request.POST, instance=leave_type)
            form.save()
            return HttpResponse(AppResponse.msg(1, "Data saved."))
        else:
            return HttpResponse(AppResponse.msg(0, "Invalid form"), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def leave_type_delete(request):
    try:
        if Util.has_perm("can_delete_leave_type", request.user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        post_ids = request.POST.get("ids")
        ids = [int(x) for x in post_ids.split(",")]
        leave_type_data = LeaveType.objects.filter(id__in=ids)
        leave_type_data.delete()
        return HttpResponse(json.dumps({"code": 1, "msg": "Data removed"}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"planning": "leaves_allocation"}])
def leaves_allocation(request):
    return render(request, "hrm/leaves_allocation.html")


def leaves_allocation_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)
        # options = {"worker": "Employee", "allocate_year": "Year", "leave_type": "Leave type"}
        if request.POST.get("group_by"):
            sort_col = request.POST.get("group_by")
            # if request.POST.get("group_by") not in options:
            #     for key, value in options.items():
            #         if request.POST.get("group_by") == value:
            #             sort_col = key

        query = Q()

        if request.POST.get("worker__name__icontains") is not None:
            query.add(Q(worker__name__icontains=str(request.POST.get("worker__name__icontains").strip())), query.connector)

        if request.POST.get("leave_type__name__icontains") is not None:
            query.add(Q(leave_type__name__icontains=str(request.POST.get("leave_type__name__icontains").strip())), query.connector)

        if request.POST.get("allocate_year") is not None:
            query.add(Q(allocate_year__icontains=int(request.POST.get("allocate_year").strip())), query.connector)

        recordsTotal = LeaveAllocation.objects.filter(query).count()
        records = (
            LeaveAllocation.objects.filter(query)
            .order_by(sort_col)[start : (start + length)]
            .values("id", "worker__name", "allocate_year", "leave_type__name", "days", "description")
        )

        response = {
            "draw": request.POST.get("draw"),
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for data in records:
            response["data"].append(
                {
                    "id": data["id"],
                    "worker": data["worker__name"],
                    "allocate_year": data["allocate_year"],
                    "leave_type": data["leave_type__name"],
                    "days": "%.2f" % data["days"] if data["days"] is not None else "",
                    "description": data["description"],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def leaves_allocation_delete(request):
    try:
        if Util.has_perm("can_delete_leaves_allocation", request.user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        post_ids = request.POST.get("ids")
        ids = [int(x) for x in post_ids.split(",")]
        LeaveAllocation.objects.filter(id__in=ids).delete()
        return HttpResponse(json.dumps({"code": 1, "msg": "Data removed"}), content_type="json")

    except ProtectedError:
        return HttpResponse(AppResponse.msg(0, "Leaveallocation is in use. Action cannot be performed."), content_type="application/json")

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def leaves_allocation_get(request):

    leaves_allocation_id = request.POST.get("id")
    leaves_allocation_data = (
        LeaveAllocation.objects.filter(id=int(leaves_allocation_id))
        .values("worker_id", "worker__name", "leave_type_id", "leave_type__name", "days", "description", "allocate_year")
        .first()
    )
    leaves_allocation_data["days"] = "%.2f" % leaves_allocation_data["days"] if leaves_allocation_data["days"] is not None else ""
    return HttpResponse(json.dumps({"code": 1, "leaves_allocation": leaves_allocation_data}), content_type="json")


def leaves_allocation_save(request):
    try:
        leaves_allocation_id = int(request.POST.get("id"))
        c_ip = base_views.get_client_ip(request)
        labourholiday = LabourHoliday.objects.filter(leave_allocation_id=leaves_allocation_id).first()
        leaves_allocation_data = LeaveAllocation.objects.filter(id=int(leaves_allocation_id)).first()
        if request.method == "POST":
            form = None
            action = AuditAction.UPDATE
            form = LeavesAllocationForm(request.POST, request.FILES)
            if leaves_allocation_id == 0:
                if Util.has_perm("can_add_leaves_allocation", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                form = LeavesAllocationForm(request.POST, request.FILES)
                action = AuditAction.INSERT
            else:
                if Util.has_perm("can_update_leaves_allocation", request.user) is False:
                    return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                if labourholiday is not None:
                    return HttpResponse(
                        AppResponse.msg(
                            0, "%s leave is already applied for %s. You cannot modify leave type." % (leaves_allocation_data.leave_type.name, labourholiday.worker.name)
                        ),
                        content_type="json",
                    )
                else:
                    leaves_allocation = LeaveAllocation.objects.get(id=int(leaves_allocation_id))
                    form = LeavesAllocationForm(request.POST, instance=leaves_allocation)
            leaves_allocation = form.save()
            history_msg = (
                "<b>"
                + leaves_allocation.leave_type.name
                + "</b> leave allocated to <b>"
                + leaves_allocation.worker.name
                + "</b> for <b>"
                + str(leaves_allocation.days)
                + "</b> day(s)."
            )
            log_views.insert("hrm", "leaveallocation", [leaves_allocation.id], action, request.user.id, c_ip, history_msg)
            return HttpResponse(AppResponse.msg(1, "Data saved."))
        else:
            leaves_allocation_data = (
                LeaveAllocation.objects.filter(id=int(leaves_allocation_id)).values("worker_id", "worker__name", "leave_type_id", "leave_type__name", "days", "description").first()
            )
            return HttpResponse(json.dumps({"code": 1, "leaves_allocation": leaves_allocation_data}), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_leave_days(request):
    try:

        leave_type_id = request.POST.get("leave_type")
        leave_type = LeaveType.objects.filter(id=leave_type_id).values("days").first()
        days = "%.2f" % leave_type["days"] if leave_type["days"] is not None else ""
        return HttpResponse(json.dumps({"code": 1, "days": days}), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_leave_allocation(request):
    try:
        leave_allocation_id = request.POST.get("leave_allocation_id")
        worker_id = request.POST.get("worker_id")
        worker = None
        if worker_id is None:
            user_id = request.user.id
            worker = Labour.objects.filter(user_id=user_id).values("id").first()
            worker_id = worker["id"]

        leave_type_id = LeaveAllocation.objects.filter(id=int(leave_allocation_id)).first().leave_type_id
        leave_type = LeaveType.objects.filter(id=leave_type_id).first()

        if worker_id is not None and leave_type is not None:
            allocated_data = get_allolcated_leaves(worker_id, leave_type_id)
            remaining_leave = "%.2f" % allocated_data["remaining_leave"]
            allocated_day = "%.2f" % allocated_data["allocated_day"]

            return HttpResponse(json.dumps({"code": 1, "remaining_leave": remaining_leave, "allocated_day": allocated_day}), content_type="json")
        else:
            return HttpResponse(json.dumps({"code": 0}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_allolcated_leaves(worker_id, leave_type_id):
    try:
        data = {"allocated_day": 0, "total_leave": 0, "remaining_leave": 0}

        if worker_id is None:
            return data

        query = Q()
        query_allocate = Q()
        if leave_type_id is not None:
            query.add(Q(leave_allocation__leave_type_id=leave_type_id), query.connector)
            query_allocate.add(Q(leave_type_id=leave_type_id), query_allocate.connector)

        query.add(Q(worker_id=worker_id), query.connector)
        query.add(Q(leave_allocation__expire=False), query.connector)
        query_allocate.add(Q(worker_id=worker_id), query_allocate.connector)

        allocated_day = 0
        total_leave = 0
        next_year_allocated_day = 0

        current_year = datetime.datetime.now().year
        allocations = LeaveAllocation.objects.filter(query_allocate, expire=False, allocate_year=current_year).values("days").aggregate(Sum("days"))

        if allocations["days__sum"] is not None:
            allocated_day = allocations["days__sum"]

        next_year_allocations = LeaveAllocation.objects.filter(worker_id=worker_id, expire=False, allocate_year__gt=current_year).values("days").aggregate(Sum("days"))

        if next_year_allocations["days__sum"] is not None:
            next_year_allocated_day = next_year_allocations["days__sum"]

        query.add(Q(status__in=["approved", "pending"]), query.connector)
        leave_total = LabourHoliday.objects.filter(query, leave_allocation__allocate_year=current_year).values("days").aggregate(Sum("days"))
        if leave_total["days__sum"] is not None:
            total_leave = leave_total["days__sum"]

        taken_leave_from_days = (
            LabourHoliday.objects.exclude(leave_allocation__leave_type__days=None)
            .filter(query, leave_allocation__allocate_year=current_year)
            .values("days")
            .aggregate(Sum("days"))["days__sum"]
        )

        taken_leave_from_next_year_day = (
            LabourHoliday.objects.exclude(leave_allocation__leave_type__days=None)
            .filter(query, leave_allocation__allocate_year__gt=current_year)
            .values("days")
            .aggregate(Sum("days"))["days__sum"]
        )

        taken_leave_from_days = taken_leave_from_days if taken_leave_from_days is not None else 0

        remaining_leave = allocated_day - total_leave

        taken_leave_from_next_year_day = taken_leave_from_next_year_day if taken_leave_from_next_year_day is not None else 0

        data = {
            "allocated_day": allocated_day,
            "next_year_allocated_day": next_year_allocated_day,
            "total_leave": total_leave,
            "remaining_leave": 0 if remaining_leave < 0 else remaining_leave,
        }
        return data
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"planning": "my_leaves"}])
def leaves_view(request):
    worker = Labour.objects.filter(user_id=request.user.id).values("id").first()
    worker_id = worker["id"] if worker is not None else None
    allocated_data = get_allolcated_leaves(worker_id, None)

    if worker is None:
        return HttpResponse('<h4 style="color:red;text-align:center;">Logged in user is not linked to any Employee. Contact to administrator.</h4>')

    return render(request, "hrm/my_leaves.html", context=allocated_data)


def leaves_search(request, search=None):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))
        sort_col = Util.get_sort_column(request.POST)
        timezone = request.session["timezone"]
        query = Q()
        show_main_grid = True
        response = {
            "draw": request.POST.get("draw"),
            "recordsTotal": 0,  # recordsTotal
            "recordsFiltered": 0,  # recordsTotal
            "data": [],
        }
        if search == "leaves_report":
            if request.POST["worker_id"] != "":
                query.add(Q(worker_id=request.POST["worker_id"]), query.connector)
            query.add(~Q(status="cancel"), query.connector)
            if request.POST["start_date__date"] == "" and request.POST["end_date__date"] == "":
                show_main_grid = False

        if search == "my_leaves":
            worker = Labour.objects.filter(user_id=request.user.id).values("id").first()
            query.add(Q(worker_id=worker["id"]), query.connector)

        if request.POST.get("worker__name__icontains") is not None:
            query.add(Q(worker__name__icontains=str(request.POST.get("worker__name__icontains").strip())), query.connector)

        if request.POST.get("start_date__date") and request.POST.get("end_date__date") and search == "leaves_report":
            user_start_date = datetime.datetime.strptime(str(request.POST["start_date__date"]), "%d/%m/%Y").strftime("%Y-%m-%d")
            user_end_date = datetime.datetime.strptime(str(request.POST["end_date__date"]), "%d/%m/%Y").strftime("%Y-%m-%d")
            query.add(Q(start_date__date__lte=user_end_date), query.connector)
            query.add(Q(end_date__date__gte=user_start_date), query.connector)
        else:
            if request.POST.get("start_date__date"):
                query.add(
                    Q(
                        start_date__range=[
                            Util.get_utc_datetime(request.POST["start_date__date_from_date"].strip(), True, timezone),
                            Util.get_utc_datetime(request.POST["start_date__date_to_date"].strip(), True, timezone),
                        ]
                    ),
                    query.connector,
                )
            if request.POST.get("end_date__date"):
                query.add(
                    Q(
                        end_date__range=[
                            Util.get_utc_datetime(request.POST["end_date__date_from_date"].strip(), True, timezone),
                            Util.get_utc_datetime(request.POST["end_date__date_to_date"].strip(), True, timezone),
                        ]
                    ),
                    query.connector,
                )

        if request.POST.get("created_on__date") is not None:
            query.add(
                Q(
                    created_on__range=[
                        Util.get_utc_datetime(request.POST["created_on__date_from_date"].strip(), True, timezone),
                        Util.get_utc_datetime(request.POST["created_on__date_to_date"].strip(), True, timezone),
                    ]
                ),
                query.connector,
            )

        if request.POST.get("status__icontains") is not None:
            query.add(Q(status__icontains=str(request.POST.get("status__icontains").strip())), query.connector)

        if request.POST.get("leave_type__name__icontains") is not None:
            query.add(Q(leave_allocation__leave_type__name__icontains=str(request.POST.get("leave_type__name__icontains").strip())), query.connector)

        recordsTotal = LabourHoliday.objects.filter(query).count()
        records = (
            LabourHoliday.objects.filter(query)
            .order_by(sort_col)[start : (start + length)]
            .values("id", "worker__name", "start_date", "end_date", "days", "leave_allocation__leave_type__name", "description", "status", "created_on", "created_by")
        )

        if show_main_grid:
            response["recordsTotal"] = recordsTotal
            response["recordsFiltered"] = recordsTotal
            for data in records:
                start_date = Util.get_local_time(data["start_date"], False)
                end_date = Util.get_local_time(data["end_date"], False)
                created_on = Util.get_local_time(data["created_on"], True)
                response["data"].append(
                    {
                        "id": data["id"],
                        "worker": data["worker__name"],
                        "start_date": start_date,
                        "end_date": end_date,
                        "days": "%.2f" % data["days"] if data["days"] is not None else "",
                        "description": data["description"],
                        "leave_allocation__leave_type__name": data["leave_allocation__leave_type__name"],
                        "created_on": created_on,
                        "status": dict(choices.leave_status)[data["status"]],
                    }
                )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except ValueError:
        return HttpResponse(AppResponse.msg(0, "Incorrect date format"), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def my_leaves_save(request):
    try:
        if request.method == "POST":
            user_id = request.user.id
            leave_allocation_id = request.POST["leave_allocation"]
            worker_id = request.POST.get("worker", None)
            description = request.POST["description"]
            leave_frags = json.loads(request.POST["leaveFrags"])
            c_ip = base_views.get_client_ip(request)
            is_email_send = False

            if worker_id is None:
                worker = Labour.objects.filter(user_id=user_id).values("id").first()
                if worker:
                    worker_id = worker["id"]
                    is_email_send = True

                if worker_id is None:
                    return HttpResponse(json.dumps({"code": 0, "msg": "Employee is not linked to the user."}), content_type="json")

            days = 0
            for leave in leave_frags:
                days += leave["days"]

            leave_type_data = LeaveAllocation.objects.filter(id=int(leave_allocation_id)).first()
            allocated_data = get_allolcated_leaves(worker_id, leave_type_data.leave_type_id)

            if str(leave_type_data.allocate_year) != leave_frags[0]["start_date"].split("/")[-1] or str(leave_type_data.allocate_year) != leave_frags[0]["end_date"].split("/")[-1]:
                return HttpResponse(json.dumps({"code": 0, "msg": "You cannot apply different years leave into single leave application."}), content_type="json")

            new_remaining = allocated_data["remaining_leave"] - Decimal(days)
            if allocated_data["allocated_day"] > 0:
                if allocated_data["remaining_leave"] == 0 or new_remaining < 0:
                    return HttpResponse(json.dumps({"code": 0, "msg": "You don't have sufficient leave to apply."}), content_type="json")

            for leave in leave_frags:
                leave_from = datetime.datetime.strptime(str(leave["start_date"]), "%d/%m/%Y")
                leave_to = datetime.datetime.strptime(str(leave["end_date"]), "%d/%m/%Y")
                days = leave["days"]
                labourholiday = LabourHoliday.objects.create(
                    worker_id=worker_id,
                    start_date=leave_from,
                    end_date=leave_to,
                    leave_allocation_id=leave_allocation_id,
                    days=days,
                    description=description,
                    created_by_id=user_id,
                )

                action = AuditAction.INSERT
                history_msg = "Leave added from <b>" + leave["start_date"] + "</b> to <b>" + leave["end_date"] + "</b> for <b>" + str(days) + "</b> day(s)."
                log_views.insert("production", "labourholiday", [labourholiday.id], action, request.user.id, c_ip, history_msg)

                emails = []
                email_for_approval = Util.get_sys_paramter("HRM_LEAVE_REQUEST_MAIL").para_value
                if is_email_send and email_for_approval != "" and email_for_approval is not None:
                    emails = [x.strip() for x in email_for_approval.split(",")]
                    template = EmailTemplate.objects.filter(name__iexact="leave_request").first()
                    mail_context = Context(
                        {
                            "user_name": request.session.get("display_name"),
                            "Reason": description,
                            "leave_from": leave["start_date"],
                            "leave_to": leave["end_date"],
                            "days": days,
                            "created_on": Util.get_local_time(datetime.datetime.utcnow()),
                            "from_date": str(datetime.datetime.strptime(leave["start_date"], "%d/%m/%Y").strftime("%b %d, %Y")),
                        }
                    )
                    template_content = Template(template.html_content).render(mail_context)
                    template_subject = Template(template.subject).render(mail_context)
                    send_mail(False, "public", emails, template_subject, template_content, [])

            gen_allocated_data = get_allolcated_leaves(worker_id, None)
            allocated_day = str(gen_allocated_data["allocated_day"])
            remaining_leave = str(gen_allocated_data["remaining_leave"])
            total_leave = str(gen_allocated_data["total_leave"])
            return HttpResponse(
                json.dumps({"code": 1, "msg": "Leave applied.", "total_leave": total_leave, "allocated_day": allocated_day, "remaining_leave": remaining_leave}),
                content_type="json",
            )
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def hrm_leave_email(start_date, end_date, is_email_send, days, description, user_name):
    try:
        emails = []
        email_for_approval = Util.get_sys_paramter("HRM_LEAVE_REQUEST_MAIL").para_value
        if is_email_send and email_for_approval != "" and email_for_approval is not None:
            emails = [x.strip() for x in email_for_approval.split(",")]
            template = EmailTemplate.objects.filter(name__iexact="leave_request").first()
            mail_context = Context(
                {
                    "user_name": user_name,
                    "Reason": description,
                    "leave_from": start_date,
                    "leave_to": end_date,
                    "days": days,
                    "created_on": Util.get_local_time(datetime.datetime.utcnow()),
                    "from_date": str(datetime.datetime.strptime(start_date, "%d/%m/%Y").strftime("%b %d, %Y")),
                }
            )
            template_content = Template(template.html_content).render(mail_context)
            template_subject = Template(template.subject).render(mail_context)
            send_mail(False, "public", emails, template_subject, template_content, [])

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def leave_cancel(request):
    try:
        cancel_ids = request.POST.get("ids")
        ids = [int(x) for x in cancel_ids.split(",")]
        c_ip = base_views.get_client_ip(request)
        action = AuditAction.DELETE
        leave_count = LabourHoliday.objects.filter(id__in=ids, status__in=["approved", "rejected"]).count()
        if leave_count > 0:
            return HttpResponse(json.dumps({"code": 0, "msg": "You cannot cancel approved or rejected leave."}), content_type="json")
        log_views.insert("production", "labourholiday", ids, action, request.user.id, c_ip, "Leave cancelled.")
        LabourHoliday.objects.filter(id__in=ids).update(status="cancel")
        return HttpResponse(json.dumps({"code": 1, "msg": "Leave cancelled"}), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_all_leaves_calendar(request):
    try:
        currentMonth = int(request.POST.get("currentMonth"))
        currentYear = int(request.POST.get("currentYear"))
        user_id = request.user.id
        query = Q()
        my_leave_id = request.POST.get("my_leave_id")
        if my_leave_id == "1":
            worker = Labour.objects.filter(user_id=user_id).values("id").first()
            query.add(Q(worker_id=worker["id"]), query.connector)

        query.add(Q(status__in=["pending", "rejected", "approved"], end_date__month=currentMonth, end_date__year=currentYear), query.connector)

        response = {"data": []}
        labour_holidays = LabourHoliday.objects.filter(query).values("id", "worker__name", "worker__user_id", "start_date", "status", "end_date", "description")
        public_holidays = Holiday.objects.filter(holiday_month=currentMonth).values("id", "name", "holiday_day", "holiday_month", "holiday_year")
        user_ids = []
        for holiday in labour_holidays:
            if holiday["worker__user_id"]:
                user_ids.append(holiday["worker__user_id"])

        users = UserProfile.objects.filter(user_id__in=user_ids).values("user_id", "profile_image")
        imageurl = {}
        for user in users:
            imageurl[user["user_id"]] = user["profile_image"]

        for public_holiday in public_holidays:
            if public_holiday["holiday_year"] is not None and public_holiday["holiday_year"] != "":
                holiday_year = public_holiday["holiday_year"]
            else:
                holiday_year = datetime.datetime.now().year

            public_holiday_date = str(holiday_year) + "-" + str(public_holiday["holiday_month"]) + "-" + str(public_holiday["holiday_day"])
            public_holiday_on = datetime.datetime.strptime(public_holiday_date, "%Y-%m-%d").strftime("%Y-%m-%d")

            response["data"].append(
                {"id": public_holiday["id"], "title": "Holiday" + " - " + public_holiday["name"], "start": public_holiday_on, "status": None, "imageurl": "holiday"}
            )

        for labour_holiday in labour_holidays:
            response["data"].append(
                {
                    "id": labour_holiday["id"],
                    "title": "" + labour_holiday["worker__name"],
                    "status": labour_holiday["status"],
                    "description": labour_holiday["description"],
                    "imageurl": Util.get_resource_url("profile", str(imageurl[labour_holiday["worker__user_id"]])) if labour_holiday["worker__user_id"] in imageurl else "",
                    "start": Util.get_local_time(labour_holiday["start_date"], True, "%Y-%m-%dT12:00"),
                    "end": Util.get_local_time(labour_holiday["end_date"], True, "%Y-%m-%dT12:00"),
                }
            )

        day_lists = {"mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4, "sa": 5, "su": 6}

        weekends = []
        workdays = Util.get_sys_paramter("workdays").para_value

        sunday_holiday = []
        sat_sun_holiday = []
        weeks = workdays.split(";")

        for i in range(len(weeks)):
            if i == 0:
                first_weekdays_list = weeks[i].split(",")
                first_weekdays_list = [x.lower() for x in first_weekdays_list]
            else:
                sec_weekdays_list = weeks[i].split(",")
                sec_weekdays_list = [x.lower() for x in sec_weekdays_list]

        for day in day_lists:
            if day not in first_weekdays_list:
                sat_sun_holiday.append(day_lists[day])
            if day not in sec_weekdays_list:
                sunday_holiday.append(day_lists[day])

        cal = calendar.Calendar()
        day_weeks_list = cal.monthdays2calendar(currentYear, currentMonth)
        count = 0
        sat_count = 0

        is_alt_sat = False
        for day_weeks in day_weeks_list:
            count += 1
            for day_week in day_weeks:
                if is_alt_sat is False and sat_count < 2:
                    if day_week[1] in sat_sun_holiday:
                        if day_week[0] != 0:
                            weekends.append(day_week[0])
                            if day_week[1] == 5 and sat_count < 2:
                                is_alt_sat = True
                                sat_count += 1
                                weekends.append(day_week[0] + 1)
                                break
                else:
                    if day_week[1] in sunday_holiday:
                        if day_week[0] != 0:
                            is_alt_sat = False
                            weekends.append(day_week[0])
        for day in weekends:
            if day:
                common_holiday_on = datetime.datetime(currentYear, currentMonth, day)
                common_date = str(common_holiday_on.date())
                commmon_holidays_on = str(common_holiday_on)
                response["data"].append({"start": commmon_holidays_on, "weekends": 1, "common_date": common_date})

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def leave_approve(request):
    if Util.has_perm("can_approve_all_leaves", request.user) is False:
        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
    approve_ids = request.POST.get("ids")
    ids = [int(x) for x in approve_ids.split(",")]
    action = AuditAction.UPDATE
    c_ip = base_views.get_client_ip(request)
    LabourHoliday.objects.filter(id__in=ids).update(status="approved")
    for id in ids:
        labour_holiday = LabourHoliday.objects.filter(id=id).values("worker__user__id", "start_date", "end_date", "description", "days", "created_on").first()
        if labour_holiday["worker__user__id"] is not None:
            send_user_notification(request, labour_holiday, "hrm", "labourholiday", "approved", id)

    log_views.insert("production", "labourholiday", ids, action, request.user.id, c_ip, "Leave approved.")
    return HttpResponse(json.dumps({"code": 1, "msg": "Leave approved"}), content_type="json")


def leave_reject(request):
    if Util.has_perm("can_reject_all_leaves", request.user) is False:
        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
    leave_reject_ids = request.POST.get("ids")
    ids = [int(x) for x in leave_reject_ids.split(",")]
    action = AuditAction.UPDATE
    c_ip = base_views.get_client_ip(request)
    LabourHoliday.objects.filter(id__in=ids).update(status="rejected")
    for id in ids:
        labour_holiday = LabourHoliday.objects.filter(id=id).values("worker__user__id", "start_date", "end_date", "description", "days", "created_on").first()
        if labour_holiday["worker__user__id"] is not None:
            send_user_notification(request, labour_holiday, "hrm", "labourholiday", "rejected", id)
    log_views.insert("production", "labourholiday", ids, action, request.user.id, c_ip, "Leave rejected.")
    return HttpResponse(json.dumps({"code": 1, "msg": "Leave rejected"}), content_type="json")


def send_user_notification(request, labour_holiday, group, model, action, entity_id):
    notification_view.user_notification(
        request,
        labour_holiday["worker__user__id"],
        group,
        model,
        action,
        entity_id,
        Reason=labour_holiday["description"],
        leave_from=labour_holiday["start_date"],
        leave_to=labour_holiday["end_date"],
        days=labour_holiday["days"],
        created_on=Util.get_local_time(labour_holiday["created_on"]),
        created_on_subject=Util.get_local_time(datetime.datetime.utcnow(), True, "%b %d, %Y, %H:%M"),
        leave_to_str=str(datetime.datetime.strptime(str(labour_holiday["start_date"]).split("+")[0], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y, %H:%M")),
        leave_from_str=str(datetime.datetime.strptime(str(labour_holiday["end_date"]).split("+")[0], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y, %H:%M")),
    )


def all_leaves_delete(request):
    try:
        if Util.has_perm("can_delete_all_leaves", request.user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        post_ids = request.POST.get("ids")
        ids = [int(x) for x in post_ids.split(",")]
        leave_delete = LabourHoliday.objects.filter(id__in=ids)
        leave_delete.delete()
        return HttpResponse(json.dumps({"code": 1, "msg": "Data removed"}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"planning": "all_leaves"}])
def all_leaves(request):
    return render(request, "hrm/all_leaves.html")


@check_view_permission([{"Shift planning": "shifts"}])
def employee(request, worker_id=None):
    try:
        with transaction.atomic():
            qualification_datas = ""

            # qualification_data = AcademicQualification.objects.filter
            if request.method == "POST":
                request.POST._mutable = True
                request.POST["description"] = request.POST["order_description"]
                form = None
                action = AuditAction.UPDATE
                id_fv = request.POST.get("id")

                name = str(request.POST.get("name")).strip()
                c_ip = base_views.get_client_ip(request)
                worker_user_id = request.POST.get("user")

                is_changed_shift = True if request.POST.get("is_changed_shift") == "true" else False
                user_id = request.user.id
                user = User.objects.get(id=user_id)
                if id_fv is None or (Util.is_integer(id_fv) and int(id_fv) in [0, -1]):
                    if Util.has_perm("can_add_workers", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    if name != "" and Labour.objects.filter(name__iexact=name).count() > 0:
                        return HttpResponse(AppResponse.get({"code": 0, "msg": "Worker already exist."}), content_type="json")
                    action = AuditAction.INSERT
                    form = LabourForm(request.POST)
                else:
                    if Util.has_perm("can_update_workers", user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    worker = Labour.objects.get(id=int(id_fv))
                    form = LabourForm(request.POST, instance=worker)
                if request.POST["date_of_birth"] is not None and request.POST["date_of_birth"] != "":
                    request.POST["date_of_birth"] = datetime.datetime.combine(datetime.datetime.strptime(str(request.POST["date_of_birth"]), "%d/%m/%Y").date(), datetime.time.min)
                if request.POST["date_of_join"] is not None and request.POST["date_of_join"] != "":
                    request.POST["date_of_join"] = datetime.datetime.combine(datetime.datetime.strptime(str(request.POST["date_of_join"]), "%d/%m/%Y").date(), datetime.time.min)
                if request.POST["agree_start_date"] is not None and request.POST["agree_start_date"] != "":
                    request.POST["agree_start_date"] = datetime.datetime.combine(
                        datetime.datetime.strptime(str(request.POST["agree_start_date"]), "%d/%m/%Y").date(), datetime.time.min
                    )
                if request.POST["agree_end_date"] is not None and request.POST["agree_end_date"] != "":
                    request.POST["agree_end_date"] = datetime.datetime.combine(
                        datetime.datetime.strptime(str(request.POST["agree_end_date"]), "%d/%m/%Y").date(), datetime.time.min
                    )
                if request.POST["date_of_sep"] is not None and request.POST["date_of_sep"] != "":
                    request.POST["date_of_sep"] = datetime.datetime.combine(datetime.datetime.strptime(str(request.POST["date_of_sep"]), "%d/%m/%Y").date(), datetime.time.min)
                request.POST._mutable = False
                if form.is_valid():
                    worker = form.save(commit=False)
                    if action == AuditAction.INSERT:
                        worker.created_by_id = user_id
                    elif is_changed_shift:
                        new_shift_code = worker.shift.code if worker.shift is not None else None
                        shift_workers = WorkWeekShiftWorker.objects.filter(
                            worker_id=worker.id, workweekshift__workweek__weekdate__gte=datetime.datetime.utcnow() + datetime.timedelta(days=-1)
                        )
                        if new_shift_code is not None:
                            for shift_worker in shift_workers:
                                workweek_shift = WorkWeekShift.objects.filter(code=new_shift_code, workweek_id=shift_worker.workweekshift.workweek_id).first()
                                shift_worker.workweekshift_id = workweek_shift.id
                                shift_worker.save()
                        else:
                            shift_workers.delete()

                    worker.user_id = worker_user_id
                    worker = form.save()
                    log_views.insert("production", "labour", [worker.id], action, request.user.id, c_ip, log_views.getLogDesc(worker.name, action))
                    if action == AuditAction.INSERT:
                        return HttpResponse(json.dumps({"code": 1, "msg": "Data saved", "update": False, "id": worker.id, "name": worker.name}), content_type="json")
                    else:
                        return HttpResponse(json.dumps({"code": 1, "msg": "Data saved.", "update": True, "id": worker.id, "name": worker.name}), content_type="json")
                else:
                    return HttpResponse(AppResponse.msg(0, form.errors), content_type="json")
            else:
                worker_data = Labour.objects.filter(id=worker_id).first()
                results = Labour.objects.filter(pk=worker_id)
                qualification_id = []
                for staff in results:
                    qualification_datas = staff.qualification.all()

                for qualification_data in qualification_datas:
                    qualification_id.append(qualification_data.id)

                qualification_ids = ",".join(str(x) for x in qualification_id)
                return render(request, "production/worker.html", {"worker_data": worker_data, "qualification_ids": qualification_ids})
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"planning": "holidays"}])
def holidays(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    perms = ["can_export_holidays", "can_import_holidays"]
    permissions = Util.get_permission_role(user, perms)
    context = {}
    context["permissions"] = json.dumps(permissions)
    return render(request, "hrm/holidays.html", context)


def holiday(request, holiday_id=None):
    try:
        with transaction.atomic():
            if request.method == "POST":
                form = None
                action = AuditAction.UPDATE
                holiday_id = request.POST.get("id")
                holiday_name_count = Holiday.objects.filter(name__icontains=request.POST["name"], holiday_year=int(request.POST["holiday_year"])).exclude(id=holiday_id).count()
                if holiday_name_count > 0:
                    return HttpResponse(json.dumps({"code": 0, "msg": "Cannot add multiple holiday with the same name "}), content_type="json")
                if holiday_id == "0":
                    if Util.has_perm("can_add_holidays", request.user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    action = AuditAction.INSERT
                    form = HolidayForm(request.POST)
                else:
                    if Util.has_perm("can_update_holidays", request.user) is False:
                        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
                    holiday = Holiday.objects.get(id=int(holiday_id))
                    form = HolidayForm(request.POST, instance=holiday)
                if form.is_valid():
                    holiday = form.save(commit=False)
                    holiday = form.save()
                    if action == AuditAction.INSERT:
                        return HttpResponse(json.dumps({"code": 1, "msg": "Data saved"}), content_type="json")
                    else:
                        return HttpResponse(AppResponse.msg(1, "Data saved"), content_type="json")
                else:
                    return HttpResponse(AppResponse.msg(0, form.errors), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_holiday(request):
    try:
        holiday_type_id = request.POST.get("id")
        holiday_type_data = Holiday.objects.filter(id=int(holiday_type_id)).values("name", "holiday_day", "holiday_month", "holiday_year").first()

        if holiday_type_data["holiday_year"] is not None and holiday_type_data["holiday_year"] != "":
            holiday_year = holiday_type_data["holiday_year"]
            reoccurring = False
        else:
            holiday_year = datetime.datetime.now().year
            reoccurring = True
        holiday_on = Util.get_local_time(
            datetime.datetime.strptime(str(holiday_type_data["holiday_day"]) + "-" + str(holiday_type_data["holiday_month"]) + "-" + str(holiday_year), "%d-%m-%Y"), False
        )
        return HttpResponse(json.dumps({"code": 1, "holiday_on": holiday_on, "holiday_type_data": holiday_type_data, "reoccurring": reoccurring}))
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def check_working_day(request):
    try:
        holiday_date = request.POST["holiday_date"]
        if WorkWeek.objects.filter(weekdate__date=holiday_date).count() not in [0, -1]:
            return HttpResponse(AppResponse.msg(1, "Matched."), content_type="json")
        return HttpResponse(AppResponse.msg(2, "No-matched."), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def holidays_del(request):
    try:
        with transaction.atomic():
            post_ids = request.POST.get("ids")
            user_id = request.user.id
            user = User.objects.get(id=user_id)

            if Util.has_perm("can_delete_holidays", user) is False:
                return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")

            if not post_ids:
                return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")
            ids = [int(x) for x in post_ids.split(",")]

            Holiday.objects.filter(id__in=ids).delete()

            return HttpResponse(AppResponse.msg(1, "Data removed"), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def holidays_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        query = Q()
        if request.POST.get("name__icontains") is not None:
            query.add(Q(name__icontains=str(request.POST.get("name__icontains"))), query.connector)

        recordsTotal = Holiday.objects.filter(query).count()
        holidays = Holiday.objects.filter(query).order_by(sort_col)[start : (start + length)]

        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for holiday in holidays:
            if holiday.holiday_year is not None and holiday.holiday_year != "":
                holiday_year = holiday.holiday_year

            else:
                holiday_year = datetime.datetime.now().year
            response["data"].append(
                {"id": holiday.id, "name": holiday.name, "holiday_on": datetime.date(holiday_year, holiday.holiday_month, holiday.holiday_day).strftime("%A, %B %d, %Y")}
            )

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def import_holiday(request):
    try:
        if request.method == "POST":
            with transaction.atomic():
                if not request.POST.get("data", False):
                    return HttpResponse(AppResponse.msg(0, "Import data is not available."), content_type="json")
                data = ast.literal_eval(request.POST["data"])
                if len(data) == 0:
                    return HttpResponse(AppResponse.msg(0, "Import data is not available."), content_type="json")
                holiday_names = [x["name"].strip() for x in data]
                existing_holidays = Holiday.objects.filter(name__in=holiday_names).values_list("name", flat=True)
                if len(existing_holidays) > 0:
                    error_message = "Following hollidays are already present,cannot import again : "
                    for holiday in existing_holidays:
                        error_message = error_message + holiday + ", "
                    return HttpResponse(AppResponse.msg(0, error_message[:-2]), content_type="json")

                for row in data:
                    if int(row["holiday_day"].strip()) > 31:
                        return HttpResponse(AppResponse.msg(0, "Date cannot be more than 31."), content_type="json")
                    if int(row["holiday_month"].strip()) > 12:
                        return HttpResponse(AppResponse.msg(0, "Month cannot be more than 12."), content_type="json")
                    if "holiday_year" in row and len(row["holiday_year"]) > 4:
                        return HttpResponse(AppResponse.msg(0, "Year cannot be in 5 digit."), content_type="json")

                    Holiday.objects.create(
                        name=row["name"].strip(),
                        holiday_day=row["holiday_day"].strip(),
                        holiday_month=row["holiday_month"].strip(),
                        holiday_year=row["holiday_year"] if "holiday_year" in row and row["holiday_year"] != "" else None,
                    )

            return HttpResponse(AppResponse.msg(1, "Holidays imported"), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, "Make sure your file structure is same as Template. Internal error: " + str(e)), content_type="json")


def leaves_report(request):
    return render(request, "hrm/leaves_report.html")


def leaves_export(request):
    try:
        worker_id = request.GET.get("worker_id", "")
        from_date = request.GET.get("from", "")
        to_date = request.GET.get("to", "")
        timezone = request.session["timezone"]
        query = Q()
        query.add(~Q(status="cancel"), query.connector)
        if worker_id != "":
            query.add(Q(worker_id=worker_id), query.connector)
        if from_date and to_date:
            query.add(Q(start_date__date__gte=Util.get_utc_datetime(from_date, False, timezone)), query.connector)
            query.add(Q(end_date__date__lte=Util.get_utc_datetime(to_date, False, timezone)), query.connector)

        leaves = LabourHoliday.objects.filter(query).values(
            "worker__name", "start_date", "end_date", "days", "leave_allocation__leave_type__name", "description", "status", "created_on"
        )

        headers = [
            {"title": "Employee"},
            {"title": "Leave from", "type": "date"},
            {"title": "Leave to", "type": "date"},
            {"title": "Days"},
            {"title": "Leave type"},
            {"title": "Reason"},
            {"title": "Status"},
            {"title": "Applied on", "type": "date"},
        ]

        return Util.export_to_xls(headers, leaves, "leave_report.xls")

    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def export_holiday(request):
    try:
        holiday_ids = request.POST.get("ids")
        ids = [int(x) for x in holiday_ids.split(",")]
        if holiday_ids != "0":
            holidays = Holiday.objects.filter(id__in=ids).values("name", "holiday_day", "holiday_month", "holiday_year")
        else:
            holidays = Holiday.objects.values("name", "holiday_day", "holiday_month", "holiday_year")

        headers = [{"title": "Name"}, {"title": "Date", "type": "date"}, {"title": "Month"}, {"title": "Year"}]

        return Util.export_to_xls(headers, holidays, "Holidays.xls")

    except Exception as e:
        logging.exception("Something went wrong!")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@public
def summary_leave_mail(request, scheduler_key=""):
    try:
        if scheduler_key == settings.SCHEDULER_KEY:
            tommorow_date = datetime.datetime.utcnow().date()
            tommorow_date = datetime.datetime.combine(tommorow_date, datetime.time.min)

            # Settle time difference for leave start as it is converted to local to utc when leave added
            date_from = Util.get_utc_datetime(tommorow_date) + datetime.timedelta(days=1)
            date_to = date_from + datetime.timedelta(days=1)

            query = Q()
            query.add(Q(start_date__gte=date_from), query.connector)
            query.add(Q(start_date__lt=date_to), query.connector)
            query.add(Q(status__in=["pending", "approved"]), query.connector)

            labour_holidays = LabourHoliday.objects.filter(query).values("start_date", "id", "end_date", "worker__name", "days")
            labour_count = len(labour_holidays)

            if labour_count > 0:
                employees = []
                for labour_holiday in labour_holidays:
                    employees.append(
                        {
                            "name": labour_holiday["worker__name"],
                            "start_date": Util.get_local_time(labour_holiday["start_date"], True),
                            "end_date": Util.get_local_time(labour_holiday["end_date"], True),
                            "days": labour_holiday["days"],
                        }
                    )
                emails = []
                email_for_approval = Util.get_sys_paramter("HRM_LEAVE_REQUEST_MAIL").para_value
                if email_for_approval is not None and email_for_approval != "":
                    emails = [x.strip() for x in email_for_approval.split(",")]
                    template = EmailTemplate.objects.filter(name__iexact="leave_summary").first()
                    mail_context = Context({"date": Util.get_local_time(date_from, True, "%b %d, %Y"), "number": labour_count, "employees": employees})
                    template_content = Template(template.html_content).render(mail_context)
                    template_subject = Template(template.subject).render(mail_context)
                    send_mail(False, "public", emails, template_subject, template_content, [])
            return HttpResponse(AppResponse.msg(1, "Success"), content_type="json")
        return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
        manager.create_from_text("leaves:" + str(tommorow_date))


@check_view_permission([{"human_resources": "academic_qualification"}])
def qualifications_type(request):
    return render(request, "hrm/qualifications_type.html")


def qualification_type(request, id=None):
    if id is not None or id != 0:
        qualification = AcademicQualification.objects.filter(id=id).first()
    return render(request, "hrm/qualification_type.html", {"qualification": qualification})


def qualification_type_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST.get("start"))
        length = int(request.POST.get("length"))

        query = Q()

        if request.POST.get("qualification__icontains") is not None:
            query.add(Q(name__icontains=str(request.POST.get("qualification__icontains"))), query.connector)

        recordsTotal = AcademicQualification.objects.filter(query).count()
        records = AcademicQualification.objects.filter(query).values("name", "id")[start : (start + length)]

        response = {
            "draw": request.POST.get("draw"),
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for data in records:
            response["data"].append({"qualification": data["name"], "id": data["id"]})
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception("Something went wrong")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_qualification_type(request):
    qualification_type_id = request.POST.get("id")
    qualification_type_data = AcademicQualification.objects.filter(id=int(qualification_type_id)).values("name", "id").first()
    return HttpResponse(json.dumps({"code": 1, "qualification_type": qualification_type_data}), content_type="json")


def qualification_type_save(request):
    try:
        qualification_type_id = request.POST.get("id")
        qualification = request.POST.get("name")

        c_ip = base_views.get_client_ip(request)
        action = AuditAction.UPDATE

        if request.method == "POST":
            if qualification_type_id == "0":
                if AcademicQualification.objects.filter(name__iexact=qualification).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Qualification type already exist."}), content_type="json")
                qualification_type = AcademicQualification.objects.create(name=qualification, created_by_id=request.user.id)
                action = AuditAction.INSERT
                log_views.insert("hrm", "academicqualification", [qualification_type.id], action, request.user.id, c_ip, log_views.getLogDesc(qualification_type.name, action))
            else:
                if AcademicQualification.objects.filter(name__iexact=qualification).exclude(id=qualification_type_id).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Qualification type already exist."}), content_type="json")
                qualification_type = AcademicQualification.objects.get(id=int(qualification_type_id))
                qualification_type.name = qualification
                qualification_type.save()
                log_views.insert("hrm", "academicqualification", [qualification_type.id], action, request.user.id, c_ip, log_views.getLogDesc(qualification_type.name, action))

            return HttpResponse(json.dumps({"code": 1, "msg": "Qualification type saved.", "id": qualification_type.id, "name": qualification_type.name}), content_type="json")

    except Exception as e:
        logging.exception("Something went wrong")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def qualification_type_delete(request):
    try:
        if Util.has_perm("can_delete_leave_type", request.user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        post_ids = request.POST.get("ids")
        ids = [int(x) for x in post_ids.split(",")]
        qualification_type_data = AcademicQualification.objects.filter(id__in=ids)
        qualification_type_data.delete()
        return HttpResponse(json.dumps({"code": 1, "msg": "Record deleted"}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def employee_leaves_search(request, worker_id=None):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        query = Q()
        query.add(Q(worker_id=int(worker_id)), query.connector)

        recordsTotal = LabourHoliday.objects.filter(query).count()
        records = (
            LabourHoliday.objects.filter(query)
            .order_by(sort_col)[start : (start + length)]
            .values("worker__name", "start_date", "end_date", "days", "leave_allocation__leave_type__name", "description", "status", "created_on", "created_by")
        )

        response = {
            "draw": request.POST.get("draw"),
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }
        for data in records:
            start_date = Util.get_local_time(data["start_date"], False)
            end_date = Util.get_local_time(data["end_date"], False)
            created_on = Util.get_local_time(data["created_on"], True)
            response["data"].append(
                {
                    "worker": data["worker__name"],
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": "%.2f" % data["days"] if data["days"] is not None else "",
                    "description": data["description"],
                    "leave_allocation__leave_type__name": data["leave_allocation__leave_type__name"],
                    "created_on": created_on,
                    "status": dict(choices.leave_status)[data["status"]],
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
