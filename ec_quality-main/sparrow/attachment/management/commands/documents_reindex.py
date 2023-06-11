from django.core.management.base import BaseCommand
from tenant_schemas.utils import schema_context

from elasticsearch import Elasticsearch
from django.conf import settings
from attachment.document_service import Attachment as Document
from django.apps import apps

from django.db import connection


class Command(BaseCommand):
    help = "Reindex Mfg order attachment"

    def handle(self, *args, **options):
        with schema_context("eda"):

            def index_data(app_name, model_name):

                start = 0
                length = 1000

                attachment_model = apps.get_model(app_name, model_name)

                while True:
                    attachments = attachment_model.objects.filter(deleted=False)[start : (start + length)]
                    if len(attachments) == 0:
                        break
                    Document().insert(attachments, app_name=app_name, model_name=model_name)
                    start += length

            schema_name = "public"
            es = Elasticsearch([settings.ELASTIC_URL])

            if es.indices.exists(index=schema_name + "-attachment"):
                es.indices.delete(index=schema_name + "-attachment")

            index_data("base", "base_attachment")
            index_data("eda", "part_attachment")
