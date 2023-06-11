from django.contrib import admin

from hrm.models import AcademicQualification


# Register your models here.
class AcademicQualificationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by")


admin.site.register(AcademicQualification, AcademicQualificationAdmin)
