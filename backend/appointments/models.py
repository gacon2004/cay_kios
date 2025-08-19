from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

# BỆNH NHÂN CHỌN CA
class BookByShiftRequestModel(BaseModel):
    clinic_id: int
    service_id: int
    doctor_id: int
    schedule_id: Optional[int] = None
    has_insurances: bool = False  # online có thể truyền kèm

class AppointmentResponseModel(BaseModel):
    id: int
    patient_id: int
    clinic_id: int
    service_id: int
    doctor_id: int
    schedule_id: int
    queue_number: int          # STT toàn ngày (quầy)
    shift_number: int          # STT trong ca
    estimated_time: datetime   # giờ dự kiến vào khám
    printed: bool
    status: int                # 1=confirmed...
    booking_channel: str       # 'online' / 'offline'
    service_name: str
    service_price: float
    doctor_name: str
    clinic_name: str
    cur_price: float

class AppointmentStatusUpdateModel(BaseModel):
    status: int = Field(..., description="Trạng thái mới: 1=confirmed, 2=completed, 3=no_show, 4=canceled")
    
# --- MODEL MỚI: response hủy lịch ---
class AppointmentCancelResponse(BaseModel):
    pass

class AppointmentFilterModel(BaseModel):
    from_date: Optional[date] = Field(None, description="Ngày bắt đầu lọc")
    to_date: Optional[date] = Field(None, description="Ngày kết thúc lọc")
    status_filter: Optional[int] = Field(None, description="Lọc theo trạng thái (1=confirmed, 4=canceled,...)")
    limit: int = Field(100, ge=1, le=500, description="Số bản ghi tối đa")
    offset: int = Field(0, ge=0, description="Bỏ qua N bản ghi đầu")

class AppointmentPaymentFilterModel(BaseModel):
    # lọc theo ngày (optional)
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    # lọc theo trạng thái thanh toán (optional):
    # 'PAID' | 'AWAITING' | 'PENDING' | 'PARTIALLY' | 'UNPAID'
    pay_status: Optional[str] = Field(
        None,
        description="PAID|AWAITING|PENDING|PARTIALLY|UNPAID"
    )
    limit: int = Field(100, ge=1, le=500)
    offset: int = Field(0, ge=0)

class AppointmentPatientItem(BaseModel):
    appointment_id: int
    # --- Thông tin bệnh nhân ---
    patient_name: str
    patient_national_id: Optional[str] = None
    patient_dob: Optional[str] = None       # dd/mm/yyyy
    patient_gender: Optional[str] = None
    patient_phone: Optional[str] = None

    # --- Thông tin khám ---
    service_name: str
    clinic_name: str
    doctor_name: str
    shift_number: Optional[int] = None
    queue_number: Optional[int] = None
    price_vnd: int
    estimated_time: Optional[datetime] = None

    # --- Thanh toán ---
    pay_status: str              # PAID / AWAITING / PENDING / PARTIALLY / UNPAID
    paid_at: Optional[datetime] = None
    order_code: Optional[str] = None

    # tuỳ frontend muốn show QR hay không (nếu cần)
    qr_code: Optional[str] = None

class AppointmentAdminPaymentItem(BaseModel):
    appointment_id: int

    # --- Thông tin bệnh nhân ---
    patient_name: str
    patient_national_id: Optional[str] = None
    patient_dob: Optional[str] = None       # yyyy-mm-dd
    patient_gender: Optional[str] = None
    patient_phone: Optional[str] = None

    # --- Thông tin khám ---
    service_name: str
    clinic_name: str
    doctor_name: str
    shift_number: Optional[int] = None
    queue_number: Optional[int] = None
    price_vnd: int
    estimated_time: Optional[datetime] = None

    # --- Thanh toán ---
    pay_status: str  # PAID | AWAITING | PENDING | PARTIALLY | UNPAID
    paid_at: Optional[datetime] = None
    order_code: Optional[str] = None
