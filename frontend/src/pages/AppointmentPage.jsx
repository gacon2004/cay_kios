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
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setError("");

    try {
      const token = localStorage.getItem("token"); // hoặc truyền trực tiếp nếu test
      const data = await createAppointment(formData, token);
      setResult(data);
    } catch (err) {
      setError(err.detail || "Lỗi không xác định");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
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

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>Thông tin cuộc hẹn</h3>
          <p>
            Bệnh viện: <strong>{result.clinic_name}</strong>
          </p>
          <p>
            Dịch vụ: <strong>{result.service_name}</strong> ({result.service_price}đ)
          </p>
          <p>
            Bác sĩ: <strong>{result.doctor_name}</strong>
          </p>
          <p>
            Số thứ tự: <strong>{result.queue_number}</strong>
          </p>
          <p>Thời gian: {new Date(result.appointment_time).toLocaleString()}</p>
          <img
            src={`data:image/png;base64,${result.qr_code}`}
            alt="QR Code"
            style={{ width: "200px", height: "200px", border: "1px solid #ccc" }}
          />
        </div>
      )}
    </div>
  );
};

export default AppointmentPage;
