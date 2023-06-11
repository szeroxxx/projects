from django.core.management.base import BaseCommand
from django.conf import settings
from tenant_schemas.utils import schema_context
import logging
from exception_log import manager
from base.util import Util
import openpyxl
from eda.models import Category
from django.db import transaction
from products.models import Product
from products.products_view import create_product
from sales.models import Order, OrderLine, OrderCertificates, Order_Attachment, ComponentBOM,OrderStatus as sales_order_status
from purchasing.models import PurchaseOrder, PurchaseOrderLine, PurchasePlanLine, PurchasePlan, PurchaseOrderCertificates, PurchasePricelist, PurchasePricelistLine, PurchaseRequisition, PurchaseRequisitionLine, PurchaseOrder_Attachment, PurchasePlanFrom, ApprovalRule, ApprovalRuleLine, ApprovalFrom, ReceivedApproval,OrderStatus as purchaseorder_status
from production.models import Mfg_order
from logistics.models import TransferOrder, TransferOrderLine, ShipMethod, Inspection, InspectionLine, TestName, ShipLabel, TransportCost, ReceivedTransferOrderLine, InspectionType, PurchaseOrderReceipt
from datetime import date, timedelta
from financial.models import Invoice,InvoiceStatus    

class Command(BaseCommand):
    help = "cancel sale orders."

    def handle(self, *args, **options):
        try:
            with schema_context('pcbpower'):
                with transaction.atomic():    
                    current_date = date.today()
                    order_staus_id=sales_order_status.objects.filter(name='cancel').values('id').first()
                    purchaseorder_status_id=purchaseorder_status.objects.filter(name='cancel').values('id').first()
                    invoice_status_id=InvoiceStatus.objects.filter(name='closed').values('id').first()
                    Order.objects.filter(created_on__lte="2019-07-31",status__name__in=['draft','new']).update(status_id=order_staus_id['id'],remarks='Order cancel due to new Assembly on '+ str(current_date))
                    PurchaseOrder.objects.filter(created_on__lte="2019-07-31",status__name__in=['draft','new']).update(status_id=purchaseorder_status_id['id'],remarks='Order cancel due to new Assembly on '+ str(current_date))
                    Mfg_order.objects.filter(created_on__lte="2019-07-31",status__in = ['pending','started']).update(status='cancel',remarks='Order cancel due to new Assembly on '+ str(current_date))
                    Invoice.objects.filter(created_on__lte="2019-07-31",invoice_status__name='draft').update(invoice_status_id=invoice_status_id['id'],remarks='Order cancel due to new Assembly on '+ str(current_date))
                    TransferOrder.objects.filter(created_on__lte="2019-07-31",status='draft').update(status='cancel',remarks='Order cancel due to new Assembly on '+ str(current_date))               
        except Exception as e:
            logging.exception('Something went wrong.') 
