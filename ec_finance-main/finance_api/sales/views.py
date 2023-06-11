import calendar
import json
from datetime import date, datetime, timedelta
from lib2to3.pgen2.pgen import ParserGenerator
import requests
from attachment import views as attachment_views
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import views as base_views
from base.models import CodeTable, Currency
from base.util import Util
from customer.models import Country, Customer
from django.contrib.auth.models import User
from django.db import transaction

# from django.core.exceptions import ValidationError
from django.db.models import Case, CharField, Count, F, Func, Q, Value, When
from django.db.models.aggregates import Count, Max, Sum
from django.db.models.functions import Concat

# from django.db.models.functions import Coalesce, Greatest
# from django.db.models.functions.window import FirstValue, LastValue
from finance_api.rest_config import APIResponse, CustomPagination
from finance_api.settings import EC_API_KEY, EC_API_URL, MEDIA_URL
from rest_framework import generics, viewsets
from rest_framework.decorators import action, api_view
from sales.filter import ActionFilter, InvoiceFilter
from sales.models import CollectionAction, CollectionActionAttachment, CollectionInvoice, CustomInvoice, Invoice, InvoiceOrder, Scheduler, SchedulerItem
from sales.serializers import ActionSerializer, CloseInvoiceSerializer, CustomerDetailSerializer, InvoiceListSerializer, InvoiceSerializer, SchedulerSerializer


