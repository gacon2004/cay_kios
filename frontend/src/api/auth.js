import API from './axiosInstance';

export const loginByCCCD = (cccd) =>
  API.post('/auth/patient/login', { national_id: cccd });

export const registerPatient = (data) =>
  API.post('/auth/patient/register', data);

export const refreshToken = () =>
  API.post('/auth/patient/refresh-token');
