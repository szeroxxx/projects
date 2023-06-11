from django.core.management.base import BaseCommand

from base.factory import factory_view


class Command(BaseCommand):
    help = "Create new schema for demo data."

    def add_arguments(self, parser):
        parser.add_argument("--domain_url")
        parser.add_argument("--schema_name")
        parser.add_argument("--demo_data")

    def handle(self, *args, **options):
        # domain_url = options["domain_url"]
        # schema_name = options["schema_name"]
        # demo_data = options["demo_data"]
        factory_view.init_database(None, None, True)
