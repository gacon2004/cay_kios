import API from './axiosInstance';

export const getMyProfile = () => API.get('/patients/me');
export const getAllPatients = () => API.get('/patients');
export const getPatientById = (id) => API.get(`/patients/${id}`);
export const updatePatient = (id, data) => API.put(`/patients/${id}`, data);
