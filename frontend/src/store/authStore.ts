import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/services';
import { storageGet, storageRemove, storageSet } from '@/utils/storage';

interface AuthState {
  isAuthenticated: boolean;
  email: string | null;
  fullName: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  setUserInfo: (email: string, fullName?: string | null) => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      email: null,
      fullName: null,

      hydrate: () => {
        const token = storageGet<string | null>('access_token', null);
        const email = storageGet<string | null>('user_email', null);
        const fullName = storageGet<string | null>('user_full_name', null);
        set({ isAuthenticated: !!token, email, fullName });
      },

      setUserInfo: (email, fullName) => {
        storageSet('user_email', email);
        if (fullName !== undefined) storageSet('user_full_name', fullName);
        set({ email, fullName: fullName ?? null });
      },

      login: async (email, password) => {
        const { data } = await authService.login(email, password);
        storageSet('access_token', data.access_token);
        storageSet('refresh_token', data.refresh_token);
        storageSet('user_email', email);
        set({ isAuthenticated: true, email });
      },

      register: async (email, password, fullName) => {
        const { data } = await authService.register(email, password, fullName);
        storageSet('user_email', data.email);
        if (data.full_name) storageSet('user_full_name', data.full_name);
        await useAuthStore.getState().login(email, password);
        set({ fullName: data.full_name });
      },

      logout: async () => {
        const refreshToken = storageGet<string | null>('refresh_token', null);
        try {
          if (refreshToken) await authService.logout(refreshToken);
        } catch {
          // proceed with local cleanup
        }
        storageRemove('access_token');
        storageRemove('refresh_token');
        storageRemove('user_email');
        storageRemove('user_full_name');
        set({ isAuthenticated: false, email: null, fullName: null });
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        email: state.email,
        fullName: state.fullName,
      }),
    },
  ),
);
