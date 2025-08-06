// src/api/appointment.js
import axios from "axios";

const BASE_URL = "http://localhost:8000"; // sửa nếu cần

// file: ../api/appointment.js

export const createAppointment = async (formData, token, hasInsurance) => {
  const url = `http://localhost:8000/appointments?insurances=${hasInsurance}`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      clinic_id: formData.clinic_id,
      service_id: formData.service_id,
      doctor_id: formData.doctor_id,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    // Ném lỗi chi tiết từ server
    throw new Error(JSON.stringify(errorData, null, 2) || "Lỗi không xác định từ server");
  }

  return response.json();
};