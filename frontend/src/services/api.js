// frontend/src/services/api.js

import axios from 'axios';

// a. Define API base URL (reads from .env.local)
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// b. Create Axios instance
const apiClient = axios.create({
  baseURL: API_URL,
});

/*
// c. Add interceptor to include Auth token (GUTTED)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// d. Auth: Login user (GUTTED)
export async function loginUser(email, password) {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
}

// e. Auth: Signup user (GUTTED)
export async function signupUser(email, password, role) {
  const response = await apiClient.post('/auth/signup', { email, password, role });
  return response.data;
}
*/

// f. RAG Query
export async function queryRAG(user_question) {
  const response = await apiClient.post('/rag/rag_query', { user_question });
  return response.data;
}

// g. Chat: Post message (This signature is already correct)
export async function postChatMessage(message, history, session_id) {
  const response = await apiClient.post('/chat/message', { message, history, session_id });
  return response.data;
}

// h. Chat: Generate report (UPDATED)
export async function generateReport(history) {
  // We now send the full history object, not just a session_id
  const response = await apiClient.post('/chat/report', { history: history });
  return response.data;
}

// --- NEW: Task 3.3 ---
// j. Location: Find Nearby Hospitals
export async function findHospitals(latitude, longitude) {
  const response = await apiClient.post('/misc/find_hospitals', { latitude, longitude });
  return response.data; // This will be { hospitals: [...] }
}

// i. Export everything for use across the app (UPDATED)
export default {
  // loginUser, (GUTTED)
  // signupUser, (GUTTED)
  queryRAG,
  postChatMessage,
  generateReport,
  findHospitals, // 👈 NEW
};
