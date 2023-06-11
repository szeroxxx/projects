import core

def get_top_ten_customers():
    data = core.execute_query("select top 10 * from genSearchCustomer")
    return {"customers": data}


def update_customer(user_id, name):

    result = core.execute_nonquery("update genSearchCustomer set lastName = '{}' where userid = {}".format(name,user_id))
    if result == True:
        return {"result": "success"}
    else:
        return {"result": "error"}
    