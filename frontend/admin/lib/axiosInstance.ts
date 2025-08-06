import axios from "axios";

const instance = axios.create({
  baseURL: "https://caykios-production.up.railway.app/",
  timeout: 20000,
  withCredentials: true,
  headers: {
    common: {
      Authorization: undefined,
    },
  },
  maxRedirects: 5, // Cho phép tối đa 5 lần chuyển hướng
});

// Interceptor cho request để thêm token
instance.interceptors.request.use(
  (config) => {
    config.headers = config.headers || {};
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        delete config.headers.Authorization;
        console.log("Không tìm thấy token, đã xóa header Authorization");
      }
    }
    return config;
  },
  (error) => {
    console.error("Lỗi Interceptor Request:", error);
    return Promise.reject(error);
  }
);

// Interceptor cho response để xử lý lỗi và chuyển hướng
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 307 && originalRequest) {
      console.log("Detected 307 redirect, retrying with Authorization...");
      const token = localStorage.getItem("token");
      if (token) {
        originalRequest.headers.Authorization = `Bearer ${token}`;
      }
      return instance(originalRequest); // Gửi lại yêu cầu với header
    }
    if (error.response?.status === 401) {
      console.log("401 Unauthorized, xóa token và chuyển hướng");
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        window.location.href = "/admin/login";
      }
    }
    return Promise.reject(error);
  }
);

export default instance;
