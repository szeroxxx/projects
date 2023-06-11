from django.contrib import admin

# Register your models here.
from sales.models import (
    CollectionAction,
    CollectionActionAttachment,
    CollectionInvoice,
    CustomInvoice,
    Invoice,
    InvoiceDiscount,
    InvoiceOrder,
    Scheduler,
    SchedulerInvoice,
    SchedulerItem,
)

admin.site.register(Scheduler)
admin.site.register(InvoiceOrder)
admin.site.register(CustomInvoice)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_editable = ("is_legal",)
    list_display = ("invoice_number", "customer", "is_legal", "order_nrs")


@admin.register(CollectionAction)
class CollectionActionAdmin(admin.ModelAdmin):
    list_display = ["customer", "action_by"]


@admin.register(CollectionInvoice)
class CollectionInvoiceAdmin(admin.ModelAdmin):
    list_display = ["action_id", "invoice"]


@admin.register(SchedulerInvoice)
class SchedulerInvoiceAdmin(admin.ModelAdmin):
    list_display = ["scheduler_item", "show_invoices"]

    def show_invoices(self, obj):
        return "\n".join([a.invoice_number for a in obj.invoice.all()])


@admin.register(SchedulerItem)
class SchedulerItemAdmin(admin.ModelAdmin):
    list_display = ["scheduler", "customer", "status"]


@admin.register(CollectionActionAttachment)
class CollectionActionAttachmentAdmin(admin.ModelAdmin):
    list_diaplay = ["name", "user"]


@admin.register(InvoiceDiscount)
class InvoiceDiscountAdmin(admin.ModelAdmin):
    list_diaplay = ["invoice", "code"]
