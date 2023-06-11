from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# from production.models import Labour


class LeaveType(models.Model):
    name = models.CharField(max_length=150)
    days = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Default duration of the leave type")


class LeaveAllocation(models.Model):
    worker = models.ForeignKey(Labour, on_delete=models.PROTECT)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    allocate_year = models.IntegerField()
    expire = models.BooleanField(default=False)
    days = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Duration of the leave allocation")
    description = models.CharField(max_length=1000, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)


class PunchTime(models.Model):
    worker = models.ForeignKey(Labour, on_delete=models.PROTECT)
    in_time = models.DateTimeField(null=True, blank=True,)
    out_time = models.DateTimeField(null=True, blank=True,)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)


class AcademicQualification(models.Model):
    name = models.CharField(max_length=200, verbose_name="Academic name")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
