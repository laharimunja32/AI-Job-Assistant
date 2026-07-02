import api from './api';

export const healthService = {
  check: () => api.get<{ status?: string }>('/health'),
};
