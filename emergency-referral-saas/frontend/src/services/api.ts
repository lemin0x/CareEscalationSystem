const API_BASE_URL = '/api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'nurse' | 'doctor';
  health_center_id: number | null;
}

export interface PatientCreate {
  first_name: string;
  last_name: string;
  age: number;
  gender: 'M' | 'F' | 'Other';
  national_id?: string;
  phone?: string;
  address?: string;
  health_center_id: number;
  oxygen_saturation?: number;
  heart_rate?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  temperature?: number;
  chest_pain: boolean;
  chief_complaint?: string;
  notes?: string;
}

export interface PatientResponse {
  id: number;
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  national_id?: string;
  phone?: string;
  address?: string;
  oxygen_saturation?: number;
  heart_rate?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  temperature?: number;
  chest_pain: boolean;
  triage_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  chief_complaint?: string;
  notes?: string;
  health_center_id: number;
  registered_by: number;
  created_at: string;
}

export interface ReferralResponse {
  id: number;
  patient_id: number;
  from_center_id: number;
  to_center_id: number;
  status: 'CREATED' | 'SENT' | 'ACCEPTED' | 'TRANSFERRED';
  priority: string;
  reason?: string;
  clinical_notes?: string;
  created_at: string;
  sent_at?: string;
  accepted_at?: string;
  transferred_at?: string;
  created_by: number;
  accepted_by?: number;
}

export interface ReferralCreate {
  patient_id: number;
  to_center_id: number;
  reason?: string;
  clinical_notes?: string;
}

export interface HealthCenter {
  id: number;
  name: string;
  center_type: string;
  address?: string;
  city?: string;
  phone?: string;
}

class ApiService {
  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Invalid credentials' }));
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async createPatient(patientData: PatientCreate): Promise<PatientResponse> {
    return this.request<PatientResponse>('/patients', {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
  }

  async getPatients(): Promise<PatientResponse[]> {
    return this.request<PatientResponse[]>('/patients');
  }

  async getReferrals(statusFilter?: string): Promise<ReferralResponse[]> {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return this.request<ReferralResponse[]>(`/referrals${query}`);
  }

  async createReferral(referralData: ReferralCreate): Promise<ReferralResponse> {
    return this.request<ReferralResponse>('/referrals', {
      method: 'POST',
      body: JSON.stringify(referralData),
    });
  }

  async acceptReferral(referralId: number): Promise<ReferralResponse> {
    return this.request<ReferralResponse>(`/referrals/${referralId}/accept`, {
      method: 'POST',
    });
  }

  async getHealthCenters(): Promise<HealthCenter[]> {
    return this.request<HealthCenter[]>('/health-centers');
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }
}

export const apiService = new ApiService();

