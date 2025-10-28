// frontend/src/services/api.js

import axios from 'axios';

// a. Define API base URL (reads from .env.local)
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// b. Create Axios instance
const apiClient = axios.create({
  baseURL: API_URL,
});

// c. Add interceptor to include Auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// d. Auth: Login user
export async function loginUser(email, password) {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
}

// e. Auth: Signup user
export async function signupUser(email, password, role) {
  const response = await apiClient.post('/auth/signup', { email, password, role });
  return response.data;
}

// f. RAG Query
export async function queryRAG(user_question) {
  const response = await apiClient.post('/rag/rag_query', { user_question });
  return response.data;
}

// g. Chat: Post message
export async function postChatMessage(message, history, session_id) {
  const response = await apiClient.post('/chat/message', { message, history, session_id });
  return response.data;
}

// h. Chat: Generate report
export async function generateReport(session_id) {
  const response = await apiClient.post('/chat/report', { session_id });
  return response.data;
}

// i. Export everything for use across the app
export default {
  loginUser,
  signupUser,
  queryRAG,
  postChatMessage,
  generateReport,
};
