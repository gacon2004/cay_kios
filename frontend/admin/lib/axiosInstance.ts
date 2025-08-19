import axios from "axios";

const baseURL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://web-production-ad4be.up.railway.app";

const instance = axios.create({
  baseURL,
  timeout: 20000,
  withCredentials: true,
  headers: {
    common: {
      Authorization: undefined,
    },
  },
  maxRedirects: 5,
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
    const currentPath =
      typeof window !== "undefined" ? window.location.pathname : "";

    // Xử lý chuyển hướng 307
    if (
      error.response?.status === 307 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      console.log("Detected 307 redirect, retrying with Authorization...");
      originalRequest._retry = true; // Đánh dấu để tránh vòng lặp vô hạn
      const token = localStorage.getItem("token");
      if (token) {
        originalRequest.headers.Authorization = `Bearer ${token}`;
      }
      return instance(originalRequest);
    }

    // Xử lý lỗi 401, nhưng không chuyển hướng nếu đang ở /admin/login hoặc /admin/register
    if (
      error.response?.status === 401 &&
      !currentPath.startsWith("/admin/login") &&
      !currentPath.startsWith("/admin/register")
    ) {
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
