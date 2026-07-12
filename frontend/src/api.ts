import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_URL,
});

// Attach Bearer token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// H-3: Auto-logout on 401 responses (expired/invalid token)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Only redirect if we're not already on the login page
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  getMe: async () => {
    const response = await api.get('/api/me');
    return response.data;
  },
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  register: async (credentials: { email: string; password: string; username: string }) => {
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

export interface Recommendation {
  title: string;
  url: string;
  rating?: number;
  tags: string[];
  topic: string;
  rationale: string;
  problemId: string;
}

export const roadmapAPI = {
  getRoadmap: async () => {
    const response = await api.get('/api/roadmap');
    return response.data;
  },
  getRecommendation: async (): Promise<Recommendation> => {
    const response = await api.post('/api/recommend');
    return response.data;
  },
  submitFeedback: async (topic: string, result: 'pass' | 'fail', problemId: string) => {
    const response = await api.post('/api/feedback', { topic, result, problemId });
    return response.data;
  }
};
