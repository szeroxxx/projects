from django.core.management.base import BaseCommand
import base64
import logging
import traceback
from django.conf import settings
from Crypto.Cipher import AES

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        try:
            # convert integer etc to string first
            password = str(options['password'])
            key = AES.new(settings.SCHEDULER_KEY[:32])
            password = (str(password) +(AES.block_size - len(str(password)) % AES.block_size) * "\0")
            print(base64.b64encode(key.encrypt(password)))
        except:
            logging.exception('Something went wrong.')