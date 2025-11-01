import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120_000,
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const defaultMessage = 'Something went wrong while talking to the backend.';
    const detail = error?.response?.data?.detail ?? defaultMessage;
    return Promise.reject(new Error(Array.isArray(detail) ? detail.join(', ') : detail));
  }
);

export const startSession = async ({ playerName }) => {
  const { data } = await client.post('/api/session/start', {
    player_name: playerName || null,
  });
  return data;
};

export const playRound = async (sessionId) => {
  const { data } = await client.post(`/api/session/${sessionId}/play-round`);
  return data;
};

export const captureExpression = async (sessionId) => {
  const { data } = await client.post(`/api/session/${sessionId}/final-expression`);
  return data;
};

export const fetchLogs = async () => {
  const { data } = await client.get('/api/logs');
  return data.sessions ?? [];
};


export const fetchPreviewStatus = async () => {
  const { data } = await client.get('/api/preview/status');
  return data;
};
export const fetchSessionStatus = async (sessionId) => {
  const { data } = await client.get(`/api/session/${sessionId}`);
  return data;
};

export { API_BASE_URL };
