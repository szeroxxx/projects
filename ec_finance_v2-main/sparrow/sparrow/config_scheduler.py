import os
import sys

import requests
from sqlalchemy import create_engine
from sqlalchemy.sql import text

import settings

sys.path.append(os.path.join(os.path.abspath(__file__), "..", "settings"))


class ConfigDatabase:
    def __init__(self):
        db_config = settings.DATABASES["default"]
        self.engine = create_engine("postgresql://{}:{}@{}:{}/{}".format(db_config["USER"], db_config["PASSWORD"], db_config["HOST"], db_config["PORT"], db_config["NAME"]))

    def connect(self):
        return self.engine.connect()


class ConfigScheduler:
    def run_schedular():
        with ConfigDatabase().connect() as conn:
            client_schemas = conn.execute(text("select * from clients_client")).fetchall()
        for client_schema in client_schemas:
            try:
                data = {
                    "client_domain": "https://" + client_schema["domain_url"],
                }
                requests.request("POST", "https://" + client_schema["domain_url"] + "/base/start_schedulers/", data=data, verify=False)
            except requests.exceptions.ConnectionError:
                pass

    run_schedular()


ConfigScheduler()
