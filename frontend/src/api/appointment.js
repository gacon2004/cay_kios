import API from './axiosInstance';

export const createAppointment = (data) => API.post('/appointments', data);
export const getMyAppointments = () => API.get('/appointments/me');
