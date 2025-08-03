import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format price for display
export function formatPrice(price: string): string {
  if (price === 'Not Found' || !price) {
    return 'Price not available';
  }
  
  // Remove any existing formatting and extract numbers
  const cleanPrice = price.replace(/[^\d]/g, '');
  if (!cleanPrice) {
    return price; // Return original if no numbers found
  }
  
  // Convert to number and format with commas
  const numPrice = parseInt(cleanPrice);
  return `LKR ${numPrice.toLocaleString()}`;
}

// Format mileage for display
export function formatMileage(mileage: string): string {
  if (mileage === 'Not Found' || !mileage) {
    return 'Mileage not available';
  }
  
  return mileage;
}

// Format location for display
export function formatLocation(location: string): string {
  if (location === 'Not Found' || !location) {
    return 'Location not available';
  }
  
  return location;
}

// Format year for display
export function formatYear(year: string): string {
  if (year === 'Not Found' || !year) {
    return 'Year not available';
  }
  
  return year;
}

// Check if a year is within reasonable range
export function isValidYear(year: string): boolean {
  const currentYear = new Date().getFullYear();
  const yearNum = parseInt(year);
  return yearNum >= 1990 && yearNum <= currentYear;
}

// Extract numeric value from price string for calculations
export function extractNumericPrice(price: string): number | null {
  const cleanPrice = price.replace(/[^\d]/g, '');
  const numPrice = parseInt(cleanPrice);
  return isNaN(numPrice) ? null : numPrice;
}

// Debounce function for search inputs
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

// Generate loading messages for different stages
export function getLoadingMessage(stage: 'analyzing' | 'finding-ads' | 'extracting-details' | 'processing'): string {
  const messages = {
    'analyzing': 'AI agents are analyzing vehicle specifications...',
    'finding-ads': 'Searching for advertisements on Sri Lankan websites...',
    'extracting-details': 'Extracting detailed information from ads...',
    'processing': 'Processing your request...'
  };
  
  return messages[stage];
}
