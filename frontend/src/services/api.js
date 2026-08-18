import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const sendVoiceQuery = async (audioBlob) => {
  const formData = new FormData();
  formData.append('file', audioBlob, 'speech_input.wav');

  const response = await api.post('/api/voice-query', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const sendTextQuery = async (queryText, language = 'en') => {
  const response = await api.post('/api/query', {
    query: queryText,
    language: language,
  });
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const fetchMetrics = async () => {
  const response = await api.get('/api/metrics');
  return response.data;
};
