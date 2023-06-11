import datetime
import json

from accounts.models import Group, User, UserGroup, UserProfile
from attachment.models import FileType
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import views as base_views
from base.models import CommentType, Remark
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from qualityapp.models import Company, Operator
from xlrd import open_workbook


class Command(BaseCommand):
    def handle(request, self, *args, **options):
        try:
            with transaction.atomic():
                wb = open_workbook("C:\\Users\\admin\\Downloads\\localoperatorlist.xls")
                sheet = wb.sheets()[2]
                number_of_rows = sheet.nrows
                number_of_columns = sheet.ncols
                operator_list = []
                first_row = []
                for column in range(number_of_columns):
                    first_row.append(sheet.cell_value(0, column))
                operator_list = []
                for row in range(1, number_of_rows):
                    operator_dict = {}
                    for column in range(number_of_columns):
                        operator_dict[first_row[column]] = sheet.cell_value(row, column)
                    operator_list.append(operator_dict)
                group = Group.objects.filter(name='Raxit operator').values('id').first()
                company = Company.objects.filter(name='Raxit').values('id').first()
                try:
                    for x in operator_list:
                        password = make_password(x["Password"])
                        doj = x["DOJ"]
                        if doj:
                            doj = (doj - 25569) * 86400.0
                            doj = datetime.datetime.utcfromtimestamp(doj)
                        else:
                            doj = None
                        doc = x["DOC"]
                        if doc:
                            doc = (doc - 25569) * 86400.0
                            doc = datetime.datetime.utcfromtimestamp(doc)
                        else:
                            doc = None
                        dor = x["DOR"]
                        if dor:
                            dor = (dor - 25569) * 86400.0
                            dor = datetime.datetime.utcfromtimestamp(dor)
                        else:
                            dor = None
                        user = User.objects.create(first_name=x["First Name"], last_name=x["Last Name"], username=x["Operator Name"], email=x["Emailid"], password=password)
                        UserProfile.objects.create(user_id=user.id, user_type=1, partner_id=0, color_scheme=settings.DEFAULT_COLOR_SCHEME, ip_restriction=False)
                        UserGroup.objects.create(user_id=user.id, group_id=group["id"])
                        Operator.objects.create(user_id=user.id, company_ids=company["id"], operator_group=x["Group of User"], operator_type=x["Type of User"], is_active=True, shift=x["Shift"], permanent_shift=x["Permanent Shift"], show_own_records_only=True, doj=doj, doc=doc, dor=dor, remark=x["Remark"])
                        c_ip = base_views.get_client_ip(request)
                        action = AuditAction.INSERT
                        log_views.insert("qualityapp", "operator", [user.id], action, request.user.id, c_ip, "Operator has been created.")
                except Exception as e:
                    print(e, "errer", x)
        except Exception as e:
            print(e)
