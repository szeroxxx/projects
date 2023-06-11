from django.core.management.base import BaseCommand
from django.db.models import Q, Count, IntegerField, When
from production.models import AssemblyPrepOrderRel, AssemblyPrepStep
from tenant_schemas.utils import schema_context


class Command(BaseCommand):
    help = "Update preparation status finish if all 4 preparation status completed."

    def handle(self, *args, **options):
        with schema_context("ec"):
            prep_step = AssemblyPrepStep.objects.get(code="finish_all_prep")
            mfg_order_ids = list(AssemblyPrepOrderRel.objects.filter(assembly_prep_step__code="finish_all_prep").values_list("mfg_order_id", flat=True))
            print(mfg_order_ids, "mfg_order_ids")
            finished_perparations = (
                AssemblyPrepOrderRel.objects.exclude(mfg_order_id__in=mfg_order_ids)
                .values("mfg_order_id")
                .annotate(count=Count("assembly_prep_step"), finished=Count("id", filter=Q(status="completed")))
            )
            print(finished_perparations, "finished_perparations")
            # total_preparations = (
            #     AssemblyPrepOrderRel.objects.filter(mfg_order_id__in=mfg_order_ids)
            #     .exculde(assembly_prep_step__code="finish_all_prep")
            #     .values("mfg_order_id")
            #     .annotate(count=Count("status"))
            # )
            for data in finished_perparations:
                print(data["count"], data["finished"], data["mfg_order_id"])
                if data["count"] == data["finished"]:
                    check_finish_prep = AssemblyPrepOrderRel.objects.filter(mfg_order_id=data["mfg_order_id"], status="finished", assembly_prep_step=prep_step)
                    print(check_finish_prep, "check_finish_prep")
                    if not check_finish_prep:
                        print("00000")
                        AssemblyPrepOrderRel.objects.create(mfg_order_id=data["mfg_order_id"], assembly_prep_step=prep_step, status="finished")
            print("Script finished")
