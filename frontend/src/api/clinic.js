import API from './axiosInstance';

export const getAllClinics = () => API.get('/clinics');
export const getClinicById = (id) => API.get(`/clinics/${id}`);
export const createClinic = (data) => API.post('/clinics', data);
export const updateClinic = (id, data) => API.put(`/clinics/${id}`, data);
export const deleteClinic = (id) => API.delete(`/clinics/${id}`);
export const getClinicsByService = (serviceId) =>
  API.get(`/clinics/by-service/${serviceId}`);
