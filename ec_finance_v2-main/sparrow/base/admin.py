from base.models import (AppReport, CommentType, Currency, CurrencyRate,
                         DocNumber, Remark, Remark_Attachment, SysParameter, Base_Attachment)
from django.contrib import admin

# from partners.models import Pricelist, PricelistLine

admin.site.register(Remark_Attachment)
admin.site.register(Base_Attachment)

@admin.register(AppReport)
class AppReportAdmin(admin.ModelAdmin):
    list_display = ["app", "report"][::-1]


@admin.register(CommentType)
class CommentTypeAdmin(admin.ModelAdmin):
    list_display = ["created_by", "created_on", "is_active", "code", "name"][::-1]


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["is_deleted", "is_base", "symbol", "name"][::-1]


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ["created_by", "created_on", "expire_date", "reference_date", "factor", "currency"][::-1]


@admin.register(DocNumber)
class DocNumberAdmin(admin.ModelAdmin):
    list_display = ["nextnum", "nextint", "increment", "length", "prefix", "desc", "code"][::-1]


@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ["prep_section", "prep_on", "prep_by", "comment_type", "created_by", "created_on", "remark_type", "remark", "content_type", "entity_id"][::-1]


@admin.register(SysParameter)
class SysParameterAdmin(admin.ModelAdmin):
    list_display = ["for_system", "para_group", "para_value", "descr", "para_code"][::-1]
