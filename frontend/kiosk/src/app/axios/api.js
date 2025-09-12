import axios from 'axios';

// Lấy token từ localStorage hoặc sessionStorage
function getToken() {
    return (
        localStorage.getItem('access_token') ||
        sessionStorage.getItem('access_token')
    );
}

const baseURL =
    process.env.NEXT_PUBLIC_API_BASE_URL || 'http://157.66.27.214/api';

const api = axios.create({
    baseURL,
    withCredentials: true,
    headers: {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json',
    },
});

// Thêm interceptor để tự động gắn Bearer token vào mỗi request
api.interceptors.request.use(
    config => {
        const token = getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

export default api;
