import json
from datetime import date, timedelta

from base.sb_send import azure_service
from customer.models import Customer
from django.db.models import Case, CharField, Count, DurationField, ExpressionWrapper, F, IntegerField, Q, Value, When
from django.db.models.aggregates import Sum
from django.db.models.functions import Concat, ExtractDay
from django.utils import timezone
from finance_api.rest_config import APIResponse, CustomPagination
from rest_framework import generics, viewsets
from rest_framework.decorators import action, api_view

from sales.filter import InvoiceFilter
from sales.models import Invoice, Scheduler, SchedulerItem
from sales.serializers import CustomerDetailSerializer, InvoiceScheduleSerializer, PaymentReminderSerializer, SchedulePaymentReminderSerializer


class SchedulePaymentReminderView(viewsets.ModelViewSet):
    serializer_class = SchedulePaymentReminderSerializer
    filterset_class = InvoiceFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        query = Q()
        now = timezone.now()
        handling_company_id = self.request.GET.get("handling_company")
        country_id = self.request.GET.get("country_id")
        status = self.request.GET.get("status")
        include_days = self.request.GET.get("include_days")
        exclude_days = self.request.GET.get("exclude_days")
        invoice_create_on = self.request.GET.get("invoice_create_on")
        # is_pdf_include = self.request.GET.get("is_pdf_include")
        if country_id is not None:
            query.add(Q(country_id=int(country_id)), query.connector)
        if status == "INVPENDING":
            query.add(Q(status__code=status), query.connector)
        if handling_company_id is not None:
            query.add(Q(hand_company__id=int(handling_company_id)), query.connector)
        if include_days is not None:
            query.add(Q(invoice_due_date__range=[date.today() - timedelta(days=int(include_days)), date.today()]), query.connector)
        if exclude_days is not None:
            query.add(~Q(last_rem_date__range=[date.today() - timedelta(days=int(exclude_days)), date.today()]), query.connector)
        if invoice_create_on is not None:
            query.add(Q(created_on__range=[invoice_create_on, date.today()]), query.connector)
        queryset = (
            Invoice.objects.prefetch_related("scheduleritem_invoice")
            .filter(query)
            .values(
                "id",
                "customer__name",
                "customer__id",
                "created_on",
                "invoice_number",
                "hand_company__name",
                "invoice_due_date",
                "invoice_value",
                "currency_invoice_value",
                "amount_paid",
                "currency_ots_vat_value",
                "currency__code",
                "last_rem_date",
                "cust_amount_paid",
            )
            .annotate(
                outstanding=F("invoice_value") - F("amount_paid"),
                customer_outstanding=F("currency_invoice_value") - F("cust_amount_paid"),
                reminder_status=Count("scheduleritem_invoice__scheduler__id"),
                outstanding_days=(ExtractDay(ExpressionWrapper(F("invoice_due_date") - now, output_field=DurationField()))),
            )
        )
        return queryset


class CountryBreakupView(generics.ListAPIView):
    serializer_class = PaymentReminderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        company_id = self.request.GET.get("company_id")
        query = Q()
        schedule_id = self.request.GET.get("schedule_id")
        if schedule_id:
            query.add(Q(scheduleritem_invoice__scheduler__id=schedule_id), query.connector)
        if company_id:
            query.add(Q(hand_company_id=company_id), query.connector)
        query.add(Q(scheduleritem_invoice__is_manual=True), query.connector)
        queryset = (
            Invoice.objects.filter(query)
            .prefetch_related("scheduleritem_invoice")
            .values(
                "country__name",
            )
            .annotate(
                id=F("country__id"),
                zero_days_amount=Sum(
                    "invoice_value",
                    filter=Q(invoice_due_date__date__gte=date.today()) & Q(scheduleritem_invoice__is_manual=True) & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                zero_days_invoice=Count(
                    "id", filter=Q(invoice_due_date__date__gte=date.today()) & Q(scheduleritem_invoice__is_manual=True) & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                ),
                l_ten_days_amount=Sum(
                    "invoice_value",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=11), date.today() - timedelta(days=1)]) & Q(scheduleritem_invoice__is_manual=True),
                ),
                l_ten_days_invoice=Count(
                    "id",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=11), date.today() - timedelta(days=1)])
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                l_thirty_days_amount=Sum(
                    "invoice_value",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=30), date.today() - timedelta(days=12)])
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                l_thirty_days_invoice=Count(
                    "id",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=30), date.today() - timedelta(days=12)])
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                l_sixty_days_amount=Sum(
                    "invoice_value",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=60), date.today() - timedelta(days=31)])
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                l_sixty_days_invoice=Count(
                    "id",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=60), date.today() - timedelta(days=31)])
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                l_ninety_days_amount=Sum(
                    "invoice_value",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=90), date.today() - timedelta(days=61)])
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                l_ninety_days_invoice=Count(
                    "id",
                    filter=Q(invoice_due_date__range=[date.today() - timedelta(days=90), date.today() - timedelta(days=61)])
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                g_ninety_days_amount=Sum(
                    "invoice_value",
                    filter=Q(invoice_due_date__date__lt=date.today() - timedelta(days=91))
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
                g_ninety_days_invoice=Count(
                    "id",
                    filter=Q(invoice_due_date__date__lt=date.today() - timedelta(days=91))
                    & Q(scheduleritem_invoice__is_manual=True)
                    & Q(scheduleritem_invoice__scheduler__id=schedule_id),
                ),
            )
            .distinct()
        )
        return queryset