class CollectionInvoiceView(viewsets.ModelViewSet):
    serializer_class = InvoiceListSerializer
    pagination_class = CustomPagination
    filterset_class = InvoiceFilter
    ordering = [F("action_date").desc(nulls_last=True), F("action_status").desc(nulls_last=True)]

    def get_queryset(self):
        query = Q()
        customer_id = self.request.GET.get("customer_id")
        reminder_id = self.request.GET.get("reminder_id")
        status = self.request.GET.get("status")
        slot = self.request.GET.get("slot")
        if slot == "day":
            if status in ["due", "done"]:
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_finished=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_date__date=date.today()), query.connector)
            elif status == "pending":
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_finished=False) & Q(collectioninvoice_invoice__action__isnull=True), query.connector)
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__date=date.today()), query.connector)
            elif status == "closed":
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__date=date.today()), query.connector)
            elif status == "all":
                query.add(
                    Q(scheduleritem_invoice__scheduler__created_on__date=date.today()) | Q(collectioninvoice_invoice__action__action_date__date=date.today()), query.connector
                )
        elif slot == "week":
            first_day_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
            last_day_week = datetime.now() - timedelta(days=-5)
            if status in ["due", "done"]:
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_finished=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_week, last_day_week]), query.connector)
            elif status == "pending":
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_finished=False) & Q(collectioninvoice_invoice__action__isnull=True), query.connector)
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_week]), query.connector)
            elif status == "closed":
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_week]), query.connector)
            elif status == "all":
                query.add(
                    Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_week])
                    | Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_week, last_day_week]),
                    query.connector,
                )
        elif slot == "month":
            first_day_month = datetime.today().replace(day=1, hour=00, minute=00, second=00)
            last_date = calendar.monthrange(date.today().year, date.today().month)[1]
            last_day_month = datetime.today().replace(day=last_date, hour=00, minute=00, second=00)
            if status in ["due", "done"]:
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_finished=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_month, last_day_month]), query.connector)
            elif status == "pending":
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_finished=False) & Q(collectioninvoice_invoice__action__isnull=True), query.connector)
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_month, last_day_month]), query.connector)
            elif status == "closed":
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_month, last_day_month]), query.connector)
            elif status == "all":
                query.add(
                    Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_month, last_day_month])
                    | Q(collectioninvoice_invoice__action__action_date__range=[first_day_month, last_day_month]),
                    query.connector,
                )
        else:
            query.add(~Q(status__code="INVCLOSED"), query.connector)
            if status == "legal_action":
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(is_finished=False), query.connector)
            elif status == "all":
                query = Q()
            else:
                query.add(Q(is_legal=False), query.connector)
            if status in ["due", "done"]:
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_finished=False), query.connector)
            elif status == "finished":
                query.add(Q(is_finished=True), query.connector)
            elif status == "pending":
                query.add(Q(is_finished=False) & Q(collectioninvoice_invoice__action__isnull=True), query.connector)
            elif status == "closed":
                query = Q()
                query.add(Q(is_legal=False), query.connector)
                query.add(Q(status__code="INVCLOSED"), query.connector)
        if customer_id:
            query = Q()
            query.add(Q(customer__id=customer_id), query.connector)
        if reminder_id and customer_id:
            query = Q()
            query.add(Q(customer__id=customer_id) & Q(scheduleritem_invoice__scheduler__id=reminder_id), query.connector)
        query.add(
            Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True),
            query.connector,
        )
        queryset = (
            Invoice.objects.prefetch_related("collectioninvoice_invoice")
            .filter(query)
            .values(
                "id",
                "invoice_number",
                "is_finished",
                "payment_tracking_number",
                "customer_id",
                "invoice_created_on",
                "amount_paid",
                "is_legal",
            )
            .annotate(
                status=F("status__desc"),
                secondary_status=F("secondry_status__desc"),
                customer_name=F("customer__name"),
                email=F("invoice_email"),
                contact=F("invoice_phone"),
                country=F("country__name"),
                last_reminder_date=F("last_rem_date"),
                invoice_amount=F("invoice_value"),
                total_reminder=Count(
                    "scheduleritem_invoice__scheduler__id",
                    distinct=True,
                    filter=query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), query.connector),
                ),  # scheduleritem_invoice__scheduler__id
                action_date=Max("collectioninvoice_invoice__action__action_date"),
                action_status=Case(
                    When(is_finished=False, then=Max("collectioninvoice_invoice__action__action_status")),
                    default=Value("finished"),
                    output_field=CharField(),
                ),
            )
            .distinct()
        )
        return queryset

    @action(detail=False, methods=["get"])
    def dashboard_reminder_overview(self, request):
        time = request.GET.get("time")
        action_date_query = Q()
        action_date_query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), action_date_query.connector)
        scheduler_query = Q()
        scheduler_query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), scheduler_query.connector)
        if time == "day":
            action_date_query.add(Q(collectioninvoice_invoice__action__action_date__date=date.today()), action_date_query.connector)
            scheduler_query.add(Q(scheduleritem_invoice__scheduler__created_on__date=date.today()), scheduler_query.connector)
        elif time == "week":
            first_day_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
            last_day_of_week = datetime.now() - timedelta(days=-5)
            action_date_query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_week, last_day_of_week]), action_date_query.connector)
            scheduler_query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_of_week]), scheduler_query.connector)
        elif time == "month":
            first_day_of_month = datetime.today().replace(day=1, hour=00, minute=00, second=00)
            last_date = calendar.monthrange(date.today().year, date.today().month)[1]
            last_day_of_month = datetime.today().replace(day=last_date, hour=00, minute=00, second=00)
            action_date_query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_month, last_day_of_month]), action_date_query.connector)
            scheduler_query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_month, last_day_of_month]), scheduler_query.connector)
        closed_query = Q()
        closed_query.add(Q(status__code="INVCLOSED"), closed_query.connector)
        queryset = list(
            Invoice.objects.prefetch_related("collectioninvoice_invoice")
            .values(
                "country__name",
            )
            .annotate(
                new=Count(
                    "invoice_number",
                    filter=(scheduler_query)
                    & ~Q(collectioninvoice_invoice__action__is_legal=False)
                    & Q(collectioninvoice_invoice__action__isnull=True)
                    & Q(is_finished=False)
                    & Q(is_legal=False)
                    & ~Q(status__code="INVCLOSED"),
                    distinct=True,
                ),
                follow_ups=Count(
                    "invoice_number",
                    filter=(action_date_query)
                    & Q(collectioninvoice_invoice__action__action_status="due")
                    & ~Q(status__code="INVCLOSED")
                    & Q(is_finished=False)
                    & Q(is_legal=False),
                    distinct=True,
                ),
                processed=Count(
                    "invoice_number",
                    filter=(action_date_query)
                    & Q(collectioninvoice_invoice__action__action_status="done")
                    & ~Q(status__code="INVCLOSED")
                    & Q(is_finished=False)
                    & Q(is_legal=False),
                    distinct=True,
                ),
                closed=Count(
                    "invoice_number",
                    filter=(scheduler_query) & Q(status__code="INVCLOSED") & Q(is_legal=False),
                    distinct=True,
                ),
                all=Count("invoice_number", filter=scheduler_query | action_date_query, distinct=True),
                slot=Value(str(time)),
            )
            .distinct()
        )
        total_record = []
        total_new = 0
        total_follow_ups = 0
        total_processed = 0
        total_closed = 0
        total_all = 0
        for x in queryset:
            total_new = total_new + x["new"]
            total_follow_ups = total_follow_ups + x["follow_ups"]
            total_processed = total_processed + x["processed"]
            total_closed = total_closed + x["closed"]
            total_all = total_all + x["all"]
            if x["new"] | x["follow_ups"] | x["processed"] | x["closed"] | x["all"] != 0:
                total_record.append(x)
        all_record = {
            "country__name": "All",
            "new": total_new,
            "follow_ups": total_follow_ups,
            "processed": total_processed,
            "slot": str(time),
            "closed": total_closed,
            "all": total_all,
        }
        total_record.insert(0, all_record)
        return APIResponse(total_record)

    @action(detail=False, methods=["get"])
    def dashboard_legal_overview(self, request):
        time = request.GET.get("time")
        action_date_query = Q()
        action_date_query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), action_date_query.connector)
        scheduler_query = Q()
        scheduler_query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), scheduler_query.connector)
        if time == "day":
            action_date_query.add(Q(collectioninvoice_invoice__action__action_date__date=date.today()), action_date_query.connector)
            scheduler_query.add(Q(scheduleritem_invoice__scheduler__created_on__date=date.today()), scheduler_query.connector)
        elif time == "week":
            first_day_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
            last_day_of_week = datetime.now() - timedelta(days=-5)
            action_date_query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_week, last_day_of_week]), action_date_query.connector)
            scheduler_query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_of_week]), scheduler_query.connector)
        elif time == "month":
            first_day_of_month = datetime.today().replace(day=1, hour=00, minute=00, second=00)
            last_date = calendar.monthrange(date.today().year, date.today().month)[1]
            last_day_of_month = datetime.today().replace(day=last_date, hour=00, minute=00, second=00)
            action_date_query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_month, last_day_of_month]), action_date_query.connector)
            scheduler_query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_month, last_day_of_month]), scheduler_query.connector)
        query = Q()
        query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), query.connector)
        query.add(Q(is_legal=True), query.connector)
        close_query = Q()
        close_query.add(Q(status__code="INVCLOSED"), close_query.connector)
        queryset = list(
            Invoice.objects.prefetch_related("collectioninvoice_invoice")
            .filter(query)
            .values("country__name")
            .annotate(
                legal_follow_ups=Count(
                    "id",
                    filter=(action_date_query)
                    & Q(collectioninvoice_invoice__action__action_status="due")
                    & Q(collectioninvoice_invoice__action__is_legal=True)
                    & Q(is_finished=False)
                    & ~Q(status__code="INVCLOSED"),
                    distinct=True,
                ),
                legal_processed=Count(
                    "id",
                    filter=(action_date_query)
                    & Q(collectioninvoice_invoice__action__action_status="done")
                    & Q(collectioninvoice_invoice__action__is_legal=True)
                    & Q(is_finished=False)
                    & ~Q(status__code="INVCLOSED"),
                    distinct=True,
                ),
                closed=Count("id", filter=scheduler_query & close_query, distinct=True),
                all=Count("id", filter=scheduler_query | action_date_query, distinct=True),
                slot=Value(str(time)),
            )
        )
        new_query = Q()
        new_query.add(~Q(status__code="INVCLOSED"), new_query.connector)
        new_query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), new_query.connector)
        new_query.add(Q(is_legal=True), new_query.connector)
        new_query.add(~Q(collectioninvoice_invoice__action__is_legal=True), new_query.connector)
        legal_new_count = list(
            Invoice.objects.prefetch_related("collectioninvoice_invoice")
            .filter(new_query)
            .values("country__name")
            .annotate(
                legal_new=Count(
                    "id",
                    filter=(scheduler_query),
                    distinct=True,
                ),
            )
        )
        total_new = 0
        total_follow_ups = 0
        total_processed = 0
        total_closed = 0
        total_all = 0
        total_record = []
        for x in queryset:
            for country in legal_new_count:
                if x["country__name"] == country["country__name"]:
                    x["legal_new"] = country["legal_new"]
            if "legal_new" not in x:
                x["legal_new"] = 0
            total_new = total_new + x["legal_new"]
            total_follow_ups = total_follow_ups + x["legal_follow_ups"]
            total_processed = total_processed + x["legal_processed"]
            total_closed = total_closed + x["closed"]
            total_all = total_all + x["all"]
            if x["legal_new"] | x["legal_follow_ups"] | x["legal_processed"] | x["closed"] | x["all"] != 0:
                total_record.append(x)
        all_record = {
            "country__name": "All",
            "legal_new": total_new,
            "legal_follow_ups": total_follow_ups,
            "legal_processed": total_processed,
            "slot": str(time),
            "closed": total_closed,
            "all": total_all,
        }
        total_record.insert(0, all_record)

        return APIResponse(total_record)

    @action(detail=False, methods=["post"])
    def calender_view(self, request):
        form_date = request.data.get("from_date")
        to_date = request.data.get("to_date")
        query = Q()
        query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), query.connector)
        if form_date and to_date:
            query.add(Q(collectioninvoice_invoice__action__action_date__range=[form_date, to_date]), query.connector)
        queryset = (
            Invoice.objects.prefetch_related("collectioninvoice_invoice")
            .filter(query)
            .values("id", "invoice_number", "customer_id", "customer__name", "is_legal")
            .annotate(action_date=Func(Max("collectioninvoice_invoice__action__action_date"), Value("YYYY-MM-DD"), function="to_char", output_field=CharField()))
        )
        invoice_numbers = [invoice_nr["invoice_number"] for invoice_nr in queryset]
        follow_up_query = Q()
        follow_up_query.add(Q(action_date__range=[form_date, to_date]), follow_up_query.connector)
        follow_up_query.add(Q(collectioninvoice_action__invoice__invoice_number__in=invoice_numbers), follow_up_query.connector)
        follow_up_query.add(Q(collectioninvoice_action__action__action_status="due"), follow_up_query.connector)

        follow_up_actions = (
            CollectionAction.objects.prefetch_related("collectioninvoice_action")
            .filter(follow_up_query)
            .values("collectioninvoice_action__invoice__invoice_number")
            .annotate(summary=F("collectioninvoice_action__action__summary"))
            .order_by("collectioninvoice_action__action__action_date")
            .distinct()
        )
        listData = []
        action_summary = Util.get_dict_from_queryset("collectioninvoice_action__invoice__invoice_number", "summary", follow_up_actions)
        for invoice in queryset:
            listData.append(
                {
                    "id": invoice["id"],
                    "title": invoice["invoice_number"],
                    "date": invoice["action_date"],
                    "customer_id": invoice["customer_id"],
                    "customer_name": invoice["customer__name"],
                    "action_desc": action_summary[invoice["invoice_number"]] if invoice["invoice_number"] in action_summary else "",
                    "is_legal": invoice["is_legal"],
                    "className": ["legal-follow-up"],
                }
            )
        return APIResponse(code=1, data=listData, message="")


