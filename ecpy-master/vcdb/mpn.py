
from fastapi import APIRouter,Request
import core

vcdb = APIRouter()


@vcdb.get("/get_part_for_auto_reserve/")
def get_parts_for_auto_reserve():
    try:
        data = core.execute_query("get_parts_for_Auto_reserve", "GET_PARTS_FOR_AUTO_RESERVE", 0, "sparrow")
        return data
    except Exception as e:
        return {"error": str(e)}


@vcdb.get("/get_count_of_unidetified_parts/")
async def get_count_of_unidetified_parts(request:Request):
    try:
        data = await request.json()
        para_date = data["parameter_date"]
        query = f"EXEC GET_Unidentified_Parts_Count '{para_date}'"
        response = core.execute_query(query, "GET_UNIDETIFIED_PARTS_COUNT", 0, "sparrow")
        return {"data" : response}
    except Exception as e:
        return {"error": str(e)}


@vcdb.get("/get_unidentified_parts/")
def get_unidentified_parts():
    try:
        data = core.execute_query("getunidentifiedparts", "GET_UNIDENTIFIED_PARTS", 0, "sparrow")
        return data
    except Exception as e:
        return {"error": str(e)}

@vcdb.get("/remove_unidentified_parts_from_queue/")
async def remove_unidentified_parts_from_queue(request:Request):
    try:
        data = await request.json()
        para_date = data["ids"]
        query = f"EXEC removeUnidentifiedPartsFromQueue '{para_date}'"
        response = core.execute_nonquery(query, "REMOVE_UNIDENTIFIED_PARTS_FROM_QUEUE", 0, "sparrow")
        return {"data" : response}
    except Exception as e:
        return {"error": str(e)}