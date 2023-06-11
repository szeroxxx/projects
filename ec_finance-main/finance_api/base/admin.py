from django.contrib import admin

from .models import CodeTable, Currency

# Register your models here.

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["name","code"]
@admin.register(CodeTable)
class CodeAdmin(admin.ModelAdmin):
    list_display = ["name","code"]

