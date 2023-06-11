from pydantic import BaseModel


class PrintingNeeds(BaseModel):
    country: str
    region: str
    orders: int
    months: int
    limit: int
    customer_name: str
    included_steam: str
    log_data: dict
