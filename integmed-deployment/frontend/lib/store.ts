/**
 * Global Auth Store using Zustand
 */
import { create } from 'zustand';
import Cookies from 'js-cookie';

interface User {
  id: string;
  name: string;
  mobile: string;
  email?: string;
  system: 'allopathy' | 'ayurveda' | 'homeopathy' | 'unani';
  role: 'doctor' | 'nurse' | 'admin';
  hpr_id?: string;
  qualification?: string;
  specialization?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => set({ user, isAuthenticated: !!user, isLoading: false }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  logout: () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    Cookies.remove('user');
    set({ user: null, isAuthenticated: false });
  },
  
  checkAuth: () => {
    const token = Cookies.get('access_token');
    const userCookie = Cookies.get('user');
    
    if (token && userCookie) {
      try {
        const user = JSON.parse(userCookie);
        set({ user, isAuthenticated: true, isLoading: false });
      } catch (e) {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
