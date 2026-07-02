import api from './api';
import type { TokenResponse, User } from '@/types';

export const authService = {
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),

  register: (email: string, password: string, full_name?: string) =>
    api.post<User>('/auth/register', { email, password, full_name }),

  refresh: (refresh_token: string) =>
    api.post<TokenResponse>('/auth/refresh', { refresh_token }),

  logout: (refresh_token: string) =>
    api.post('/auth/logout', { refresh_token }),
};
