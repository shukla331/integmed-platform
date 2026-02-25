import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type User = {
  id: string;
  name: string;
  mobile: string;
  email: string;
  system: string;
  qualification: string;
  specialization: string;
  role: string;
};

type AuthState = {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
  checkAuth: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      login: (user) =>
        set({
          user,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          user: null,
          isAuthenticated: false,
        }),

      checkAuth: () =>
        set((state) => ({
          user: state.user,
          isAuthenticated: Boolean(state.user),
        })),
    }),
    {
      name: 'auth-storage',
    }
  )
);
