import base64
from datetime import datetime


class Util(object):

    @staticmethod
    def encrypt_data(data):
        return base64.b64encode(data.encode())

    @staticmethod
    def decrypt_data(data):
        return base64.b64decode(data).decode()

    @staticmethod
    def ticks(dt):
        return (dt - datetime(1, 1, 1)).total_seconds() * 10000000
