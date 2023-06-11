import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

MSSQL_HOST = os.environ["MSSQL_HOST"]
SQL_PORT = os.environ["SQL_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
ECC_URL = os.environ["ECC_URL"]


def execution_timer_func(func):
    argnames = func.__code__.co_varnames[:func.__code__.co_argcount]

    def wrap_func(*args, **kwargs):
        arg = [entry for entry in args[:len(argnames)]]
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        if len(arg) > 1:
            user_id = arg[2]
            page_name = arg[1]
            executed_query = arg[0]
            execution_time = end_time - start_time
            username = arg[3]
            query = f"EXEC ECPY_Insert_API_log {user_id}, '{executed_query}', '{page_name}', '{execution_time}', '{username}'"
            execute_ec_api_log(query)
        return result
    return wrap_func


@execution_timer_func
def execute_query(sqlString, page, ec_user_id, ec_user):
    """
    Executes a select statement and  or stored procedure and returns the results.
    """
    try:

        conn_string = "mssql+pymssql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, MSSQL_HOST, DB_NAME)

        engine = create_engine(conn_string)

        result = ''
        with engine.connect() as conn:
            result = conn.execute(sqlString)
            result = result.fetchall()
        data = [dict(r) for r in result]
        return data

    except Exception as e:
        return "Error: " + str(e)


@execution_timer_func
def execute_raw_query(sqlString, page, ec_user_id, ec_user):
    """
    Executes multiple(nested) statements or stored procedure and returns the results.
    *note : execute_raw_query use when execute_query does not work.
    """
    sets = []
    conn_string = "mssql+pymssql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, MSSQL_HOST, DB_NAME)
    engine = create_engine(conn_string)
    connection = engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sqlString)
        while 1:
            names = [c[0] for c in cursor.description]
            set_ = []
            while 1:
                row_raw = cursor.fetchone()
                if row_raw is None:
                    break
                row = dict(zip(names, row_raw))
                set_.append(row)

            sets.append(list(set_))
            if cursor.nextset() is None:
                break
            if cursor.description is None:
                break
    except Exception as e:
        return "Error: " + str(e)
    finally:
        connection.close()
    return sets


@execution_timer_func
def execute_nonquery(sqlString, page, ec_user_id, ec_user):
    """
    Executes a non-select statement (insert, update, delete) or stored procedure and it's don't return any value.
    """
    conn_string = "mssql+pymssql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, MSSQL_HOST, DB_NAME)
    engine = create_engine(conn_string)
    connection = engine.raw_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlString)
            cursor.close()
            connection.commit()
        return True

    except Exception as e:
        return "Error: " + str(e)
    finally:
        connection.close()


def execute_return_query(sqlString, page, ec_user_id, ec_user):
    """
    Executes a non-select statement (insert, update, delete) or stored procedure and if the SP is returnable then returns the results.
    """
    conn_string = "mssql+pymssql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, MSSQL_HOST, DB_NAME)
    engine = create_engine(conn_string)
    connection = engine.raw_connection()
    result = ''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlString)
            result = cursor.fetchone()
            cursor.close()
            connection.commit()
        return result
    except Exception as e:
        return "Error: " + str(e)
    finally:
        connection.close()


def execute_ec_api_log(sqlString):
    """
    execute_ec_api_log is only for logging purpose
    """
    conn_string = "mssql+pymssql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, MSSQL_HOST, DB_NAME)
    engine = create_engine(conn_string)
    connection = engine.raw_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlString)
            cursor.close()
            connection.commit()
        return True
    except Exception as e:
        return "Error: " + str(e)
    finally:
        connection.close()