class CustomerBreakupView(generics.ListAPIView):
    serializer_class = PaymentReminderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        country_id = self.request.GET.get("country_id")
        schedule_id = self.request.GET.get("schedule_id")
        query = Q()
        if country_id:
            query.add(Q(country_id=country_id) & Q(scheduleritem_invoice__scheduler__id=schedule_id), query.connector)
            query.add(Q(scheduleritem_invoice__is_manual=True), query.connector)
            queryset = (
                Invoice.objects.filter(query)
                .prefetch_related("scheduleritem_invoice")
                .values("customer__ec_customer_id", "customer__name", "scheduleritem_invoice__scheduler__created_on")
                .annotate(
                    id=F("customer__id"),
                    email=F("invoice_address__email"),
                    language_code=F("customer__invoice_lang__code"),
                    zero_days_amount=Sum(
                        "invoice_value",
                        filter=Q(invoice_due_date__date__gte=date.today())
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    zero_days_invoice=Count(
                        "id",
                        filter=Q(invoice_due_date__date__gte=date.today())
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_ten_days_amount=Sum(
                        "invoice_value",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=11), date.today() - timedelta(days=1)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_ten_days_invoice=Count(
                        "id",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=11), date.today() - timedelta(days=1)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_thirty_days_amount=Sum(
                        "invoice_value",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=30), date.today() - timedelta(days=12)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_thirty_days_invoice=Count(
                        "id",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=30), date.today() - timedelta(days=12)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_sixty_days_amount=Sum(
                        "invoice_value",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=60), date.today() - timedelta(days=31)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_sixty_days_invoice=Count(
                        "id",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=60), date.today() - timedelta(days=31)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_ninety_days_amount=Sum(
                        "invoice_value",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=90), date.today() - timedelta(days=61)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    l_ninety_days_invoice=Count(
                        "id",
                        filter=Q(invoice_due_date__range=[date.today() - timedelta(days=90), date.today() - timedelta(days=61)])
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    g_ninety_days_amount=Sum(
                        "invoice_value",
                        filter=Q(invoice_due_date__date__lt=date.today() - timedelta(days=91))
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                    g_ninety_days_invoice=Count(
                        "id",
                        filter=Q(invoice_due_date__date__lt=date.today() - timedelta(days=91))
                        & Q(scheduleritem_invoice__is_manual=True)
                        & Q(scheduleritem_invoice__scheduler__id=schedule_id)
                        & Q(country_id=country_id),
                    ),
                )
                .distinct()
            )
            return queryset


class InvoiceBreakupView(generics.ListAPIView):
    serializer_class = PaymentReminderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        customer_id = self.request.GET.get("customer_id")
        country_id = self.request.GET.get("country_id")
        schedule_id = self.request.GET.get("schedule_id")
        query = Q()
        now = timezone.now()
        if customer_id:
            query.add(Q(customer__id=customer_id) & Q(scheduleritem_invoice__scheduler__id=schedule_id) & Q(country__id=country_id), query.connector)
        query.add(Q(scheduleritem_invoice__is_manual=True), query.connector)
        queryset = (
            Invoice.objects.filter(query)
            .prefetch_related("scheduleritem_invoice")
            .values(
                "status__code",
                "id",
                "customer__customer_type",
                "invoice_number",
                "invoice_created_on",
                "outstanding_amount",
                "currency_outstanding_amount",
                "invoice_due_date",
                "invoice_value",
                "currency_invoice_value",
                "amount_paid",
                "currency__code",
                "last_rem_date",
                "order_nrs",
                "scheduleritem_invoice__scheduler__created_on",
                "scheduleritem_invoice__status",
                "scheduleritem_invoice__remarks",
                "cust_amount_paid",
                "currency_invoice_value",
            )
            .annotate(
                reminder_status=Count("scheduleritem_invoice__scheduler__id"),
                outstanding_days=(ExtractDay(ExpressionWrapper(F("invoice_due_date") - now, output_field=DurationField()))),
                outstanding=F("invoice_value") - F("amount_paid"),
                customer_outstanding=Sum(F("currency_invoice_value") - F("cust_amount_paid")),
            )
        )
        return queryset


class ReminderPreview(generics.ListAPIView):
    serializer_class = PaymentReminderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        customer_id = self.request.query_params.get("customer_id")
        query = Q()
        now = timezone.now()
        if customer_id:
            query.add(Q(customer__id=int(customer_id)), query.connector)
        query.add(Q(scheduleritem_invoice__is_manual=True), query.connector)

        queryset = (
            Invoice.objects.prefetch_related("scheduleritem_invoice")
            .filter(query)
            .values(
                "id",
                "country__id",
                "outstanding_amount",
                "currency_outstanding_amount",
                "invoice_created_on",
                "invoice_due_date",
                "amount_paid",
                "payment_date",
                "invoice_number",
                "invoice_value",
                "currency__code",
                "order_nrs",
            )
            .annotate(
                reminder_status=Count("scheduleritem_invoice__scheduler__id"),
                outstanding_days=(ExtractDay(ExpressionWrapper(F("invoice_due_date") - now, output_field=DurationField()))),
            )
        )
        return queryset


@api_view(["get"])
def customer_reminder_preview(request):
    customer_id = request.query_params.get("customer_id", None)
    hand_company_id = request.query_params.get("hand_company_id", None)
    if hand_company_id == "null":
        hand_company_id = None
    if customer_id == "null":
        customer_id = None
    customer = (
        Customer.objects.prefetch_related("invoice_customer")
        .filter(id=customer_id)
        .values("id")
        .annotate(
            customer__name=F("name"),
            total_outstanding_amount=Sum(F("invoice_customer__invoice_value") - F("invoice_customer__amount_paid")),
            total_paid_amount=Sum("invoice_customer__amount_paid"),
            total_invoice_amount=Sum("invoice_customer__invoice_value"),
            email=F("invoice_customer__invoice_email"),
            customer_name=F("invoice_customer__customer__name"),
            hand_com_name=F("invoice_customer__hand_company__name"),
            contact=F("invoice_customer__invoice_phone"),
            fax=F("invoice_customer__invoice_fax"),
            address=Concat(
                "invoice_customer__street_address1",
                Value(" , "),
                "invoice_customer__street_address2",
                Value("Zip: "),
                "invoice_customer__postal_code",
                output_field=CharField(),
            ),
        )
        .first()
    )
    serializer = CustomerDetailSerializer(customer).data
    response = {"data": serializer}
    return APIResponse(response)


class ScheduleView(viewsets.ModelViewSet):
    serializer_class = InvoiceScheduleSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        query = Q()
        query.add(~Q(scheduleritem_scheduler__invoice__status__code="CLOASESTATUS"), query.connector)
        queryset = (
            Scheduler.objects.filter(query)
            .prefetch_related("scheduleritem_scheduler")
            .values(
                "id",
                "name",
                "created_on",
                "created_by__first_name",
                "created_by__last_name",
            )
            .annotate(
                status=Case(When(is_processed=True, then=Value("Sent")), output_field=CharField(), default=Value("Pending")),
                full_name=Concat(F("created_by__first_name"), Value(" "), F("created_by__last_name")),
                automatic_invoice=Sum(Case(When(scheduleritem_scheduler__is_sent=True, then=1), output_field=IntegerField(), default=0)),
                manual_invoice=Sum(Case(When(scheduleritem_scheduler__is_manual=True, then=1), output_field=IntegerField(), default=0)),
                total_invoices=Count("scheduleritem_scheduler__invoice__id"),
            )
        )
        return queryset

    def create(self, request):
        now = timezone.now().today().strftime("%A,%d/%m/%Y %H:%M %p")
        created_on = timezone.now().today()
        customer_ids = request.data.get("customer_ids")
        invoice_ids = request.data.get("invoice_id")
        include_pdf = request.data.get("is_pdf_include")
        user_id = request.data.get("user_id")
        customers_ids = []
        if include_pdf is True:
            include_pdf_val = 1
        else:
            include_pdf_val = 0
        total_items = request.data.get("total_items")
        # invoice_number= request.data.get("invoice_number")
        # customer_name= request.data.get("customer_name")
        if invoice_ids:
            invoice_ids = [x for x in invoice_ids.split(",")]
        if customer_ids:
            customers_ids = [x for x in customer_ids.split(",")]
        # customers_ids = set(customers_ids)
        scheduler = Scheduler.objects.create(name=str(now) + " FinApp", created_on=str(created_on), created_by_id=user_id)
        scheduler_item = []
        scheduler_details = dict(zip(customers_ids, invoice_ids))
        azure_payload = {"type": "schedule", "data": {"user_id": user_id, "total_item": total_items, "scheduler_name": now, "is_include_pdf": include_pdf_val, "items": []}}
        for customer_id, invoice_id in scheduler_details.items():
            scheduler_item = SchedulerItem.objects.create(
                scheduler=scheduler,
                customer_id=int(customer_id),
                invoice_id=int(invoice_id),
            )
            azure_payload["data"]["items"].append(
                {
                    "invoice_number": scheduler_item.invoice.invoice_number,
                }
            )
        # azure_payload = json.dumps(azure_payload)
        # azure_service(azure_payload)
        return APIResponse(code=1, message="Schedule created")

    @action(detail=False, methods=["post"])
    def delete_scheduler(self, request):
        schedule_ids = request.data.get("ids")
        SchedulerItem.objects.filter(scheduler__id=schedule_ids).delete()
        Scheduler.objects.filter(id=schedule_ids).delete()
        return APIResponse(code=1, message="Scheduler deleted")


@api_view(["post"])
def send_reminder(request):
    invoice_number = request.data.get("invoice_number")
    email = request.data.get("email")
    status = request.data.get("status")
    azure_service({"type": "sendReminder", "data": [{"invoice_nr": invoice_number, "status": status, "customer_email": email}]})
    return APIResponse(code=1, message="Reminder sended")


@api_view(["post"])
def schedule(request):
    customer_id = request.data.get("customer_id")
    country_id = request.data.get("country_id")
    user_id = request.data.get("user_id")
    total_items = request.data.get("total_items")
    include_pdf = request.data.get("is_pdf_include")
    query = Q()
    schedule_id = request.data.get("schedule_id")
    if schedule_id:
        query.add(Q(scheduleritem_invoice__scheduler__id=schedule_id), query.connector)
    if customer_id:
        query.add(Q(customer__id=customer_id), query.connector)
    if country_id:
        query.add(Q(country__id=country_id), query.connector)
    scheduler_name = (
        Invoice.objects.filter(query)
        .prefetch_related("scheduleritem_invoice")
        .values(
            "scheduleritem_invoice__scheduler__name",
            "scheduleritem_invoice__scheduler__ec_scheduler_id",
            "scheduleritem_invoice__invoice__customer__ec_customer_id",
        )
    ).first()
    if include_pdf is True:
        include_pdf_val = 1
    else:
        include_pdf_val = 0
    azure_payload = {
        "type": "schedule",
        "data": {
            "user_id": user_id,
            "ec_customer_id": scheduler_name["scheduleritem_invoice__invoice__customer__ec_customer_id"],
            "ec_schedule_id": scheduler_name["scheduleritem_invoice__scheduler__ec_scheduler_id"],
            "total_item": total_items,
            "scheduler_name": scheduler_name["scheduleritem_invoice__scheduler__name"],
            "is_include_pdf": include_pdf_val,
        },
    }
    azure_payload = json.dumps(azure_payload)
    Scheduler.objects.filter(id=schedule_id).update(is_processed=False, is_re_processed=True)
    azure_service(azure_payload)
    return APIResponse(code=1, message="Scheduled")


@api_view(["post"])
def schedule_update(request):
    schedule_data = request.data
    for schedule in schedule_data["data"]:
        ec_invoice_id = schedule["ec_invoice_Id"]
        name = schedule["ScheduleName"]
        is_sent = schedule["IsSent"]
        is_manual = schedule["IsManual"]
        send_date = schedule["SentOn"]
        ec_scheduler_id = schedule["ec_schedule_id"]
        name = schedule["ScheduleName"]
        is_processed = schedule["IsProcessed"]
        IsReProcessed = schedule["IsReProcessed"]
        remarks = schedule["Remarks"]
        message = schedule["message"]

        SchedulerItem.objects.filter(scheduler__name=name, invoice__ec_invoice_id=ec_invoice_id).update(
            is_sent=is_sent,
            sent_on=send_date,
            is_manual=is_manual,
            remarks=remarks,
        )
        Scheduler.objects.filter(name=name).update(is_processed=is_processed, is_re_processed=IsReProcessed, ec_scheduler_id=ec_scheduler_id)
        if is_sent:
            Invoice.objects.filter(ec_invoice_id=ec_invoice_id).update(last_rem_date=send_date)

    return APIResponse(code=1, message="Scheduled Updated")
