from fastapi import APIRouter, HTTPException, Header, Request, Depends, status
from .models import CreateOrderIn, CreateOrderOut, PaymentOrderOut, Bank_informayion
from backend.auth.providers.partient_provider import PatientProvider, AuthUser
from backend.auth.providers.auth_providers import AuthProvider, AdminUser
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .controllers import (
    create_payment_order,
    get_payment_order_by_code,
    verify_webhook_auth,
    handle_sepay_webhook,
    update_bank_account,
    get_bank_information
)

auth_patient_handler = PatientProvider()
auth_user_handler = AuthProvider()

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

@router.put("/bank_information")
async def update_bank(
    bank_if : Bank_informayion,
    current_user: AdminUser = Depends(auth_user_handler.get_current_admin_user)
    ):
    return update_bank_account(bank_if)

@router.get("/bank_information", response_model=Bank_informayion)
async def get_bank(
    current_user: AdminUser = Depends(auth_user_handler.get_current_admin_user)
    ):
    bank = get_bank_information()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(bank))