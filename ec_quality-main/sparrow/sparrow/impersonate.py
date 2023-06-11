from django.conf import settings
from win32 import win32security


class Impersonate:
    def __enter__(self):
        self.handel = win32security.LogonUser(settings.FILE_SERVER_USER, settings.FILE_SERVER_DOMAIN, settings.FILE_SERVER_PWD, 9, 3)
        win32security.ImpersonateLoggedOnUser(self.handel)

    def __exit__(self, type, value, traceback):
        win32security.RevertToSelf()
        self.handel.Close()
