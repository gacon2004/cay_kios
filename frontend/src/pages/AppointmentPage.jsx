import React, { useState } from "react";
import { createAppointment } from "../api/appointment";

const AppointmentPage = () => {
  const [formData, setFormData] = useState({
    clinic_id: "",
    service_id: "",
    doctor_id: "",
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setError("");

    const token = localStorage.getItem("token");
    if (!token) {
      setError("Bạn chưa đăng nhập.");
      return;
    }

    try {
      const data = await createAppointment(formData, token);
      setResult(data);
    } catch (err) {
      console.error("Lỗi phía server:", err.message);
      setError(err.message || "Lỗi không xác định");
    }
  };

  const handlePrint = async (appointmentId) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `http://localhost:8000/appointments/${appointmentId}/print`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Không thể tạo PDF.");
      }

      const blob = await response.blob();
      const fileURL = URL.createObjectURL(blob);
      window.open(fileURL, "_blank");
    } catch (error) {
      alert("Lỗi khi in phiếu: " + error.message);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "700px", margin: "auto" }}>
      <h2>Đặt lịch khám</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Clinic ID:</label>
          <input
            name="clinic_id"
            value={formData.clinic_id}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Service ID:</label>
          <input
            name="service_id"
            value={formData.service_id}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Doctor ID:</label>
          <input
            name="doctor_id"
            value={formData.doctor_id}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit">Tạo phiếu</button>
      </form>

      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

      {result && (
        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "10px",
          }}
        >
          <h3 style={{ textAlign: "center" }}>Hoàn Thành Đăng Ký</h3>
          <p style={{ textAlign: "center" }}>
            Kiểm tra thông tin và in phiếu khám
          </p>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              backgroundColor: "#f5f5f5",
              padding: "15px",
              borderRadius: "10px",
            }}
          >
            <div>
              <h4>Thông Tin Bệnh Nhân</h4>
              <p>Họ tên: {result.patient_name}</p>
              <p>CCCD: {result.national_id}</p>
              <p>Ngày sinh: {result.date_of_birth}</p>
              <p>Giới tính: {result.gender}</p>
              <p>SDT: {result.phone}</p>
            </div>
            <div>
              <h4>Thông Tin Khám</h4>
              <p>Dịch vụ: {result.service_name}</p>
              <p>Phòng: {result.room_name || "Phòng 104"}</p>
              <p>Bác sĩ: {result.doctor_name}</p>
              <p>Số thứ tự: {result.queue_number}</p>
              <p>
                Thời gian: {new Date(result.appointment_time).toLocaleString("vi-VN")}
              </p>
            </div>
          </div>

          <div style={{ textAlign: "center", marginTop: "20px" }}>
            <p>Mã QR để check-in</p>
            <img
              src={`data:image/png;base64,${result.qr_code}`}
              alt="QR Code"
              style={{ width: "200px", height: "200px" }}
            />
            <div style={{ marginTop: "20px" }}>
              <button
                onClick={() => handlePrint(result.id)}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                }}
              >
                In Phiếu Khám
              </button>
            </div>
          </div>

          <div
            style={{
              backgroundColor: "#fff3cd",
              padding: "10px",
              borderRadius: "8px",
              marginTop: "20px",
            }}
          >
            <p><strong>Hướng dẫn:</strong></p>
            <ul>
              <li>Vui lòng đến phòng khám đúng giờ hẹn</li>
              <li>Mang theo phiếu khám và giấy tờ tùy thân</li>
              <li>Liên hệ tổng đài nếu cần hỗ trợ</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppointmentPage;
