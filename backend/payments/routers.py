from fastapi import APIRouter, HTTPException, Header, Request, Depends
from .models import CreateOrderIn, CreateOrderOut, PaymentOrderOut
from backend.auth.providers.partient_provider import PatientProvider, AuthUser
from .controllers import (
    create_payment_order,
    get_payment_order_by_code,
    verify_webhook_auth,
    handle_sepay_webhook,
)

auth_patient_handler = PatientProvider()

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/orders", response_model=CreateOrderOut)
async def create_order(
    payload: CreateOrderIn,
    current_user: AuthUser = Depends(auth_patient_handler.get_current_patient_user),
):
    # truyền id bệnh nhân hiện tại xuống controller
    return await create_payment_order(
        appointment_id=payload.appointment_id,
        ttl_seconds=payload.ttl_seconds,
        patient_id=current_user["id"],
    )

@router.get("/orders/{order_code}", response_model=PaymentOrderOut)
def get_order(
    order_code: str,
    current_user: AuthUser = Depends(auth_patient_handler.get_current_patient_user),
):
    data = get_payment_order_by_code(
        order_code=order_code,
        patient_id=current_user["id"],
    )
    if not data:
        raise HTTPException(status_code=404, detail="Order not found")
    return data

# Webhook từ SePay (money-in)
@router.post("/webhooks/sepay")
async def sepay_webhook(request: Request, Authorization: str = Header(None)):
    verify_webhook_auth(Authorization)
    payload = await request.json()
    return handle_sepay_webhook(payload)
