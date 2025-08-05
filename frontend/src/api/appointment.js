// src/api/appointment.js
import axios from "axios";

const BASE_URL = "http://localhost:8000"; // sửa nếu cần

export const createAppointment = async (formData, token) => {
  try {
    const response = await axios.post(
      `${BASE_URL}/appointments`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`, // QUAN TRỌNG
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (error) {
    const detail =
      error.response?.data?.detail || "Lỗi kết nối hoặc không xác định";
    throw new Error(detail);
  }
};
