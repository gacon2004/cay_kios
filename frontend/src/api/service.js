import API from './axiosInstance';

export const getAllServices = () => API.get('/services');
export const getServiceById = (id) => API.get(`/services/${id}`);
export const createService = (data) => API.post('/services', data);
export const updateService = (id, data) => API.put(`/services/${id}`, data);
export const deleteService = (id) => API.delete(`/services/${id}`);
export const getServicesWithClinicsDoctors = () => API.get('/services/with-clinics-doctors');
