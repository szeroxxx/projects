from pydantic import BaseModel
from typing import List


class CustomerCreditLimit(BaseModel):
    credit_limit : float
    base_credit_limit : float
    days : int
    customer_id : int
    invoice_date : str


class schedulePaymentReminder(BaseModel):
    items : List[dict] = []