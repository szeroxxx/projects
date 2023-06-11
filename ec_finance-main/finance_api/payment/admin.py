from django.contrib import admin
from payment.models import CodaFile,PaymentBrowserUnmatch,CodaCustomerMapping, Payment, CodaTransaction
# Register your models here.

admin.site.register(Payment)
admin.site.register(CodaTransaction)

admin.site.register(PaymentBrowserUnmatch)

@admin.register(CodaFile)
class CodaFileAdmin(admin.ModelAdmin):
    list_display= ['file_name']
    
@admin.register(CodaCustomerMapping)
class CodaCustomerMappingAdmin(admin.ModelAdmin):
    list_display= ['bank_customer_name']