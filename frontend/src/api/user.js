import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const getAllUsers = async () => {
  const res = await axios.get(`${API_BASE}/v1/users`);
  return res.data;
};
