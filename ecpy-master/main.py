import logging
from typing import Union

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

import api_security
import customers
from api_security import User
from finance.invoicing import finance
from sales.customers import customer
from sales.invoicing import invoicing
from vcdb.mpn import vcdb

from pws.orders import pws


app = api_security.app

app.include_router(vcdb, prefix="/ecpy/vcdb", dependencies=[Depends(api_security.get_current_active_user)])
app.include_router(finance, prefix="/ecpy/finance", dependencies=[Depends(api_security.get_current_active_user)])
app.include_router(customer, prefix="/ecpy/sales", dependencies=[Depends(api_security.get_current_active_user)])
app.include_router(invoicing, prefix="/ecpy/sales", dependencies=[Depends(api_security.get_current_active_user)])
app.include_router(pws, prefix="/ecpy/pws", dependencies=[Depends(api_security.get_current_active_user)])
