// TypeScript interfaces based on backend ER documentation

export interface VehicleAnalysisRequest {
  vehicle1: string;  // Required, non-empty
  vehicle2: string;  // Required, non-empty
}

export interface AdDetails {
  id?: number;           // Auto-generated (database only)
  title: string;         // Ad headline
  price: string;         // Format: "LKR 6,500,000" or "Not Found"
  location: string;      // City/area in Sri Lanka
  mileage: string;       // Format: "45,000 km" or "Not Found"
  year: string;          // Manufacturing year or "Not Found"
  link: string;          // Full URL to original ad
}

export interface VehicleAnalysisResponse {
  comparison_report: string;        // Markdown-formatted report
  vehicle1_ads: AdDetails[];       // Array of ads for first vehicle
  vehicle2_ads: AdDetails[];       // Array of ads for second vehicle
}

export interface VehicleAdsStatsRequest {
  ads: AdDetails[];
  min_price?: number;
  max_price?: number;
  year?: number;
  location?: string;
}

export interface VehicleAdsStatsResponse {
  ads: AdDetails[];      // Filtered ads
  stats: {
    count: number;
    min_price: number | null;
    max_price: number | null;
    avg_price: number | null;
  };
}

export interface ApiError {
  detail: string;
}

// Vehicle categories for autocomplete suggestions
export const VEHICLE_SUGGESTIONS = {
  'Popular Japanese Models': ['Toyota Aqua', 'Honda Fit', 'Suzuki Alto', 'Nissan March'],
  'Hybrid Vehicles': ['Toyota Prius', 'Honda Vezel', 'Toyota CH-R'],
  'Luxury Vehicles': ['BMW 320i', 'Mercedes C200', 'Audi A4'],
  'SUVs': ['Toyota Fortuner', 'Mitsubishi Pajero', 'Honda CR-V'],
  'Budget Cars': ['Perodua Axia', 'Suzuki Wagon R', 'Daihatsu Mira'],
  'Commercial Vehicles': ['Toyota Hiace', 'Nissan Caravan', 'Isuzu D-Max']
};

export const ALL_VEHICLES = Object.values(VEHICLE_SUGGESTIONS).flat();
