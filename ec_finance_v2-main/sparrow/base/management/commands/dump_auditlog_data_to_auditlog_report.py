# -*- coding: utf-8 -*-
from auditlog.models import AuditReportLog, Auditlog
from django.core.management.base import BaseCommand
from tenant_schemas.utils import schema_context
import re
import time


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        with schema_context("eda"):
            start = 0
            length = 1000
            count = 0
            recordsTotal = (
                Auditlog.objects.filter(descr__contains="Spec workspace:")
                .values("content_type_id", "id", "action_by__username", "ip_addr", "action__name", "descr", "action_on", "object_id")
                .count()
            )
            status = {
                "New": "new",
                "Pending": "pending",
                "In progress": "in_progress",
                "Cross checked": "cross_checked",
                "In verification": "in_verification",
                "Finished": "finished",
                "Exception": "exception",
            }
            while True:
                auditlog_data = (
                    Auditlog.objects.filter(descr__contains="Spec workspace:")
                    .values("id", "content_type_id", "action_by", "ip_addr", "action", "descr", "action_on", "object_id")
                    .order_by("id")[start : (start + length)]
                )
                for data in auditlog_data:
                    # print(data, "data")
                    count += 1
                    result = re.search("<b>(.*)</b>", data["descr"])
                    # print(result.group(1), result)
                    status_code = status[result.group(1)]
                    print(status_code, "status_code", data["action_on"])
                    AuditReportLog.objects.create(
                        id=data["id"],
                        action_by_id=data["action_by"],
                        ip_addr=data["ip_addr"],
                        action_id=data["action"],
                        descr=data["descr"],
                        action_on=data["action_on"],
                        object_id=data["object_id"],
                        group="specification",
                        status_code=status_code,
                        content_type_id=data["content_type_id"],
                    )
                    print(f"count is {count}")

                time.sleep(1)
                start += length
            print("==> Specs update finished")
