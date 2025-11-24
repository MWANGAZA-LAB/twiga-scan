// API service for backend communication

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export interface ScanRequest {
  content: string;
  device_id?: string;
  ip_address?: string;
}

export interface ScanResponse {
  scan_id: string;
  timestamp: string;
  content_type: string;
  parsed_data: any;
  provider: boolean;
  auth_status: string;
  warnings: string[];
  verification_results: any;
  user_action?: string;
  outcome?: string;
  // Duplicate detection fields
  is_duplicate?: boolean;
  usage_count?: number;
  first_seen?: string;
}

export interface ScanHistoryResponse {
  scans: Array<{
    scan_id: string;
    timestamp: string;
    content_type: string;
    auth_status: string;
    user_action?: string;
    outcome?: string;
  }>;
  total: number;
  limit: number;
  offset: number;
}

export interface Provider {
  id: number;
  name: string;
  domain?: string;
  provider_type: string;
  status: string;
  is_active: boolean;
  created_at?: string;
}

export interface ProviderResponse {
  providers: Provider[];
  total: number;
  limit: number;
  offset: number;
}

export interface ScanActionRequest {
  action: string;
  outcome?: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('API request failed:', error);
      }
      throw error;
    }
  }

  // Scan endpoints
  async scanContent(data: ScanRequest): Promise<ScanResponse> {
    return this.request<ScanResponse>('/scan/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getScanHistory(limit = 10, offset = 0): Promise<ScanHistoryResponse> {
    return this.request<ScanHistoryResponse>(`/scan/?limit=${limit}&offset=${offset}`);
  }

  async getScanResult(scanId: string): Promise<ScanResponse> {
    return this.request<ScanResponse>(`/scan/${scanId}`);
  }

  async updateScanAction(scanId: string, action: ScanActionRequest): Promise<any> {
    return this.request(`/scan/${scanId}/action`, {
      method: 'PUT',
      body: JSON.stringify(action),
    });
  }

  // Provider endpoints
  async getProviders(limit = 50, offset = 0): Promise<ProviderResponse> {
    return this.request<ProviderResponse>(`/providers/?limit=${limit}&offset=${offset}`);
  }

  async getProvider(providerId: number): Promise<Provider> {
    return this.request<Provider>(`/providers/${providerId}`);
  }

  async createProvider(providerData: Partial<Provider>): Promise<any> {
    return this.request('/providers/', {
      method: 'POST',
      body: JSON.stringify(providerData),
    });
  }

  async updateProvider(providerId: number, providerData: Partial<Provider>): Promise<any> {
    return this.request(`/providers/${providerId}`, {
      method: 'PUT',
      body: JSON.stringify(providerData),
    });
  }

  async deleteProvider(providerId: number): Promise<any> {
    return this.request(`/providers/${providerId}`, {
      method: 'DELETE',
    });
  }

  async getProviderTypes(): Promise<{ provider_types: string[]; suggested_types: string[] }> {
    return this.request('/providers/types/list');
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: number; service: string }> {
    return this.request('/health');
  }
}

export const apiService = new ApiService(); 