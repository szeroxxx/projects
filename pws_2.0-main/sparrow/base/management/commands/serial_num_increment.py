# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from inventory.models import ProductTracking
import time
from datetime import timedelta
from tenant_schemas.utils import schema_context
from django.db.models import Count


class Command(BaseCommand):
    help = "Wurth price insert."

    def handle(self, *args, **options):
        with schema_context("pcbpower"):
            start_time = time.time()
            #             Item.objects.values('group').annotate(
            #      type_count=models.Count("type")
            # ).filter(type_count__gt=1).order_by("-type_count")
            recordsTotal = ProductTracking.objects.annotate(type_count=Count("serial_num")).filter(type_count__gt=1).values("type_count", "serial_num").order_by("-type_count")
            print(recordsTotal, "recordsTotal")
            recordsTotal = recordsTotal
            start = 0
            length = 1000
            #

            print("==> Job starts")
            while True:
                serial_numbers = (
                    ProductTracking.objects.values("serial_num").annotate(type_count=Count("serial_num")).filter(type_count__gt=1).order_by("-type_count")[start : (start + length)]
                )
                print(serial_numbers, "serial_numbers")
                serial_number = []
                for num in serial_numbers:
                    serial_number.append(num["serial_num"])

                if len(serial_number) == 0:
                    break

                records = ProductTracking.objects.filter(serial_num__in=serial_number).values("serial_num", "id").order_by("serial_num")

                i = 0
                for record in records:
                    serial_num = record["serial_num"] + "_" + str(i)
                    print(serial_num, "serial_num")
                    ProductTracking.objects.filter(id=record["id"]).update(serial_num=serial_num)
                    i += 1

                print(serial_number, "serial_number")

                print(">> Processed index:", (start + length), "/", recordsTotal)
                start += length

            elapsed_time_secs = time.time() - start_time
            print("==> Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
            print("==> Job finished")
