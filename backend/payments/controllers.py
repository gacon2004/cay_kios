import os, time, secrets, json, httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from backend.database.connector import DatabaseConnector
import re

# ENV
SEPAY_BANK_ACCOUNT_ID = os.getenv("SEPAY_BANK_ACCOUNT_ID")
SEPAY_TOKEN = os.getenv("SEPAY_TOKEN")
SEPAY_WEBHOOK_SECRET = os.getenv("SEPAY_WEBHOOK_SECRET")

db = DatabaseConnector()

def _gen_order_code(appointment_id: int) -> str:
    # ví dụ: APPT-123-250812-AB12
    return f"APPT{appointment_id}{time.strftime('%y%m%d')}{secrets.token_hex(2).upper()}"

async def create_payment_order(appointment_id: int, ttl_seconds: Optional[int]) -> Dict[str, Any]:
    """
    Tạo 1 đơn thanh toán (VA theo đơn hàng) + gọi SePay trả VA/QR.
    """
    # 1) Lấy appointment + check tồn tại
    appt = db.query_get("""
        SELECT a.id, a.cur_price, a.patient_id, a.clinic_id, a.service_id
        FROM appointments a WHERE a.id=%s
    """, (appointment_id,))
    if not appt:
        raise HTTPException(404, "Appointment not found")
    appt = appt[0]

    # 2) Không cho tạo nếu đã có đơn chưa thanh toán
    exists = db.query_get("""
        SELECT id FROM payment_orders
        WHERE appointment_id=%s AND status IN ('PENDING','AWAITING') LIMIT 1
    """, (appointment_id,))
    if exists:
        raise HTTPException(400, "An unpaid payment order already exists")

    order_code = _gen_order_code(appointment_id)
    amount = int(appt["cur_price"])

    # 3) INSERT payment_orders (PENDING) và lấy id
    try:
        conn = db.get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO payment_orders
                      (appointment_id, patient_id, clinic_id, service_id,
                       order_code, amount_vnd, status, method, provider)
                    VALUES (%s,%s,%s,%s,%s,%s,'PENDING','VA','SEPAY')
                """, (appointment_id, appt["patient_id"], appt["clinic_id"],
                      appt["service_id"], order_code, amount))
                po_id = cur.lastrowid
            conn.commit()
    except Exception as e:
        raise HTTPException(500, f"DB error: {e}")

    bank_if = db.query_get("""
        SELECT a.account_number, a.bank_name, a.va
        FROM bank_information a
    """, ())
    if not bank_if:
        raise HTTPException(404, "bank information not found")
    bank_if = bank_if[0]

    account_number = bank_if["account_number"]
    bank_name = bank_if["bank_name"]
    va = bank_if["va"]

    qr_code_url = f"https://qr.sepay.vn/img?acc={account_number}&bank={bank_name}&amount={amount}&des={order_code}"


    # 5) Cập nhật đơn sang AWAITING + lưu VA/QR
    db.query_put("""
        UPDATE payment_orders
        SET status='AWAITING', sepay_order_id=%s, va_number=%s, qr_code_url=%s
        WHERE id=%s
    """, (appointment_id, va, qr_code_url, po_id))

    return {
        "payment_order_id": po_id,
        "order_code": order_code,
        "amount_vnd": amount,
        "status": "AWAITING",
        "va_number": va,
        "qr_code_url": qr_code_url,
    }

def get_payment_order_by_code(order_code: str) -> Optional[Dict[str, Any]]:
    rows = db.query_get("""
        SELECT id, order_code, amount_vnd, status, va_number, qr_code_url
        FROM payment_orders WHERE order_code=%s
    """, (order_code,))
    return rows[0] if rows else None

def _json_dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def verify_webhook_auth(Authorization: Optional[str]):
    print(f"Authorization header received: '{Authorization}'") # Thêm dòng này vào
    if not Authorization or not Authorization.lower().startswith("apikey "):
        raise HTTPException(401, "Missing Apikey")
    key = Authorization.split(" ", 1)[1]
    if key != SEPAY_WEBHOOK_SECRET:
        raise HTTPException(401, "Invalid Apikey")


def extract_order_code_from_content(content: str) -> Optional[str]:
    """
    Trích xuất mã đơn hàng (có dạng 'APPT...') từ chuỗi nội dung.
    """
    if not content:
        return None
    # Regex tìm chuỗi bắt đầu bằng 'APPT' và theo sau là chữ cái hoặc số
    pattern = r"APPT[A-Z0-9]+"
    match = re.search(pattern, content)
    if match:
        return match.group(0)
    return None

def handle_sepay_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Xử lý webhook biến động/VA: idempotent + map về payment_orders bằng code.
    """
    tx_id = payload.get("id")
    if tx_id is None:
        raise HTTPException(400, "Missing id")

    # 1) Idempotent
    existed = db.query_get("SELECT id FROM payment_events WHERE sepay_tx_id=%s", (tx_id,))
    if existed:
        return {"success": "da thanh toan"}

    code = payload.get("code")           # với VA theo đơn hàng = order_code
    amount = int(payload.get("transferAmount") or 0)
    ttype  = payload.get("transferType") # 'in'/'out'
    content = payload.get("content")
    ref = payload.get("referenceCode")
    order_code = extract_order_code_from_content(content)

    # 2) Lưu event trước (audit)
    db.query_put("""
        INSERT INTO payment_events (payment_order_id, sepay_tx_id, code, reference_code,
                transfer_amount, transfer_type, content, raw_payload)
        VALUES (Null, %s, %s, %s, %s, %s, %s, CAST(%s AS JSON))
    """, (tx_id, order_code, ref, amount, ttype, content, _json_dumps(payload)))

    # 3) Map về payment_orders và cập nhật trạng thái
    if ttype == "in":
        # Lock nhẹ bằng update có điều kiện trạng thái
        rows = db.query_get("""
            SELECT id, amount_vnd, status FROM payment_orders WHERE order_code=%s
        """, (order_code,))
        if rows:
            po = rows[0]
            if po["status"] in ("PENDING", "AWAITING"):
                if amount >= po["amount_vnd"]:
                    db.query_put("""
                        UPDATE payment_orders
                        SET status='PAID', paid_at=NOW()
                        WHERE id=%s
                    """, (po["id"],))
                elif 0 < amount < po["amount_vnd"]:
                    db.query_put("UPDATE payment_orders SET status='PARTIALLY' WHERE id=%s", (po["id"],))
    else:
        return {"success": "khong co code"}

    return {"success": True}
