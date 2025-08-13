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
    qr_code: Optional[str] = None

# --- MODEL MỚI: response hủy lịch ---
class AppointmentCancelResponse(BaseModel):
    pass

class AppointmentFilterModel(BaseModel):
    from_date: Optional[date] = Field(None, description="Ngày bắt đầu lọc")
    to_date: Optional[date] = Field(None, description="Ngày kết thúc lọc")
    status_filter: Optional[int] = Field(None, description="Lọc theo trạng thái (1=confirmed, 4=canceled,...)")
    limit: int = Field(100, ge=1, le=500, description="Số bản ghi tối đa")
    offset: int = Field(0, ge=0, description="Bỏ qua N bản ghi đầu")