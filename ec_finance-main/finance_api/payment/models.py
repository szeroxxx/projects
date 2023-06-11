from pyexpat import model
from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from numpy import True_
from sales.models import Invoice
from customer.models import Customer
from base.models import Currency
from base.choices import base_choices
# Create your models here.
class CodaFile(models.Model):
    xml_string = models.TextField(null=True)
    created_by = models.ForeignKey(User,on_delete=models.PROTECT, null=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    compared_xml_string = models.TextField(null=True)
    file_name = models.CharField(max_length=200,null=True)
    xml_string1 = models.JSONField(blank=True, null=True)
    compared_xml_string2 = models.JSONField(blank=True, null=True)
    
    
class CodaTransaction(models.Model):
    customer_name = models.CharField(max_length=200, null=True)
    coda_file_date = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3,null=True, blank=True)
    message = models.CharField(max_length=500,null=True)
    invoice = models.ForeignKey(Invoice,on_delete=models.PROTECT)
    invoice_no = models.CharField(max_length=200,null=True)
    ec_customer_id = models.IntegerField(null=True, blank=True)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT,null=True,blank=True)
    ec_customer_name = models.CharField(max_length=200, null=True)
    bank_account_no =models.CharField(max_length=200, null=True)
    bank_name = models.CharField(max_length=200,null=True)
    ec_coda_id = models.IntegerField(null=True, blank=True)
    
class PaymentBrowserUnmatch(models.Model):
    customer_name = models.CharField(max_length=200, null=True)
    bank_account_nr =models.CharField(max_length=200, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3,null=True, blank=True)
    message = models.CharField(max_length=500,null=True)
    invoice_nos = models.CharField(max_length=200,null=True)
    remarks = models.CharField(max_length=200,null=True)
    created_on = models.DateTimeField(auto_now_add=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.PROTECT,null=True)
    is_deleted = models.BooleanField(default=False)
    coda_file = models.ForeignKey(CodaFile,on_delete=models.PROTECT,null=True)
    is_mapped = models.BooleanField(default=False)
    bank_name = models.CharField(max_length=200,null=True)
    
    
class CodaCustomerMapping(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT,null=True,blank=True)
    remark = models.TextField(default="")
    bank_customer_name = models.CharField(max_length=200,null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    account_no = models.CharField(max_length=100,null=True)
    
    
class Payment(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    paid_on = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(Currency,on_delete=models.PROTECT, null=True)
    currency_rate = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    currency_total_amount = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    payment_mode = models.CharField(max_length=100,choices=base_choices("payment_mode"), null=True)
    
    
class PaymentRegistration(models.Model):
    payment =  models.ForeignKey(Payment, on_delete=models.PROTECT, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    amount = models.IntegerField(null=True)
    transfer_type = models.CharField(max_length=50,null=True)
    reference =  models.CharField(max_length=50,null=True)
    ref_document_do = models.CharField(max_length=50,null=True)
    invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE,null=True)
    payment_difference_type = models.CharField(max_length=100,choices=base_choices("payment_difference_types"),null=True)
    payment_date = models.DateTimeField(null=True)
    balance_on_date = models.DecimalField(max_digits=12, decimal_places=3,null=True)
    remark = models.TextField(default="")
    created_by = models.ForeignKey(User,on_delete=models.PROTECT,null=True)
    # modified_by = models.ForeignKey(User,on_delete=models.PROTECT,null=True,related_name="modified_by")
    username = models.CharField(max_length=100,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(null=True)
    currency_amount = models.IntegerField(null=True)
    currency_balance_on_date = models.DecimalField(max_digits=12, decimal_places=3,null=True)
    paid_on = models.DateTimeField(null=True,blank=True)
    currency = models.ForeignKey(Currency,on_delete=models.PROTECT,null=True)
    currency_rate = models.DecimalField(max_digits=12, decimal_places=8,null=True)
    currency_total_amount = models.DecimalField(max_digits=12, decimal_places=3,null=True)


"""
pk_PaymentId	bigint
CustomerId  	bigint
Amount      	numeric
TransferType	varchar
Reference	    nvarchar
RefDocumentNo	varchar
InvoiceId	      bigint
PaymentDifferenceType	bigint
PaymentDate	datetime
BalanceOnDate	numeric
Remark	nvarchar
CreatedBy	bigint
CreatedDate	datetime
ModifiedBy	bigint
ModifiedDate	datetime
PaymentHeaderId	bigint
Currency_Amount	numeric
Currency_BalanceOnDate	numeric
CurrencyId	bigint
CurrRate	decimal
CurrSymbol	nvarchar


PaymentId	 bigint
CompanyId	 bigint
TotalAmount	 decimal
PaidOn	     datetime
PaymentMode	 bigint
CurrencyId	 bigint
CurrRate	 decimal
CurrSymbol	 nvarchar(20)
Currency_TotalAmount	  decimal"""