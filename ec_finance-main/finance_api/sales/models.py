from attachment.models import Attachment
from base.choices import action_status, action_types, scheduler_status
from base.models import CodeTable, Currency
from customer.models import Address, Country, Customer
from customer.models import User as ECUser
from django.contrib.auth.models import User
from django.db import models


class Invoice(models.Model):
    ec_invoice_id = models.IntegerField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, unique=True)
    status = models.ForeignKey(CodeTable, on_delete=models.PROTECT, related_name="%(class)s_status")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="%(class)s_customer")
    outstanding_amount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    currency_outstanding_amount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)  # outstandingAmountCustCurrency
    invoice_created_on = models.DateTimeField(null=True, blank=True)
    invoice_due_date = models.DateTimeField(null=True, blank=True)
    invoice_close_date = models.DateTimeField(null=True, blank=True)
    hand_company = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="%(class)s_hand_company")
    invoice_value = models.DecimalField(max_digits=12, decimal_places=3)
    vat_percentage = models.DecimalField(max_digits=12, decimal_places=3)
    vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    order_net_value = models.DecimalField(max_digits=12, decimal_places=3)
    ec_invoice_type_id = models.IntegerField(null=True, blank=True)
    transport_cost = models.DecimalField(max_digits=12, decimal_places=3)
    weight = models.DecimalField(max_digits=12, decimal_places=3)
    custom_value = models.DecimalField(max_digits=12, decimal_places=3)
    cust_account_no = models.CharField(max_length=100, null=True, blank=True)
    delivery_condition = models.CharField(max_length=100, null=True, blank=True)
    intrastat = models.CharField(max_length=100, null=True, blank=True)
    packing = models.IntegerField(null=True, blank=True)
    country_of_origin = models.IntegerField(null=True, blank=True)
    trans_port_serivice = models.IntegerField(null=True, blank=True)
    is_invoiced = models.BooleanField(default=False)
    created_on = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(ECUser, on_delete=models.PROTECT, null=True, blank=True)
    last_rem_date = models.DateTimeField(null=True, blank=True)
    meta_data = models.TextField(null=True, blank=True)
    currency_invoice_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_order_net_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_transport_cost = models.DecimalField(max_digits=12, decimal_places=3)
    # currency_customer_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    curr_rate = models.DecimalField(max_digits=12, decimal_places=8)
    is_invoice_deliver = models.BooleanField(default=False)
    is_invoice_send = models.BooleanField(default=False)
    is_invoice_by_post = models.BooleanField(default=False)
    is_e_invoice = models.BooleanField(default=False)
    ots_vat_percentage = models.DecimalField(max_digits=12, decimal_places=3)
    ots_vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_ots_vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    order_nrs = models.CharField(max_length=500, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=3)
    cust_amount_paid = models.DecimalField(max_digits=12, decimal_places=3)
    payment_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    secondry_status = models.ForeignKey(CodeTable, on_delete=models.PROTECT, null=True, blank=True, related_name="%(class)s_secondry_status")
    is_einv_sign_scheduled = models.BooleanField(default=False)
    original_invoice_number = models.CharField(max_length=100, null=True, blank=True)
    is_downpayment = models.BooleanField(default=False)
    is_peppol_invoice = models.BooleanField(default=False)
    is_peppol_verified = models.BooleanField(default=False)
    payment_tracking_number = models.IntegerField(null=True, blank=True)
    ec_invoice_address_id = models.IntegerField(null=True, blank=True)  # changed column name # no need this column
    invoice_address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True)
    is_legal = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    delivery_no = models.CharField(max_length=100, null=True, blank=True)  # new field
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True)
    invoice_email = models.CharField(max_length=200, null=True, blank=True)
    invoice_phone = models.CharField(max_length=50, null=True, blank=True)
    invoice_fax = models.CharField(max_length=50, null=True, blank=True)
    invoice_city = models.CharField(max_length=50, null=True, blank=True)
    street_address1 = models.CharField(max_length=200, null=True, blank=True)
    street_address2 = models.CharField(max_length=200, null=True, blank=True)
    financial_block = models.BooleanField(default=False)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    paid_on = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.invoice_number)


