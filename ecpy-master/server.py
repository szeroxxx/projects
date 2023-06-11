import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import os 

class App:
    ...

app = App()

def log_setup():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    log_handler = RotatingFileHandler(dir_path + '/log/app.log', maxBytes=100000, backupCount=3)
    formatter = logging.Formatter(
        '%(asctime)s process_name [%(process)d]: %(message)s',
        '%b %d %H:%M:%S')
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    log_setup()
    uvicorn.run("main:app", host="127.0.0.1", port=8081, log_level="debug")