class LegalInvoiceView(viewsets.ModelViewSet):
    serializer_class = InvoiceListSerializer
    pagination_class = CustomPagination
    filterset_class = InvoiceFilter
    ordering = [F("action_date").desc(nulls_last=True), F("action_status").desc(nulls_last=True)]

    def get_queryset(self):
        query = Q()
        status = self.request.GET.get("status")
        customer_id = self.request.GET.get("customer_id")
        reminder_id = self.request.GET.get("reminder_id")
        slot = self.request.GET.get("slot")
        if slot == "day":
            if status in ["due", "done"]:
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_finished=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_date__date=date.today()), query.connector)
            elif status == "pending":
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(~Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__date=date.today()), query.connector)
            elif status == "closed":
                query.add(Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__date=date.today()), query.connector)
            elif status == "all":
                query.add(Q(is_legal=True), query.connector)
                query.add(
                    Q(scheduleritem_invoice__scheduler__created_on__date=date.today()) | Q(collectioninvoice_invoice__action__action_date__date=date.today()), query.connector
                )
        elif slot == "week":
            first_day_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
            last_day_of_week = datetime.now() - timedelta(days=-5)
            if status in ["due", "done"]:
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_finished=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_week, last_day_of_week]), query.connector)
            elif status == "pending":
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(~Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_of_week]), query.connector)
            elif status == "closed":
                query.add(Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_of_week]), query.connector)
            elif status == "all":
                query.add(Q(is_legal=True), query.connector)
                query.add(
                    Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_week, last_day_of_week])
                    | Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_week, last_day_of_week]),
                    query.connector,
                )
        elif slot == "month":
            first_day_of_month = datetime.today().replace(day=1, hour=00, minute=00, second=00)
            last_date = calendar.monthrange(date.today().year, date.today().month)[1]
            last_day_of_month = datetime.today().replace(day=last_date, hour=00, minute=00, second=00)
            if status in ["due", "done"]:
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_finished=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_month, last_day_of_month]), query.connector)
            elif status == "pending":
                query.add(~Q(status__code="INVCLOSED"), query.connector)
                query.add(~Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_month, last_day_of_month]), query.connector)
            elif status == "closed":
                query.add(Q(status__code="INVCLOSED"), query.connector)
                query.add(Q(is_legal=True), query.connector)
                query.add(Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_month, last_day_of_month]), query.connector)
            elif status == "all":
                query.add(Q(is_legal=True), query.connector)
                query.add(
                    Q(scheduleritem_invoice__scheduler__created_on__range=[first_day_of_month, last_day_of_month])
                    | Q(collectioninvoice_invoice__action__action_date__range=[first_day_of_month, last_day_of_month]),
                    query.connector,
                )
        else:
            query.add(~Q(status__code="INVCLOSED"), query.connector)
            if status in ["due", "done"]:
                query.add(Q(collectioninvoice_invoice__action__action_status=status), query.connector)
                query.add(Q(is_finished=False), query.connector)
                query.add(Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
            elif status == "finished":
                query.add(Q(is_finished=True), query.connector)
            elif status == "pending":
                query.add(~Q(collectioninvoice_invoice__action__is_legal=True), query.connector)
            elif status == "closed":
                query = Q()
                query.add(Q(status__code="INVCLOSED"), query.connector)
            elif status == "all":
                query = Q()
            query.add(Q(is_legal=True), query.connector)
        if customer_id:
            query = Q()
            query.add(Q(customer__id=customer_id), query.connector)
        if reminder_id and customer_id:
            query = Q()
            query.add(Q(customer__id=customer_id) & Q(scheduleritem_invoice__scheduler__id=reminder_id), query.connector)
        query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), query.connector)
        query.add(Q(is_legal=True), query.connector)
        queryset = (
            Invoice.objects.prefetch_related("collectionaction_invoice")
            .filter(query)
            .values(
                "id",
                "invoice_number",
                "is_finished",
                "payment_tracking_number",
                "customer_id",
                "invoice_created_on",
                "amount_paid",
                "is_legal",
            )
            .annotate(
                status=F("status__desc"),
                secondary_status=F("secondry_status__desc"),
                customer_name=F("customer__name"),
                email=F("invoice_email"),
                contact=F("invoice_phone"),
                country=F("country__name"),
                last_reminder_date=F("last_rem_date"),
                invoice_amount=F("invoice_value"),
                total_reminder=Count(
                    "scheduleritem_invoice__scheduler__id",
                    distinct=True,
                    filter=query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), query.connector),
                ),
                action_date=Max(
                    Case(
                        When(
                            collectioninvoice_invoice__action__is_legal=True,
                            then=F(
                                "collectioninvoice_invoice__action__action_date",
                            ),
                        ),
                    ),
                ),
                action_status=Max(
                    Case(
                        When(collectioninvoice_invoice__action__is_legal=True, is_finished=False, then=F("collectioninvoice_invoice__action__action_status")),
                        When(is_finished=True, then=Value("finished")),
                        default=None,
                        output_field=CharField(),
                    ),
                ),
            )
            .distinct()
        )
        return queryset


