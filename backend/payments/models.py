from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ----- Requests -----
class CreateOrderIn(BaseModel):
    appointment_id: int
    ttl_seconds: Optional[int] = 900   # thời gian hết hạn VA (nếu bạn muốn)

# ----- Responses -----
class CreateOrderOut(BaseModel):
    payment_order_id: int
    order_code: str
    amount_vnd: int
    status: str
    va_number: Optional[str] = None
    qr_code_url: Optional[str] = None

class PaymentOrderOut(BaseModel):
    id: int
    order_code: str
    amount_vnd: int
    status: str
    paid_at: Optional[datetime] = None 
    va_number: Optional[str] = None
    qr_code_url: Optional[str] = None

class Bank_informayion(BaseModel):
    account_number: str
    bank_name :  str
    va : str