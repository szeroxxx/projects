from azure.servicebus import ServiceBusClient, ServiceBusMessage
from finance_api.settings import QUEUE_NAME,CONNECTION_STR 
servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=False)


def send_single_message(sender,data):
    message = ServiceBusMessage(data)
    sender.send_messages(message)

def azure_service(data):
    with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            send_single_message(sender,data)
            # send_a_list_of_messages(sender)
            # send_batch_message(sender)


