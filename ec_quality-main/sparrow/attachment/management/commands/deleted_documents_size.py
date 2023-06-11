from django.core.management.base import BaseCommand
from tenant_schemas.utils import schema_context
from django.apps import apps
from django.conf import settings
import os
import time
from datetime import timedelta

# from attachment.models import Attachment


class Command(BaseCommand):
    help = "Get deleted document file size"

    def handle(self, *args, **options):
        with schema_context("eda"):
            modle_wise_size = []
            start_time = time.time()
            print("==> Job starts")
            data = []

            def index_data(app_name, model_name):

                attachment_model = apps.get_model(app_name, model_name)

                attachments = attachment_model.objects.filter(deleted=True)
                all_attachment_size = 0
                for attachment in attachments:
                    path = settings.MEDIA_ROOT + str(attachment.url)
                    if os.path.isfile(path):
                        all_attachment_size += attachment.size

                modle_wise_size.append(all_attachment_size / 1024)
                deleted_documents_size = 0
                for size in modle_wise_size:
                    deleted_documents_size += size
                data.append(deleted_documents_size)
                # print(deleted_documents_size, "MB")

            # def get_all_subclasses(cls):
            #     all_subclasses = []

            #     for subclass in cls.__subclasses__():
            #         all_subclasses.append(subclass)
            #         all_subclasses.extend(get_all_subclasses(subclass))

            #     for all_subclasse in all_subclasses:
            #         index_data(all_subclasse)
            #     return all_subclasses

            # get_all_subclasses(Attachment)
            index_data("base", "base_attachment")
            index_data("eda", "part_attachment")
            print(data[-1], "MB")
            elapsed_time_secs = time.time() - start_time
            print("==> Total Execution time: %s" % timedelta(seconds=round(elapsed_time_secs)))
            print("==> Job finished")
