import API from './axiosInstance';

export const checkInsurance = (cccd) => API.get(`/insurances/check/${cccd}`);
export const getAllInsurances = () => API.get('/insurances');
export const createInsurance = (data) => API.post('/insurances', data);
export const deleteInsurance = (id) => API.delete(`/insurances/${id}`);