class InvoiceOrder(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="%(class)s_invoice")
    ec_order_id = models.IntegerField(null=True, blank=True)
    order_number = models.CharField(max_length=100, null=True, blank=True)
    order_unit_value = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    ord_trp_value = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    order_vnit_value_curr = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    ord_trp_value_curr = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    invoice_amount_curr = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    is_reduce_vat = models.BooleanField(default=False)
    invoice_ref = models.CharField(max_length=100, null=True, blank=True)
    purchase_ref = models.CharField(max_length=100, null=True, blank=True)  # new value
    project_ref = models.CharField(max_length=100, null=True, blank=True)  # new value
    article_ref = models.CharField(max_length=100, null=True, blank=True)  # new value


class CustomInvoice(models.Model):  # need to change table name
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="%(class)s_invoice")
    code = models.CharField(max_length=100, null=True)
    harm_code = models.CharField(max_length=100, null=True)
    intrastat = models.CharField(max_length=100, null=True)
    country_of_origin = models.CharField(max_length=100, null=True)
    weight = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    value_curr = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    vat_percentage = models.DecimalField(max_digits=12, decimal_places=5, null=True)


class Scheduler(models.Model):
    ec_scheduler_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name="Scheduler Name", null=True)
    created_on = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    is_re_processed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class SchedulerItem(models.Model):
    scheduler = models.ForeignKey(Scheduler, on_delete=models.PROTECT, related_name="%(class)s_scheduler")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="%(class)s_customer")
    status = models.CharField(max_length=100, choices=scheduler_status, default="pending")
    is_sent = models.BooleanField(default=False)
    sent_on = models.DateTimeField(null=True, blank=True)
    is_manual = models.BooleanField(default=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="%(class)s_invoice", blank=True, null=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.scheduler)


class SchedulerInvoice(models.Model):
    scheduler_item = models.ForeignKey(SchedulerItem, on_delete=models.CASCADE, related_name="scheduler_item")
    invoice = models.ManyToManyField(Invoice, related_name="scheduler_invoice")

    def __str__(self):
        return str(self.scheduler_item)


class CollectionActionAttachment(Attachment):
    pass


class CollectionAction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="%(class)s_customer")
    action_by = models.ForeignKey(User, on_delete=models.PROTECT)
    # invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, related_name="%(class)s_invoice", blank=True, null=True)
    action_type = models.CharField(max_length=100, choices=action_types, null=True, blank=True)
    action_status = models.CharField(max_length=100, choices=action_status, null=True)
    action_date = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_legal = models.BooleanField(default=False)
    is_cust_base = models.BooleanField(default=False)

    def __str__(self):
        return str(self.action_by)


class CollectionInvoice(models.Model):
    action = models.ForeignKey(CollectionAction, on_delete=models.CASCADE, related_name="%(class)s_action")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, related_name="%(class)s_invoice")


class HutaxInvoice(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="%(class)s_invoice")
    hu_status = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField(default="")
    index_number = models.IntegerField(null=True)
    order_count = models.IntegerField(null=True)
    status_time = models.DateTimeField(null=True, blank=True)
    result = models.CharField(max_length=250, null=True)
    error = models.TextField(default="")
    original_invoice_number = models.CharField(max_length=150)
    vat_no = models.CharField(max_length=25, null=True)


class PeppolInvoice(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="%(class)s_invoice")
    pe_status = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=250, null=True, blank=True)
    error = models.TextField(default="")


class InvoiceDiscount(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="%(class)s_invoice")
    code = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    currency_amount = models.DecimalField(max_digits=12, decimal_places=5, null=True)
