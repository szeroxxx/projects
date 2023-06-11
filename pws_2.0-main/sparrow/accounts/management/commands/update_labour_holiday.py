import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from exception_log import manager
from hrm.models import LeaveAllocation
from tenant_schemas.utils import schema_context

# from production.models import LabourHoliday

class Command(BaseCommand):
	help = 'Generate user profile image.'

	def handle(self, *args, **options):
		with schema_context('ec'):

			try:
				labourholidays = LabourHoliday.objects.filter().values('worker_id', 'leave_type_id')

				for labourholiday in labourholidays:
					leave_allocation_ids = LeaveAllocation.objects.filter(worker_id = labourholiday['worker_id'], leave_type_id = labourholiday['leave_type_id']).values('id')
					if leave_allocation_ids:
						leave_allocation_id = leave_allocation_ids.first()['id']
						labour_holiday = LabourHoliday.objects.filter(worker_id = labourholiday['worker_id'], leave_type_id = labourholiday['leave_type_id']).update(leave_allocation_id = leave_allocation_id)

			except Exception as e:
				manager.create_from_exception(e)
				logging.exception('Something went wrong.')
