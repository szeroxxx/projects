from django.db import connection
from sqlalchemy import create_engine
import logging
from django.conf import settings

class DBEngine(object):    

    def __init__(self):
        db_config = settings.DATABASES['default']
        
        self.engine = create_engine("postgresql://{}:{}@{}:{}/{}".format(db_config['USER'],db_config['PASSWORD'],db_config['HOST'],db_config['PORT'],db_config['NAME']))    
    
    def connect(self):
        return self.engine.connect()

