import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const createAppointment = async (data, token) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/appointments/`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Unknown error" };
  }
};