class ActionView(viewsets.ModelViewSet):
    serializer_class = ActionSerializer
    pagination_class = CustomPagination
    filter_class = ActionFilter

    def get_queryset(self, **kwargs):
        customer_id = self.request.GET.get("customer_id")
        invoice_id = self.request.GET.get("invoice_id")
        query = Q()
        if invoice_id:
            query.add(Q(collectioninvoice_action__invoice_id=invoice_id), query.connector)
        if customer_id:
            query.add(Q(customer_id=customer_id), query.connector)
        queryset = (
            CollectionAction.objects.prefetch_related("collectioninvoice_action")
            .filter(query)
            .values(
                "id",
                "action_by__first_name",
                "action_by__last_name",
                "is_legal",
                "customer__id",
                "action_type",
                "action_status",
                "action_date",
                "summary",
                "is_cust_base"
            )
            .annotate(
                full_name=Concat(F("action_by__first_name"), Value(" "), F("action_by__last_name")),
                invoice_nr = F("collectioninvoice_action__invoice__invoice_number")
            )
        ).distinct("id")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            attachment_ids = [dict(row)["id"] for row in serializer.data]
            attachments = CollectionActionAttachment.objects.filter(object_id__in=attachment_ids).values("url", "id", "name", "uid", "object_id")
            attachment_urls = Util.get_dict_from_queryset("object_id", "url", attachments)
            attachment_uid = Util.get_dict_from_queryset("object_id", "uid", attachments)
            for i in serializer.data:
                row = dict(i)
                if row["id"] in attachment_urls:
                    url = attachment_urls[row["id"]]
                    uid = attachment_uid[row["id"]]
                    url = request.build_absolute_uri(str(MEDIA_URL) + url.strip())
                    i.update({"url": url, "uid": uid})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(serializer.data)

    def create(self, request):
        data = json.loads(request.data["data"])
        is_many = isinstance(data, list)
        c_ip = base_views.get_client_ip(request)
        action_by_id = None
        msg = ""

        if is_many:
            is_legal = data[0]["is_legal"]
            action_by_id = data[0]["action_by_id"]
            action_id = data[0]["action_id"]
            invoice_id = data[0]["invoice_id"]
        else:
            action_by_id = data["action_by_id"]
            action_id = data["action_id"]
            invoice_id = data["invoice_id"]
        user = User.objects.get(id=action_by_id)
        if Util.has_perm("can_add_action", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if action_id != 0:
            action = CollectionAction.objects.get(id=action_id)
            serializer = ActionSerializer(instance=action, data=data[0])
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            is_legal = True if is_legal == "true" else False

            if request.FILES:
                attachment_views.upload("sales", "collectionactionattachment", action_id, request.FILES["attachment"], None, c_ip, "-", action_by_id, True, "")

            log_views.insert("sales", "invoice", [invoice_id], AuditAction.INSERT, action_by_id, c_ip, "Action updated.")
        else:
            msg = "Action Added"
            serializer = self.get_serializer(data=data, many=isinstance(data, list))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        if action_id == 0:
            user = User.objects.get(id=action_by_id).id
            collection_invoice = []
            for action in serializer.data:
                if request.FILES:
                    attachment_views.upload("sales", "collectionactionattachment", action["id"], request.FILES["attachment"], None, c_ip, "-", user, True, "")

                collection_invoice.append(CollectionInvoice(action_id=action["id"], invoice_id=invoice_id))
                log_views.insert("sales", "invoice", [invoice_id], AuditAction.INSERT, user, c_ip, msg)
            CollectionInvoice.objects.bulk_create(collection_invoice)
        return APIResponse(serializer.data)

    @action(detail=False, methods=["post"])
    def customer_level(self, request):
        customer_id = None
        data = json.loads(request.data["data"])
        for cust_base in data:
            cust_base["is_cust_base"] = True
        is_many = isinstance(data, list)
        c_ip = base_views.get_client_ip(request)
        action_by_id = None
        msg = ""
        if is_many:
            customer_id = data[0]["customer_id"]
            action_by_id = data[0]["action_by_id"]
            action_id = data[0]["action_id"]
        else:
            customer_id = data["customer_id"]
            action_by_id = data["action_by_id"]
            action_id = data["action_id"]
        user = User.objects.get(id=action_by_id)
        if Util.has_perm("can_add_action", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        msg = "Action Added"
        serializer = self.get_serializer(data=data, many=isinstance(data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        invoices = None
        invoices = SchedulerItem.objects.filter(customer_id=customer_id).values("scheduler__id").last()
        invoice_numbers = SchedulerItem.objects.filter(scheduler__id=invoices["scheduler__id"], customer_id=customer_id, invoice__is_legal=False).values(
            "invoice__invoice_number", "invoice__id"
        )
        if action_id == 0:
            collection_invoice = []
            user = User.objects.get(id=action_by_id).id
            for action in serializer.data:
                if request.FILES:
                    attachment_views.upload("sales", "collectionactionattachment", action["id"], request.FILES["attachment"], None, c_ip, "-", user, True, "")
                invoice_ids = []
                for invoice in invoice_numbers:
                    invoice_ids.append(invoice["invoice__id"])
                    collection_invoice.append(CollectionInvoice(action_id=action["id"], invoice_id=invoice["invoice__id"]))
                log_views.insert("sales", "invoice", invoice_ids, AuditAction.INSERT, user, c_ip, msg)
            CollectionInvoice.objects.bulk_create(collection_invoice)
        return APIResponse(serializer.data)

    @action(detail=False, methods=["post"])
    def delete_action(self, request):
        action_ids = request.data.get("ids")
        user_id = request.data.get("user_id")
        c_ip = base_views.get_client_ip(request)
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_delete_action", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if action_ids is None:
            return APIResponse(code=0, message="Please select at least one record.")
        action_ids = [int(id) for id in action_ids.split(",")]
        invoice_id = CollectionInvoice.objects.filter(action__id=action_ids[0]).values("invoice__id").first()
        CollectionAction.objects.filter(id__in=action_ids).delete()
        if user_id and invoice_id:
            log_views.insert(
                "sales",
                "invoice",
                [invoice_id["invoice__id"]],
                AuditAction.DELETE,
                user_id,
                c_ip,
                "Action deleted",
            )
        return APIResponse(code=1, message="Action deleted")

    @action(detail=False, methods=["post"])
    def edit_action(self, request):
        action_id = request.data.get("action_id")
        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_update_action", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if action_id != "0":
            action = CollectionAction.objects.filter(id=action_id).values("id", "action_by", "action_type", "action_date", "summary", "action_status").first()
            action["action_tab"] = action["action_status"]

        else:
            user = User.objects.filter(id=user_id).values("id").first()
            action = {"action_type": "call", "action_by": user["id"], "action_tab": "done", "scope": "invoice_level"}
        return APIResponse(code=1, data=action)

    @action(detail=False, methods=["post"])
    def complete_action(self, request):
        action_ids = request.data.get("ids")
        user_id = request.data.get("user_id")
        invoice_id = request.data.get("invoice_id")
        c_ip = base_views.get_client_ip(request)
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_complete_action", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if action_ids is None:
            return APIResponse(code=0, message="Please select at least one record.")
        action_ids = [int(id) for id in action_ids.split(",")]
        CollectionAction.objects.filter(id__in=action_ids).update(action_status="done", action_by_id=user_id)
        if user_id and invoice_id:
            log_views.insert(
                "sales",
                "invoice",
                [invoice_id],
                AuditAction.UPDATE,
                user_id,
                c_ip,
                "Action completed.",
            )
        return APIResponse(code=1, message="Action completed.")

    @action(detail=False, methods=["post"])
    def follow_up_action(self, request):
        action_id = request.data.get("ids")
        user_id = request.data.get("user_id")
        invoice_id = request.data.get("invoice_id")
        action_date = request.data.get("action_date")
        c_ip = base_views.get_client_ip(request)
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_followup_action", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if action_id is None:
            return APIResponse(code=0, message="Please select at least one record.")
        obj = CollectionAction.objects.get(id=action_id)
        obj.id = None
        obj.action_date = action_date
        obj.action_type = "follow_up"
        obj.action_status = "due"
        obj.action_by_id = user_id
        obj.save()
        CollectionInvoice.objects.create(action_id=obj.id, invoice_id=invoice_id)
        if user_id and invoice_id:
            log_views.insert(
                "sales",
                "invoice",
                [invoice_id],
                AuditAction.UPDATE,
                user_id,
                c_ip,
                "Follow-up added.",
            )
        return APIResponse(code=1, message="Follow-up added.")


class SchedulerView(viewsets.ModelViewSet):
    serializer_class = SchedulerSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        query = Q()
        customer_id = self.request.GET.get("customer_id")
        is_legal = self.request.GET.get("is_legal")
        query.add(Q(scheduleritem_scheduler__customer__id=customer_id), query.connector)
        if is_legal:
            query.add(Q(invoice__is_legal=True), query.connector)
        query.add(Q(is_re_processed=True) | Q(is_processed=True), query.connector)
        queryset = (
            Scheduler.objects.filter(query)
            .prefetch_related("scheduleritem_scheduler")
            .values("id", "name", "created_on")
            .annotate(
                customer_name=F("scheduleritem_scheduler__customer__name"),
                customer_id=F("scheduleritem_scheduler__customer__id"),
                total_invoices=Count("scheduleritem_scheduler__invoice__id", filter=Q(is_re_processed=True) | Q(is_processed=True), distinct=True),
            )
        )
        return queryset

    @action(detail=False, methods=["post"])
    def send_to_legal_action(self, request):
        ids = request.data.get("ids")
        c_ip = base_views.get_client_ip(request)
        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_send_to_legal_action", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if ids is None:
            return APIResponse(code=0, message="Please select at least one record.")
        invoice_ids = [int(x) for x in ids.split(",")]
        Invoice.objects.filter(id__in=invoice_ids).update(is_legal=True, is_finished=False)
        if user_id:
            log_views.insert("sales", "invoice", invoice_ids, AuditAction.UPDATE, user_id, c_ip, "Sent to legal action.")
        return APIResponse(code=1, message="Invoice(s) has been sent to legal action.")

    @action(detail=False, methods=["post"])
    def customer_details(self, request):
        customer_id = self.request.data.get("customer_id")
        is_legal = self.request.data.get("is_legal")
        query = Q()
        query.add(Q(customer_id=customer_id), query.connector)
        if is_legal:
            query.add(Q(is_legal=True), query.connector)
        query.add(
            Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True),
            query.connector,
        )
        customer = (
            Invoice.objects.select_related("scheduleritem_invoice")
            .filter(query)
            .aggregate(
                total_invoices=Count("id", distinct=True),
                total_paid_amount=Sum("amount_paid"),
                total_invoice_amount=Sum("invoice_value"),
                total_reminder=Count(
                    "scheduleritem_invoice__scheduler__id",
                    filter=query.add(Q(scheduleritem_invoice__scheduler__is_re_processed=True) | Q(scheduleritem_invoice__scheduler__is_processed=True), query.connector),
                    distinct=True,
                ),
            )
        )
        customer_de = (
            Invoice.objects.select_related("scheduleritem_invoice")
            .filter(customer_id=customer_id)
            .values("country__name", "customer_id", "customer__name")
            .annotate(email=F("invoice_email"), contact=F("invoice_phone"), last_reminder_date=F("last_rem_date"))
            .first()
        )
        customer_de.update(customer)
        serializer = CustomerDetailSerializer(customer_de).data

        return APIResponse(serializer)

    @action(detail=False, methods=["post"])
    def finish_invoice(self, request):
        ids = request.data.get("ids")
        user_id = request.data.get("user_id")
        c_ip = base_views.get_client_ip(request)
        invoice_ids = []
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_finished", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if ids is None:
            return APIResponse(code=0, message="Please select at least one record.")
        invoice_ids = [int(x) for x in ids.split(",")]
        Invoice.objects.filter(id__in=invoice_ids).update(is_finished=True)
        if user_id:
            log_views.insert("sales", "invoice", invoice_ids, AuditAction.UPDATE, user_id, c_ip, "Invoice finished.")
        return APIResponse(code=1, message="Invoice(s) marked as finished.")

    @action(detail=False, methods=["post"])
    def change_invoice_status(self, request):
        invoice_number = request.data.get("invoice_nr")
        status_code = request.data.get("status")
        secondary_status = request.data.get("secondary_status")

        if invoice_number is None:
            return APIResponse(code=0, message="Please select record .")
        status = CodeTable.objects.filter(code=status_code).values("id").first()
        if status_code and status:
            Invoice.objects.filter(invoice_number=invoice_number).update(status_id=status["id"])
        secondary_code = CodeTable.objects.filter(code=secondary_status).values("id").first()
        if secondary_status and secondary_code:
            Invoice.objects.filter(invoice_number=invoice_number).update(secondry_status_id=secondary_code["id"])
        return APIResponse(code=1, message="Invoice status changed.")

    @action(detail=False, methods=["post"])
    def last_scheduler(self, request):
        scheduler = Scheduler.objects.values("ec_scheduler_id").last()["ec_scheduler_id"]
        data = {"key": EC_API_KEY, "funname": "Get_FinanceAppSchedulerIDS", "param": {"SchedualId": scheduler}}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        scheduler_ids = requests.request("GET", EC_API_URL, data=json.dumps(data), headers=headers)
        scheduler_ids = json.loads(scheduler_ids.json())
        scheduler_ids = scheduler_ids["data"]
        return APIResponse(scheduler_ids)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def create_scheduler(self, request):
        scheduler = Scheduler.objects.filter(ec_scheduler_id__isnull=False).values("ec_scheduler_id").last()["ec_scheduler_id"]
        payload_data = {"key": EC_API_KEY, "funname": "Get_FinanceAppSchedulerIDS", "param": {"SchedualId": scheduler}}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        scheduler_ids = requests.request("GET", EC_API_URL, data=json.dumps(payload_data), headers=headers)
        scheduler_ids = json.loads(scheduler_ids.json())
        scheduler_ids = scheduler_ids["data"]
        if scheduler_ids is None or scheduler_ids == "":
            return APIResponse(code=2, message="There are no new invoices to fetch.")
        codes = Util.get_codes("code_table")
        for scheduler_id in scheduler_ids:
            payload_data = {
                "key": EC_API_KEY,
                "funname": "GET_FinAppPaymentReminderScheduleData",
                "param": {
                    "SchedualId": scheduler_id["ID"],
                },
            }
            response = requests.request("GET", EC_API_URL, data=json.dumps(payload_data), headers=headers)
            response = response.json()
            scheduler_list = json.loads(response)
            scheduler_list = scheduler_list["data"]
            if isinstance(scheduler_list, dict):
                ec_customer_ids = [x["companyId"] for x in scheduler_list["Customer"]]
                invoice_data = [x["Invoices"] for x in scheduler_list["Customer"]]
                currency_code = []
                ec_user_ids = []
                invoices_nrs = []
                customer_not_exists = list(Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values_list("ec_customer_id", flat=True))
                customer_bulk = []
                for customer in scheduler_list["Customer"]:
                    if customer["companyId"] not in customer_not_exists:
                        customer_bulk.append(Customer(ec_customer_id=customer["companyId"], name=customer["CustomerName"]))
                if len(customer_bulk) > 0:
                    Customer.objects.bulk_create(customer_bulk)

                customer = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id", "ec_customer_id")
                customer_ids = Util.get_dict_from_queryset("ec_customer_id", "id", customer)
                handling_companies = []
                for invoices in invoice_data:
                    for invoice in invoices:
                        currency_code.append(invoice["currency"])
                        ec_user_ids.append("created_by")
                        invoices_nrs.append(invoice["invoice_number"])
                        handling_companies.append(invoice["hand_company"])
                currency = Currency.objects.filter(code__in=currency_code).values("id", "code")
                currency_ids = Util.get_dict_from_queryset("code", "id", currency)
                handling_com = Customer.objects.filter(ec_customer_id__in=handling_companies).values("id", "ec_customer_id")
                handling_com = Util.get_dict_from_queryset("ec_customer_id", "id", handling_com)
                invoice_orders = []
                scheduler = Scheduler.objects.create(
                    name=scheduler_list["ScheduleName"], is_processed=scheduler_list["is_processed"], created_on=datetime.now(), ec_scheduler_id=scheduler_list["ScheduleId"]
                )
                for invoices in invoice_data:

                    for invoice in invoices:
                        country = Country.objects.filter(code=invoice["country_code"]).values("id").first()
                        country_id = None
                        if country is None:
                            country = Country.objects.create(
                                code=invoice["country_code"],
                                name=invoice["Countryname"],
                            )
                            country_id = country.id
                        else:
                            country_id = country["id"]
                        customer_id = customer_ids[invoice["ec_customer_id"]] if invoice["ec_customer_id"] in customer_ids else None
                        company_id = handling_com[invoice["hand_company"]] if invoice["hand_company"] in handling_com else None

                        invoice["status"] = codes[invoice["status"]] if invoice["status"] in codes else None
                        invoice["customer"] = customer_id
                        invoice["hand_company"] = company_id
                        invoice["currency"] = currency_ids[invoice["currency"]] if invoice["currency"] in currency_ids else None
                        invoice["created_by"] = None
                        invoice["secondry_status"] = codes[invoice["secondry_status"]] if invoice["secondry_status"] in codes else None
                        invoice_orders.append("Orders")
                        invoice["credit_limit"] = invoice["creditLimit"]
                        invoice["customer_credit_limit"] = invoice["creditLimit_Customer"]
                        invoice["delivery_no"] = invoice["delivery_no"]
                        invoice["country"] = country_id
                        invoice["postal_code"] = invoice["postal_code"]
                        invoice["street_address1"] = invoice["address_line_1"]
                        invoice["street_address2"] = invoice["address_line_2"]
                        invoice["invoice_city"] = invoice["city"]
                        invoice["invoice_phone"] = invoice["InvoiceTelephone"]
                        invoice["ec_invoice_id"] = invoice["InvoiceId"]
                        if invoice["invoice_due_date"] == "":
                            invoice.pop("invoice_due_date")
                        if invoice["invoice_close_date"] == "":
                            invoice.pop("invoice_close_date")
                        if invoice["last_rem_date"] == "":
                            invoice.pop("last_rem_date")
                        if invoice["payment_date"] == "":
                            invoice.pop("payment_date")
                        if invoice["invoice_created_on"] == "":
                            invoice.pop("invoice_created_on")
                        if invoice["created_on"] == "":
                            invoice.pop("created_on")
                        invoice_id = None
                        if Invoice.objects.filter(invoice_number=invoice["invoice_number"]).exists():
                            invoice_instance = Invoice.objects.get(invoice_number=invoice["invoice_number"])
                            serializer = InvoiceSerializer(instance=invoice_instance, data=invoice)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            invoice_id = invoice_instance.id
                        else:
                            serializer = InvoiceSerializer(data=invoice)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            invoice_id = serializer.data["id"]
                        SchedulerItem.objects.create(scheduler=scheduler, customer_id=customer_id, invoice_id=invoice_id, is_sent=invoice["is_sent"], is_manual=invoice["is_manul"])
                    orders_bulk = []
                    customer_bulk = []
                    customer_invoice = list(CustomInvoice.objects.filter(invoice_id=invoice_id).values_list("invoice_id", flat=True))
                    if "CustomerInvoice" in invoice:
                        for customer in invoice["CustomerInvoice"]:
                            if invoice_id not in customer_invoice:
                                customer_bulk.append(
                                    CustomInvoice(
                                        invoice_id=invoice_id,
                                        code=customer["code"],
                                        harm_code=customer["harm_code"],
                                        intrastat=customer["intrastat"],
                                        country_of_origin=customer["country_of_origin"],
                                        weight=customer["weight"],
                                        value=customer["value"],
                                        value_curr=customer["value_curr"],
                                        vat_percentage=customer["vat_percentage"],
                                    )
                                )
                        CustomInvoice.objects.bulk_create(customer_bulk)
                    orders = list(InvoiceOrder.objects.filter(invoice_id=invoice_id).values_list("order_number", flat=True))
                    for order in invoice["Orders"]:
                        if order["order_number"] not in orders:
                            orders_bulk.append(
                                InvoiceOrder(
                                    invoice_id=invoice_id,
                                    ec_order_id=order["ec_order_id"],
                                    order_number=order["order_number"],
                                    order_unit_value=order["order_unit_value"],
                                    quantity=order["quantity"],
                                    invoice_amount=order["invoice_amount"],
                                    ord_trp_value=order["ord_trp_value"],
                                    order_vnit_value_curr=order["order_vnit_value_curr"],
                                    invoice_amount_curr=order["invoice_amount_curr"],
                                    is_reduce_vat=order["is_reduce_vat"],
                                    invoice_ref=order["invoice_ref"],
                                )
                            )
                        else:
                            orders.remove(order["order_number"])
                    InvoiceOrder.objects.bulk_create(orders_bulk)
                    InvoiceOrder.objects.filter(order_number__in=orders).delete()
        return APIResponse(code=1, message="invoices successfully fetched.")


class CloseInvoiceView(generics.ListAPIView):
    serializer_class = CloseInvoiceSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        ids = self.request.GET.get("ids")
        ids = [x for x in ids.split(",")]
        query = Q()
        if ids:
            query.add(Q(id__in=ids), query.connector)
        queryset = (
            Invoice.objects.filter(query)
            .values(
                "id",
                "invoice_number",
                "invoice_created_on",
                "invoice_due_date",
                "invoice_value",
                "ec_invoice_id",
                "amount_paid",
                "currency_invoice_value",
                "customer__name",
                "customer__id",
                "customer__ec_customer_id",
                "currency__name",
                "currency__id",
                "curr_rate",
                "status__code",
                "currency__id",
                "cust_amount_paid",
            )
            .annotate(
                outstanding=Sum(F("currency_invoice_value") - F("cust_amount_paid")),
                new_payment=Sum(F("currency_invoice_value") - F("cust_amount_paid")),
                payment_deference_type=Value("INVCLOSED"),
                difference=Value(0.000),
            )
        )
        return queryset


@api_view(["get"])
def edit_invoice(request):
    invoice_id = request.GET.get("ids")
    data = (
        Invoice.objects.filter(id=invoice_id)
        .values(
            "id",
            "customer__ec_customer_id",
            "invoice_number",
            "hand_company__name",
            "invoice_created_on",
            "invoice_due_date",
            "vat_percentage",
            "vat_value",
            "customer__name",
            "transport_cost",
            "country__name",
            "postal_code",
            "status__code",
            "customer__vat_no",
            "invoice_city",
            "street_address1",
            "delivery_date",
            "invoice_value",
            "invoice_address__street_no",
            "invoice_address__street_name",
            "meta_data",
            "remarks",
        )
        .first()
    )

    return APIResponse(data)


@api_view(["get"])
def credit_invoice(request):
    invoice_id = request.GET.get("ids")
    invoice = (
        Invoice.objects.filter(id=invoice_id)
        .values(
            "id",
            "customer__name",
            "street_address1",
            "street_address2",
            "invoice_city",
            "postal_code",
            "country__name",
            "invoice_fax",
            "customer__vat_no",
            "customer__invoice_lang__name",
            "invoice_number",
            "invoice_address__state",
            "invoice_phone",
            "hand_company__name",
            "hand_company__id",
            "hand_company__vat_no",
            "invoice_due_date",
            "custom_value",
            "weight",
            "invoice_value",
            "vat_percentage",
            "transport_cost",
            "delivery_date",
            "invoice_created_on",
        )
        .first()
    )
    hand_id = invoice["hand_company__id"]
    customer = (
        Customer.objects.prefetch_related("address_customer")
        .filter(id=hand_id)
        .values(
            "address_customer__street_address1",
            "address_customer__street_address2",
            "address_customer__city",
            "address_customer__state",
            "address_customer__country",
            "address_customer__fax",
            "address_customer__phone",
            "address_customer__fax",
            "address_customer__postal_code",
        )
        .first()
    )
    data = {**invoice, **customer}
    return APIResponse(data)

