import { VehicleAnalysisRequest, VehicleAnalysisResponse, ApiError } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export class ApiClient {
  private static async request<T>(
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
        const errorData: ApiError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(errorData.detail || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  static async analyzeVehicles(
    request: VehicleAnalysisRequest
  ): Promise<VehicleAnalysisResponse> {
    return this.request<VehicleAnalysisResponse>('/api/v1/analyze-vehicles', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async healthCheck(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/');
  }
}

// Validation functions
export const validateVehicleInput = (vehicle: string): string | null => {
  if (!vehicle.trim()) {
    return 'Vehicle name is required';
  }
  if (vehicle.length < 2) {
    return 'Vehicle name must be at least 2 characters';
  }
  if (vehicle.length > 100) {
    return 'Vehicle name must be less than 100 characters';
  }
  return null;
};

export const validateVehicleAnalysisRequest = (
  request: VehicleAnalysisRequest
): string[] => {
  const errors: string[] = [];
  
  const vehicle1Error = validateVehicleInput(request.vehicle1);
  if (vehicle1Error) {
    errors.push(`Vehicle 1: ${vehicle1Error}`);
  }
  
  const vehicle2Error = validateVehicleInput(request.vehicle2);
  if (vehicle2Error) {
    errors.push(`Vehicle 2: ${vehicle2Error}`);
  }
  
  return errors;
};
