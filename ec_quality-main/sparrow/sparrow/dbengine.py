from django.conf import settings
from django.contrib.postgres.indexes import BTreeIndex
# from elasticsearch import Elasticsearch
from sqlalchemy import create_engine


class DBEngine(object):
    def __init__(self):
        db_config = settings.DATABASES["default"]

        self.engine = create_engine("postgresql://{}:{}@{}:{}/{}".format(db_config["USER"], db_config["PASSWORD"], db_config["HOST"], db_config["PORT"], db_config["NAME"]))

    def connect(self):
        return self.engine.connect()

class DBEngineSql(object):
    def __init__(self):
        db_config = settings.DATABASES["secondary"]
        self.engine = create_engine("sqlite:///" + db_config["NAME"])

    def connect(self):
        return self.engine.connect()


class UpperBtreeIndex(BTreeIndex):
    def create_sql(self, model, schema_editor, using=""):
        statement = super().create_sql(model, schema_editor, using=using)
        quote_name = statement.parts["columns"].quote_name

        def upper_quoted(column):
            return f"UPPER({quote_name(column)})"

        statement.parts["columns"].quote_name = upper_quoted
        return statement
