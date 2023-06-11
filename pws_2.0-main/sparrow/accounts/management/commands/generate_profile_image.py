from django.core.management.base import BaseCommand
from django.conf import settings
from accounts import profile_image_generator
from accounts.models import UserProfile
from tenant_schemas.utils import schema_context
import logging
from exception_log import manager

class Command(BaseCommand):
	help = 'Generate user profile image.'

	def handle(self, *args, **options):
		with schema_context('demo'):
			users = UserProfile.objects.filter(is_deleted = False).values('id', 'user__first_name', 'user__last_name')
			for user in users:
				characters = user['user__first_name'][0].upper()+''+user['user__last_name'][0].upper() if user['user__last_name'] else user['user__first_name'][0].upper()
				profile_image = profile_image_generator.GenerateCharacters(characters, user['id'])
				user_profile = UserProfile.objects.filter(id = user['id']).first()
				user_profile.profile_image = profile_image
				user_profile.save()