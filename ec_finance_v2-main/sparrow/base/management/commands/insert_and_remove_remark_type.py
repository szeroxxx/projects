from django.core.management.base import BaseCommand
from django.db import transaction
import json
from base.models import CommentType,Remark
from attachment.models import FileType
from qualityapp.models import Order_Attachment
class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                id = [11,13,17,20,12]
                Remark.objects.filter(comment_type_id__in=id).delete()
                CommentType.objects.filter(id__in=id).delete()
                remarks_types = [
                    {
                        'name': 'Re-Preparation Remarks',
                        'code': 'RE_Preparation_remarks',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'PreSI2 Remarks',
                        'code': 'PreSI_2_Remarks',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'Delay Remarks',
                        'code': 'Delay_Remarks',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'Back Production Remarks',
                        'code': 'Back_Production_Remarks',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'PreSI Remarks',
                        'code': 'PreSI_Remarks',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'Sales Change By CSIL',
                        'code': 'Sales_Change_BY_CSIL',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'FQC Multi Remarks',
                        'code': 'FQC_multi_Remarks',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'Internal CAM Remarks',
                        'code': 'Internal_CAM_Remarks',
                        'is_active': True,
                        'created_by': 1
                        },
                        {
                        'name': 'CSIL Remarks',
                        'code': 'CSIL_Remarks',
                        'is_active': True,
                        'created_by': 1
                        },

                        {
                        'name': 'Sales Change Request',
                        'code': 'Sales_Change_Request',
                        'is_active': True,
                        'created_by': 1
                        },

                        {
                        'name': 'NCFQC',
                        'code': 'NCFQC',
                        'is_active': True,
                        'created_by': 1
                        }
                ]
                bulk = []
                for i in remarks_types:
                    bulk.append(CommentType(name=i["name"],code=i["code"],is_active=True,created_by_id=1))
                CommentType.objects.bulk_create(bulk)
                # Order_Attachment.objects.filter(file_type__code = "EXCEPTION_HALF_PREPARED").delete()
                # need to delete type from FileType table
        except Exception as e:
            print(e)
