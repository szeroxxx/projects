from waitress import serve
import logging
from logging.handlers import RotatingFileHandler
from sparrow.wsgi import application

import sys, os
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = os.getenv('LOG_FILE')

def log_setup():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    log_handler = RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=10)
    formatter = logging.Formatter(
        '%(asctime)s process_name [%(process)d]: %(message)s',
        '%b %d %H:%M:%S')
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    port = 8001
    IP = '127.0.0.1'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    #log_setup()
    logging.info('Starting server on port %s' % port)

    serve(application, host=IP, port=port)