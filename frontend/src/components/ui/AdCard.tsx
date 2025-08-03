'use client';

import { AdDetails } from '@/types/api';
import { formatPrice, formatMileage, formatLocation, formatYear, cn } from '@/lib/utils';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDollarSign, faMapMarkerAlt, faCalendarAlt, faTachometerAlt, faExternalLinkAlt } from '@fortawesome/free-solid-svg-icons';
import '@/lib/fontawesome';

interface AdCardProps {
  ad: AdDetails;
  className?: string;
}

export default function AdCard({ ad, className }: AdCardProps) {
  const isValidData = (value: string) => value !== 'Not Found' && value.trim() !== '';

  return (
    <div className={cn(
      'group bg-white rounded-xl border border-gray-200 hover:border-indigo-300 hover:shadow-lg transition-all duration-200 overflow-hidden',
      className
    )}>
      <div className="p-6">
        {/* Title */}
        <h3 className="font-semibold text-gray-900 text-lg mb-4 line-clamp-2 group-hover:text-indigo-600 transition-colors">
          {ad.title}
        </h3>

        {/* Details Grid */}
        <div className="space-y-3 mb-6">
          {/* Price */}
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <FontAwesomeIcon icon={faDollarSign} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Price</p>
              <p className="font-semibold text-gray-900">
                {isValidData(ad.price) ? formatPrice(ad.price) : 'Price not available'}
              </p>
            </div>
          </div>

          {/* Location */}
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <FontAwesomeIcon icon={faMapMarkerAlt} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Location</p>
              <p className="font-medium text-gray-700">
                {isValidData(ad.location) ? formatLocation(ad.location) : 'Location not available'}
              </p>
            </div>
          </div>

          {/* Year and Mileage */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <FontAwesomeIcon icon={faCalendarAlt} className="text-gray-400" />
              <div>
                <p className="text-xs text-gray-500">Year</p>
                <p className="font-medium text-gray-700 text-sm">
                  {isValidData(ad.year) ? formatYear(ad.year) : 'N/A'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <FontAwesomeIcon icon={faTachometerAlt} className="text-gray-400" />
              <div>
                <p className="text-xs text-gray-500">Mileage</p>
                <p className="font-medium text-gray-700 text-sm">
                  {isValidData(ad.mileage) ? formatMileage(ad.mileage) : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* View Ad Link */}
        <a
          href={ad.link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center w-full px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors duration-200 group/link"
        >
          <span>View Full Details</span>
          <FontAwesomeIcon icon={faExternalLinkAlt} className="ml-2 group-hover/link:translate-x-0.5 transition-transform" />
        </a>
      </div>
    </div>
  );
}
