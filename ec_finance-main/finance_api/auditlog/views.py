
from email.policy import default
from django.contrib.contenttypes.models import ContentType
from django.db.models import (Case, CharField, F, OuterRef, Prefetch, Q,
                              Subquery, Value, When, Window)
from django.db.models.functions import Concat
from finance_api.rest_config import CustomPagination
from rest_framework import generics,viewsets
from finance_api.rest_config import APIResponse
from auditlog.models import AuditAction, Auditlog,InvoiceHistory
from auditlog.serializers import AuditLogSerializer,InvoiceHistorySerializer,paymentHistorySerializer
from rest_framework.decorators import api_view
from base.util import Util
from sales.models import Invoice
from payment.models import PaymentRegistration
from django.db.models.aggregates import Count, Max, Min, Sum


def insert(app_name, model_name, object_ids, action_id, action_by_id, ip_addr, descr,document_no="",username="",status_code=""):
    app_name = app_name.lower()
    model_name = model_name.lower()
    model_id = ContentType.objects.filter(app_label=app_name, model=model_name)[0].id
    for object_id in object_ids:
        log = Auditlog(content_type_id=model_id, object_id=object_id, action_id=action_id, action_by_id=action_by_id, ip_addr=ip_addr, descr=descr,document_no=document_no,username=username,status_code=status_code)
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

class AuditLog(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        model = self.request.GET.get("model")
        group = self.request.GET.get("group")
        ids =  self.request.GET.get("id")
        query =Q()
        if ids is not None and ids != "":
            obejct_ids = [int(x) for x in ids.split("-")]
            query.add(Q(object_id__in=obejct_ids), query.connector)
        if model is not None:
            query.add(Q(content_type_id__model__in=[str(model)]), query.connector)
        if group is not None:
            query.add(Q(group__iexact=group), query.connector)
        queryset =  (Auditlog.objects.filter(query)
                     .values("action_on","descr","ip_addr","action_by__first_name","action_by__last_name","username","document_no","object_id")
                     .annotate(
                         full_name=Case(When(action_by__isnull = True,then=Value('username')), default=Concat(F('action_by__first_name'),Value(' '),F('action_by__last_name')))
                        ))
        return queryset

class InvoiceHistoryView(viewsets.ModelViewSet):
    serializer_class = InvoiceHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        ids =  self.request.GET.get("id")
        group =  self.request.GET.get("group")
        if group is not None:
            query.add(Q(group__iexact=group), query.connector)
        query =Q()
        if ids is not None and ids != "":
            query.add(Q(object_id=ids), query.connector)
        queryset =  (Auditlog.objects.filter(query)
                     .values(
                         "id","object_id","action_on","descr","ip_addr","action_by__first_name",
                         "action_by__last_name","status_code","username","document_no",
                         )
                     .annotate(
                         full_name=Case(
                            When(action_by__isnull = True,then=F('username'),),
                         default=Concat(F('action_by__first_name'),Value(' '),F('action_by__last_name'))),
                         )
                         )
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            object_ids =[dict(row)["object_id"] for row in serializer.data]
            invoices = Invoice.objects.filter(id__in=object_ids).values("id","invoice_number","currency__name","invoice_value","customer__name","status__desc","invoice_due_date")
            invoice_numbers = Util.get_dict_from_queryset("id","invoice_number",invoices)
            currency_names = Util.get_dict_from_queryset("id","currency__name",invoices)
            invoice_values = Util.get_dict_from_queryset("id","invoice_value",invoices)
            customer_names = Util.get_dict_from_queryset("id","customer__name",invoices)
            status_descs = Util.get_dict_from_queryset("id","status__desc",invoices)
            invoice_due_dates = Util.get_dict_from_queryset("id","invoice_due_date",invoices)
        
            
            for i in serializer.data:
                row = dict(i)
                if row["object_id"] in invoice_numbers:
                    invoice_number = invoice_numbers[row["object_id"]]
                    i.update({"invoice_number":invoice_number})
                    
                if row["object_id"] in currency_names:
                    currency_name = currency_names[row["object_id"]]
                    i.update({"currency_name":currency_name})
                    
                if row["object_id"] in invoice_values:
                    invoice_value = invoice_values[row["object_id"]]
                    i.update({"invoice_value":invoice_value})

                if row["object_id"] in customer_names:
                    customer_name = customer_names[row["object_id"]]
                    i.update({"customer_name":customer_name})
                
                if row["object_id"] in status_descs:
                    status_desc = status_descs[row["object_id"]]
                    i.update({"status_desc":status_desc})
                
                if row["object_id"] in invoice_due_dates:
                    invoice_due_date = invoice_due_dates[row["object_id"]]
                    i.update({"invoice_due_date":invoice_due_date})
                
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(serializer.data)
        
def insert_invoice_history(entity, entity_type,created_by, status_code, action, created_on, ip_address, document_no, old_value):
    history = InvoiceHistory(entity_id=entity , entity_type=entity_type,created_by_id=created_by, status_code=status_code, action=action,created_on=created_on,document_no=document_no,ip_address=ip_address,old_value=old_value)
    history.save()
    
class paymentHistoryView(generics.ListAPIView):
    serializer_class = paymentHistorySerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        ids =  self.request.GET.get("id")
        query =Q()
        if ids :
            query.add(Q(payment__id=ids), query.connector)
        queryset =(PaymentRegistration.objects.filter(payment__id=ids)
                     .values(
                         "id",
                         "payment__total_amount",
                         "payment__paid_on",
                         "currency_rate",
                         "payment__currency_total_amount",
                         "payment__payment_mode",
                           "invoice__invoice_number",
                           "invoice__created_on",
                           "invoice__currency__code",
                           "currency_amount",
                           "invoice__invoice_due_date",
                           "invoice__invoice_value",
                           "invoice__amount_paid",
                           "invoice__currency_invoice_value"
                     ).annotate(
                        outstanding = Sum(F("invoice__invoice_value") - F("invoice__amount_paid")),
                        customer_outstanding = Sum(F("invoice__currency_invoice_value") - F("invoice__cust_amount_paid"))
                     ))
                    
        return queryset
    
    