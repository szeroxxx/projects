import datetime
import json
import threading

import requests
from django.conf import settings


class HawkEventCode:
    # SCHUKAT_PRICE_API = "vcschprapi"
    MOUSER_PRICE_API = "vcmoprapi"
    ARROW_PRICE_API = "vcarrowprapi"
    E14_PRICE_API = "vce14prapi"
    TME_PRICE_API = "vctmeprapi"
    WURTH_STOCK_API = "vcwurprapi"
    SUPPLIER_PRICE_API = "vcprinapi"
    DIGIKEY_PRICE_API = "vcdigprapi"
    DIGIKEY_TOEKN_RENEW = "vcdigitoke"
    REORDER_LEVEL_NOTIFICAITON = "eclwstocks"
    ASSEMBLY_ORDER_PRIORITY = "ecmopriori"
    MYCRONIC_PART_PROCESSED_API = "ecmycprocessed"
    VCDB_PART_SYNC_EC_SPARROW = "ecsyncvcprt"
    INTELLIAL = "intellialcom"
    EUROCIRCUITS = "eccom"
    BE_EUROCIRCUITS = "beeuro"
    ISPL_EVENT = "ispltest"
    DATASHEET_PDF_TO_IMG_CLEAN = "vcddtpd2img"
    VDDB_REMOVE_PRICE_LOG = "vcdbrmpls"
    VCDB_EC_STOCK_UPDATE = "vcdbesfrmespw"
    EDA_PART_SYNC_FAIL = "ecspwpartsync"
    EDA_PART_SYNC_FAIL_ERR = "ecspwpartsyncerr"
    QUEUE_SHIPMENT_DATE = "ecqueueshipdate"
    SOS_PRICE_API = "vcsosprapi"
    SOS_TOKEN_GENERATE = "vcsostoke"
    DISTRELEC_PRICE_API = "vcdistrpriapi"


class HawkEventStatus:
    OK = "ok"
    ERROR = "error"


class HawkLogger:
    def __init__(self, event_start_time, event_end_time):
        self.event_start_time = event_start_time
        self.event_end_time = event_end_time

    def hawk_log_event_func(self, event_code, status, message, c_ip, event_duration):
        event_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        url = settings.HAWK_LOG_ENDPOINT + "hawk/insert_event_logs/"
        data = {"event_ip": c_ip, "event_code": event_code, "event_time": event_time, "event_status": status, "message": {"desc": message}, "event_duration": event_duration}
        headers = {"Content-Type": "application/json"}
        requests.request("POST", url, headers=headers, data=json.dumps(data))

    def hawk_log_event(self, event_code, status, message, c_ip):
        event_duration = int((self.event_end_time - self.event_start_time) * 1000)
        thread = threading.Thread(target=HawkLogger.hawk_log_event_func, args=(self, event_code, status, message, c_ip, event_duration,))
        thread.start()
