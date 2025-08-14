from fastapi import APIRouter, HTTPException, Header, Request
from .models import CreateOrderIn, CreateOrderOut, PaymentOrderOut
from .controllers import (
    create_payment_order,
    get_payment_order_by_code,
    verify_webhook_auth,
    handle_sepay_webhook,
)

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/orders", response_model=CreateOrderOut)
async def create_order(payload: CreateOrderIn):
    return await create_payment_order(payload.appointment_id, payload.ttl_seconds)

@router.get("/orders/{order_code}", response_model=PaymentOrderOut)
async def get_order(order_code: str):
    data = get_payment_order_by_code(order_code)
    if not data:
        raise HTTPException(404, "Order not found")
    return data

# Webhook từ SePay (money-in)
@router.post("/webhooks/sepay")
async def sepay_webhook(request: Request, authorapikey: str = Header(None)):
    
    payload = await request.json()
    return handle_sepay_webhook(payload)
