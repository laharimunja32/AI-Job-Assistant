import api from './api';
import type { Profile } from '@/types';

export const profileService = {
  get: () => api.get<Profile>('/profile'),

  update: (data: Partial<Profile>) => api.put<Profile>('/profile', data),

  delete: () => api.delete('/profile'),
};
