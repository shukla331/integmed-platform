/**
 * API Client for IntegMed Backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = Cookies.get('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try refresh
          const refreshToken = Cookies.get('refresh_token');
          if (refreshToken) {
            try {
              const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
                refresh_token: refreshToken,
              });
              const { access_token } = response.data;
              Cookies.set('access_token', access_token);
              
              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${access_token}`;
                return this.client.request(error.config);
              }
            } catch (refreshError) {
              // Refresh failed, logout
              Cookies.remove('access_token');
              Cookies.remove('refresh_token');
              window.location.href = '/login';
            }
          } else {
            // No refresh token, redirect to login
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async initDoctorAuth(mobile: string) {
    const response = await this.client.post('/auth/doctor/init', { mobile, purpose: 'login' });
    return response.data;
  }

  async verifyDoctorAuth(txnId: string, otp: string) {
    const response = await this.client.post('/auth/doctor/verify', { txn_id: txnId, otp });
    const { access_token, refresh_token, user } = response.data;
    
    // Store tokens in cookies
    Cookies.set('access_token', access_token, { expires: 1 }); // 1 day
    Cookies.set('refresh_token', refresh_token, { expires: 7 }); // 7 days
    
    return { user, access_token };
  }

  logout() {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    window.location.href = '/login';
  }

  // Patients
  async getPatient(patientId: string) {
    const response = await this.client.get(`/patients/${patientId}`);
    return response.data;
  }

  async createPatient(patientData: any) {
    const response = await this.client.post('/patients', patientData);
    return response.data;
  }

  // Encounters
  async createEncounter(encounterData: any) {
    const response = await this.client.post('/encounters', encounterData);
    return response.data;
  }

  async updateEncounter(encounterId: string, updateData: any) {
    const response = await this.client.patch(`/encounters/${encounterId}`, updateData);
    return response.data;
  }

  // Prescriptions
  async expandShorthand(shorthand: string) {
    const response = await this.client.post('/prescriptions/expand-shorthand', { shorthand });
    return response.data;
  }

  async checkInteractions(medicationData: any) {
    const response = await this.client.post('/prescriptions/check-interactions', medicationData);
    return response.data;
  }

  async createPrescription(prescriptionData: any) {
    const response = await this.client.post('/prescriptions/draft', prescriptionData);
    return response.data;
  }

  async signPrescription(prescriptionId: string) {
    const response = await this.client.post(`/prescriptions/${prescriptionId}/sign`);
    return response.data;
  }

  // Clinical
  async getHealthTimeline(patientId: string, params?: any) {
    const response = await this.client.get(`/clinical/health-graph/${patientId}`, { params });
    return response.data;
  }

  // ABDM
  async requestConsent(consentData: any) {
    const response = await this.client.post('/abdm/consent-requests/init', consentData);
    return response.data;
  }
}

export const api = new ApiClient();
export default api;
