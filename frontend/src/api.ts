import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  getMe: async () => {
    const response = await api.get('/api/me');
    return response.data;
  },
  login: async (credentials: any) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  register: async (credentials: any) => {
    const response = await api.post('/auth/register', credentials);
    return response.data;
  },
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  }
};

export const userAPI = {
  linkHandle: async (codeforcesHandle: string) => {
    const response = await api.post('/api/handle', { codeforcesHandle });
    return response.data;
  }
};

export const roadmapAPI = {
  getRoadmap: async () => {
    const response = await api.get('/api/roadmap');
    return response.data;
  },
  getRecommendation: async () => {
    const response = await api.post('/api/recommend');
    return response.data;
  },
  submitFeedback: async (topic: string, result: 'pass' | 'fail', problemId: string) => {
    const response = await api.post('/api/feedback', { topic, result, problemId });
    return response.data;
  }
};
